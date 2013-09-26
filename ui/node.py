#!/usr/bin/env python3


"""Interface to PAKE node.

SYNTAX:
    pakenode [global_opts...] [mode [mode_opts...] [submode [submode_opts...]...]]


GLOBAL OPTIONS:
    These options can be placed before or after mode declaration.

{0}

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
    print(__doc__.format('\n'.join(clap.helper.Helper(ui).help()[1:])))
    exit()


root = pake.shared.getnodepath()
fail = False

# this will exit the program if there is no node on which to operate
# unless the program is called in `init` mode because it means that user will be initializing the node
if not root and str(ui) != 'init': exit('pake: fatal: no root found')


# If everything went fine, which means:
#   * root was found,
#   * UI files were found,
#   * UI has been built.
#
# Execute according to user input.

if str(ui) == 'init':
    """This mode is used for initialization of local node.
    Note, that when you'll reinitialize all config JSON will
    be overwritten.
    """
    if root:
        if '--debug' in ui:
            print('pake: debug: node already exists in {0}'.format(root))
        if '--force' in ui:
            pake.node.manager.remove(root)
            message = 'pake: removed old node'
            if '--verbose' in ui: message += ' from {0}'.format(root)
            if '--quiet' not in ui: print(message)
        else:
            message = 'pake: fatal: node cannot be initialized'
            if '--verbose' in ui: message += ' in {0}'.format(root)
            if '--quiet' not in ui: print(message)
            fail = True
    if not fail:
        root = pake.shared.getnodepath(check=False)
        pake.node.manager.makedirs(root)
        pake.node.manager.makeconfig(root)
        message = 'pake: node initialized'
        if '--verbose' in ui: message += ' in {0}'.format(root)
        if '--quiet' not in ui: print(message)
elif str(ui) == 'meta':
    """Logic for meta.json manipulation.
    """
    if '--set' in ui:
        key, value = ui.get('--set')
        pake.config.node.Meta(root).set(key, value).write()
    if '--remove' in ui:
        pake.config.node.Meta(root).remove(ui.get('--remove')).write()
    if '--get' in ui:
        print(pake.config.node.Meta(root).get(ui.get('--get')))
    if '--list-keys' in ui:
        meta = pake.config.node.Meta(root)
        if '--verbose' in ui:
            for key in sorted(meta.keys()): print('{0}: {1}'.format(key, meta.get(key)))
        else:
            print(', '.join(sorted(meta.keys())))
    if '--reset' in ui:
        pake.config.node.Meta(root).reset().write()
    if '--pretty' in ui:
        #   this should be routine and independent from
        #   every other options to always enable the possibility
        #   to format JSON in pretty way
        pake.config.node.Meta(root).write(pretty=True)
elif str(ui) == 'mirrors':
    """This mode is used for management of mirrors and pushers list.

    The process of management of both mirrors and pushers should not be split because they MUST BE
    synchronized with each other.
    Otherwise you might end with mirrors not visible to outer network.
    """
    mirrors = pake.config.node.Mirrors(root)
    pushers = pake.config.node.Pushers(root)

    if '--add' in ui:
        """Code used to add mirrors and pushers which are very much alike each other.
        *Mirrors* are visible to the outside network and are just a list of URLs while
        *pushers* contain additional data:
            - host which is used for connection,
            - directory to which PAKE should go.
        """
        url = ui.get('--url')
        host = ui.get('--host')
        cwd = ui.get('--cwd')
        if url not in mirrors:
            """If URL is not in mirrors everything's fine and we can just add it to the list
            of pushers and mirrors.
            """
            mirrors.add(url).write()
            pushers.add(url=url, host=host, cwd=cwd).write()
            message = 'pake: node: added mirror'
            if '--verbose' in ui: message += ' {0} on host {1}'.format(url, host)
            if '--quiet' not in ui: print(message)
        else:
            """Otherwise fail and tell user that mirror with this URL already exists.
            """
            message = 'pake: node: fatal: mirror already exists'
            if '--verbose' in ui: message += ' {0}'.format(url)
            if '--quiet' not in ui: print(message)
    if '--remove' in ui:
        """Code used to remove mirrors and pushers.
        Mirrors and pushers are identified via URLs because they are unique - hostnames and directories may be
        the same across different mirrors.
        """
        url = ui.get('--remove')
        mirrors.remove(url).write()
        pushers.remove(url).write()
        message = 'pake: node: mirror removed'
        if '--verbose' in ui: message += ': {0}'.format(url)
        if '--quiet' not in ui: print(message)
    if '--list' in ui:
        if '--verbose' in ui:
            for m in pushers:
                print(' * {0}'.format(m['url']))
                print('   + host: {0}'.format(m['host']))
                print('   + cwd:  {0}'.format(m['cwd']))
        else:
            for m in mirrors: print(m)
elif str(ui) == 'push':
    """This mode is used to push node's contents to mirror servers on the Net.
    """
    def getcredentials(url, pushers):
        """Returns two-tuple (username, password) for given URL.
        Prompting user to enter them.
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
    if '--only-main' in ui: urls = [pake.config.node.Meta(root).get('url')]
    else: urls = [m for m in mirrors]

    for url in urls:
        # check input for invalid mirror URLs
        if url in mirrors:
            # if a URL is valid ask for credentials
            try:
                credentials.append(getcredentials(url, pushers))
            except KeyboardInterrupt:
                # append empty credentials - do not push to this mirror
                credentials.append(())
                print()
            except EOFError:
                # cancel push operation
                print()
                exit()
        else:
            # if it's not valid print error message
            print('pake: fail: no such mirror: {0}'.format(url))
            # and append empty credentials to keep indexes synced
            credentials.append(())

    for i, url in enumerate(urls):
        # enumeration is required to get index for credentials
        # they are stored in a list synced with list of URLs
        if credentials[i]:
            print('* pushing to mirror {0}:'.format(url), end='  ')
            username, password = credentials[i]
            try:
                pake.node.pusher.push(root, url, username, password)
                message = 'OK'
            except KeyboardInterrupt:
                message = 'cancelled'
            except Exception as e:
                if '--debug' in ui:
                    # if running with --debug option reraise the exception to
                    # provide stack trace and debug info
                    # No message should be set here to throw exception in the `finally` block
                    # if we would declare the message finally would kick in and silence the error
                    raise
                else:
                    # otherwise, silence the exception and just show error message
                    message = 'failed: {0}'.format(e)
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
            added = pake.aliens.manager.addalien(root, url)
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
    if '--update' in ui:
        print('not impelemented')
    if '--list' in ui:
        for url in aliens:
            print(' * {0}'.format(url))
            if '--verbose' in ui:
                amirrors = aliens.get(url)['mirrors']
                for am in amirrors: print('   + {0}'.format(am))
