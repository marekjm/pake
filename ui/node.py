#!/usr/bin/env python3


"""Interface to PAKE node.

SYNTAX:
    pakenode [global opts...] [mode [mode opts...]]

GLOBAL OPTIONS:
    These options can be placed before or after mode declaration.

    -v, --version           - print version information and exit
    -V, --verbose           - be more verbose
    -Q, --quiet             - be less verbose


MODES:

init:
    Mode used for initalization of the node

    -f, --force             - force node initialization (used for reinitializing)


meta:
    Mode used for manipulation and checking of meta.json configuration file.

    -s, --set KEY VALUE     - used to set a key in meta.json
    -r, --remove KEY        - remove key from meta.json
    -l, --list-keys         - list keys in meta.json (if --verbose list format is KEY: VALUE\\n)
    -p, --pretty            - format JSON in a pretty way
    -r, --reset             - reset meta.json to default state


mirrors:
    Mode used for manipulating `mirrors.json` and `pushers.json` files.
    `mirrors.json` file contains list of URLs pointing to the mirrors of the node and
    is downloadable from the Net.
    `pushers.json` is used by PAKE to determine how to setup FTP connection to a server.
    It contains list of dictionaries containing:
        * url   - url as set in mirrors (acts as unique ID of the pusher, cannot be duplicated),
        * host  - host with which FTP connection will be made,
        * cwd   - directory to which PAKE should go after connection to the server.

    Example (this is the pusher for my main mirror):
        * url   - 'http://pake.taistelu.com/node'
        * host  - 'taistelu.com'
        * cwd   - '/domains/taistelu.com/public_html/pake/node'

    -a, --add               - add new mirror and pusher (requires: -u, -H, and -c options),
    -u, --url STR           - set URL for the mirror,
    -H, --host STR          - set HOST for the mirror,
    -c, --cwd STR           - set CWD for the mirror,
    -r, --remove URL        - remove mirror and pusher identified by given URL (if URL is not found
                              message will be printed)


aliens:
    Mode used to add alien nodes to your network. Aliens are used for package installation and search.
    The more you have them in your network the more powerful and healthy it is.
    If you can't install a package via PAKE but you know it's available it may be an issue of not having
    author's node in your network.

    -a, --add URL           - add alien to your network (it will also download mirrors)
    -r, --remove URL        - remove alien from your network
    -u, --update            - update your list of aliens (fetch new mirrorlists)
    -p, --purge             - remove dead (returning 404 for all mirrors) nodes from your network
    -l, --list              - list all aliens (combine with --verbose to list aliens and their mirrors)
    -d, --discover          - use alien discovery feature to expand your network automatically


push:
    Mode used to push contents of the local node to mirrors.
    By default it pushes to all mirrors.

    First, you will be asked about logins and passwords to all mirrors and
    then, after credentials gathering is finished, PAKE will push to all mirrors and
    print report to the screen.
    It's designed this way because in a situation when you had many packages and
    many mirrors you would have to login and wait many times.
    This design lets you enter all credentials and then do something productive while
    your stuff is being uploaded automatically.

    -m, --main              - push to main mirror (== --only $(pakenode meta -g url))
    -o, --only URL          - push only to this mirror
    -i, --installed         - push also `installed.json` file (useful for backup)


----

This program is part of the PAKE toolset and is published under GNU GPL v3+ license.
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import getpass
import os
import sys
import urllib

import clap
import pake


uifile = pake.shared.getuipath('node')
if not uifile: exit('pake: ui: fatal: no ui file found')

formater = clap.formater.Formater(sys.argv[1:])
formater.format()

builder = clap.builder.Builder(path=uifile, argv=list(formater))
builder.build()

ui = pake.shared.checkinput(builder.get())


if '--version' in ui:
    print(pake.__version__)
    exit()

if '--help' in ui:
    print(__doc__)
    exit()


root = pake.shared.getrootpath()
fail = False

# this will execute the program if there is no node on which to operate
# exception is when the program is called in `init` modes
# because it means that user will be initializing the node
if not root and str(ui) == 'init': exit('pake: fatal: no root found')

if str(ui) == 'init':
    """This mode is used for initialization of local node.
    Note, that when you'll reinitialize all config JSON will
    be overwritten.
    """
    if root:
        if '--debug' in ui: print('pake: debug: node already exists in {0}'.format(root))
        if '--force' in ui:
            pake.node.local.remove(root)
            message = 'pake: removed old node'
            if '--verbose' in ui: message += ' from {0}'.format(root)
            if '--quiet' not in ui: print(message)
        else:
            message = 'pake: fatal: node cannot be initialized'
            if '--verbose' in ui: message += ' in {0}'.format(root)
            if '--quiet' not in ui: print(message)
            fail = True
    if not fail:
        root = pake.shared.getrootpath(check=False)
        pake.node.local.makedirs(root)
        pake.node.local.makeconfig(root)
        message = 'pake: node initialized'
        if '--verbose' in ui: message += ' in {0}'.format(root)
        if '--quiet' not in ui: print(message)
elif str(ui) == 'meta':
    """Logic for meta.json manipulation.
    """
    if '--set' in ui:
        key, value = ui.get('--set')
        pake.config.node.Meta(root).set(key, value)
    if '--remove' in ui:
        pake.config.node.Meta(root).remove(ui.get('--remove'))
    if '--get' in ui:
        print(pake.config.node.Meta(root).get(ui.get('--get')))
    if '--list-keys' in ui:
        meta = pake.config.node.Meta(root)
        if '--verbose' in ui:
            for key in sorted(meta.keys()): print('{0}: {1}'.format(key, meta.get(key)))
        else:
            print(', '.join(sorted(meta.keys())))
    if '--reset' in ui:
        pake.config.node.Meta(root).reset()
    if '--pretty' in ui:
        #   this should be routine and independent from
        #   every other options to always enable the possibility
        #   to format JSON in pretty way
        pake.config.node.Meta(root).write(pretty=True)
elif str(ui) == 'mirrors':
    """This mode is used for management of mirrors and pushers list.
    """
    mirrors = pake.config.node.Mirrors(root)
    pushers = pake.config.node.Pushers(root)
    if '--add' in ui:
        url = ui.get('--url')
        host = ui.get('--host')
        cwd = ui.get('--cwd')
        if url not in mirrors:
            mirrors.add(url)
            pushers.add(url=url, host=host, cwd=cwd)
            message = 'pake: node: added mirror'
            if '--verbose' in ui: message += ' {0} on host {1}'.format(url, host)
            if '--quiet' not in ui: print(message)
        else:
            if '--debug' in ui: print('pake: fail: mirror {0} already exists'.format(url))
            message = 'pake: node: fatal cannot add mirror'
            if '--verbose' in ui: message += ' {0}'.format(url)
            if '--quiet' not in ui: print(message)
    if '--remove' in ui:
        url = ui.get('--remove')
        mremoved = mirrors.remove(url)
        premoved = pushers.remove(url)
        if mremoved and premoved:
            message = 'pake: node: mirror removed'
            if '--verbose' in ui: message += ': {0}'.format(url)
            if '--quiet' not in ui: print(message)
        elif mremoved and not premoved and '--debug' in ui:
            print('pake: fail: pusher does not exist: {0}'.format(url))
        elif not mremoved and premoved and '--debug' in ui:
            print('pake: fail: mirror does not exist: {0}'.format(url))
        else:
            print('pake: fail: mirror was not existsent')
    if '--list' in ui:
        if '--verbose' in ui:
            for m in pushers:
                print('{0}: {1}: {2}'.format(m['url'], m['host'], m['cwd']))
        else:
            for m in mirrors:
                print(m)
elif str(ui) == 'push':
    """This mode is used to push node's contents to mirror servers on the Net.
    """
    def getcredentials(url, pushers):
        """Returns two-tuple (username, password) for given URL.
        """
        username = input('Username for {0}: '.format(url))
        prompt = 'Password for {0}@{1}: '.format(username, pushers.get(url)['host'])
        password = getpass.getpass(prompt)
        return (username, password)

    mirrors = pake.config.node.Mirrors(root)
    pushers = pake.config.node.Pushers(root)
    installed = '--installed' in ui  # whether push also installed.json file
    credentials = []
    if '--only' in ui: urls = [ui.get('--only')]
    if '--main' in ui: urls = [pake.config.node.Meta(root).get('url')]
    else: urls = [m for m in mirrors]

    for url in urls:
        if url in mirrors:
            try:
                credentials.append(getcredentials(url, pushers))
            except KeyboardInterrupt:
                credentials.append(())  # append empty credentials - do not push to this mirror
                print()
            except EOFError:
                print()
                exit()  # cancel push operation
        else:
            print('pake: fail: no such mirror: {0}'.format(url))

    for i, url in enumerate(urls):
        if credentials[i]:
            print('* pushing to mirror {0}:'.format(url), end='  ')
            username, password = credentials[i]
            try:
                pake.node.local.push(root, url, username, password, installed=installed)
                message = 'OK'
            except Exception as e:
                message = e
            finally:
                print(message)
elif str(ui) == 'aliens':
    """This mode is used for aliens.
    """
    aliens = pake.config.node.Aliens(root)
    if '--add' in ui:
        url = ui.get('--add')
        if url[-1] == '/': url = url[:-1]
        try:
            added = pake.node.local.addalien(root, url)
            message = 'pake: alien added: {0}'.format(added)
        except urllib.error.URLError as e:
            message = 'pake: fail: alien was not found: {0}'.format(e)
        finally:
            if '--quiet' not in ui: print(message)
    if '--remove' in ui:
        try:
            aliens.remove(ui.get('--remove'))
            message = 'pake: alien removed'
        except KeyError as e:
            message = 'pake: fail: alien not found: {0}'.format(e)
        finally:
            if '--quiet' not in ui: print(message)
    if '--list' in ui:
        for url in aliens:
            print('* {0}'.format(url))
            if '--verbose' in ui:
                amirrors = aliens.get(url)['mirrors']
                for am in amirrors: print('  + {0}'.format(am))
else:
    if '--debug' in ui: print('pake: fail: mode `{0}` is implemented yet'.format(str(ui)))