elif str(ui) == 'packages':
    packages = pake.config.node.Packages(root)
    registered = pake.config.node.Registered(root)
    if '--register' in ui:
        try:
            path = os.path.join(ui.get('--register'), '.pakerepo')
            if path[0] == '~': path = os.path.abspath(os.path.expanduser(path))
            pake.node.manager.packages.register(root, path)
            meta = pake.config.repository.Meta(path)
            if not os.path.isdir(path): raise pake.errors.PAKEError('repository not found in: {0}'.format(path))

            report = 'pake: registered repository'
            if '--verbose' in ui: report += ' for package: {0} (version: {1})'.format(meta.get('name'), meta.get('version'))
        except (pake.errors.PAKEError) as e:
            report = 'pake: fatal: {0}'.format(e)
        finally:
            print(report)
    if '--update' in ui:
        try:
            pake.node.manager.packages.update(root, ui.get('--update'))
        except (pake.errors.PAKEError) as e:
            print('pake: fatal: {0}'.format(e))
            fail = True
        finally:
            if '--quiet' not in ui and not fail: print('pake: metadata updated')
    if '--unregister' in ui:
        pack = ui.get('--unregister')
        if '--name' in ui: registered.remove(name=pack)
        else: registered.remove(path=pack)
    if '--list' in ui:
        for package in packages:
            p = packages.get(package)
            report = '{0} {1} {2}'.format(p['name'], p['version'], registered.get(p['name']))
            if '--verbose' in ui:
                report += ' ({0})'.format(p['license'])
                if 'description' in p: report += ': {0}'.format(p['description'])
            if package not in registered: report += ' (not registered)'
            if '--quiet' not in ui: print(report)
else:
    if '--debug' in ui: print('pake: fail: mode `{0}` is implemented yet'.format(str(ui)))
