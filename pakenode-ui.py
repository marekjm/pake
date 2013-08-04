#!/usr/bin/env python3


"""This is the interface to PAKE node (the `~/.pakenode` directory).

Currently, it provides methods for:

    *   (re)initializing the node,
    *   uploading it to server,
    *   editing `*.json` config files,
    *   registering new PAKE repositories,

@help.begin_global
Syntax:

    pakenode [global options] [MODE [mode options]]

Global options:
    -h, --help          - display this message
    -v, --version       - display version information
        --component STR - choose component (ui, backend) which version should be displayed (only with --version)
    -V, --verbose       - print more messages, conflicts with: --quiet
        --debug         - show debug messages
    -Q, --quiet         - print less messages, conflicts with: --verbose (it doesn't really do anything yet)
    -R, --root          - specify alternative root directory for initialization (default: ~);

**Warning:** use --root option only for testing!

@help.end_global

Mode options:

init:
@help.begin_mode=init
This mode is used for initializing a node repository in user's home directory.
If you want to just check if you can initialize option --dry is for you.
By default, if you are trying to reinitialize pake will exit with error message saying
that you cannot because old repository is found.
This is to prevent you from accidentally overwriting your repository as a reinitialization
process is dumb and just removes the node and creates a fresh one.


    -d, --dry           - do a "dry run", just check if init would be successful
    -r, --re            - tell pakenode you are reinitializing and it should remove old node
                          directory if found, otherwise an exception will be raised
    -p, --preserve      - preserves config files during reinitialization

@help.end_mode=init
----

meta:
@help.begin_mode=meta
This mode is used for editing `meta.json` config file which is the most important file in
your node. Without it being properly set up your node is considered `dead` to the rest of
the network.

    -s, --set           - sets a key with given name (requires two arguments)
    -r, --remove KEY    - removes a key from meta.json
    -g, --get KEY       - prints value of given KEY, if KEY is not found returs empty string
    -m, --missing       - prints key missing in meta.json
    -l, --list          - prints comma separated list of keys in meta.json
    -p, --pretty        - enable pretty formating of `meta.json` file
        --reset FILE    - resets given config file (use with caution!)

@help.end_mode=meta
----

mirrors:
@help.begin_mode=mirrors
This mode is used to manipulate `mirrors.json` file of the node.

These options define what to do. They conflict with each other.

        --add           - add new mirror
        --edit URL      - edit a mirror, URL defines what mirror is edited
        --remove URL    - removes mirror which has given URL

These options add details.

    -u, --url STR       - url from which other users fetch data
    -p, --push-url STR  - url which is used to connect to node server
    -c, --cwd STR       - directory to which pake should go after connecting to server
    -m, --main          - if this option is passed with a mirror, it will be set as main in meta.json

@help.end_mode=mirrors
----

push:
@help.begin_mode=push
This mode is used for pushing to mirrors. Before every push you will be asked for username and
password used for logging in to the remote server. By default push goes to every mirror.

    -m, --only-main     - if passed pushes only to main mirror
    -f, --fallback      - create fallback files
    -i, --installed     - push also `installed.json` file (useful for backup)
    -d, --dont-push     - don't actually push anything, useful for updating credentials
    -D, --dont-force    - if push to one node fails don't continue with the others
    -A, --ask-once      - for the same push-url PAKE will only ask once for username and password
                          (can be buggy if you have several account for the same server -- push-url)

@help.end_mode=push
----

packages:
@help.begin_mode=packages
This mode is not yet implemented.

@help.end_mode=packages
----

nodes:
@help.begin_mode=nodes
This mode lets you add nodes to your network.

    -s, --set           - add URL by hand

@help.end_mode=nodes
@help.footer
----


This script is published under GNU GPL v3 or any later version of this license.
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import getpass
import os
import shutil
import sys
import re

import clap
import pake

from pake.ui import base as ui


formater = clap.formater.Formater(sys.argv[1:])
formater.format()

init = clap.parser.Parser()
init.add(short='r', long='re')
init.add(short='d', long='dry')
init.add(short='p', long='preserve', requires=['--re'])

meta = clap.parser.Parser()
meta.add(short='s', long='set', conflicts=['-r', '-g', '-m', '-l'])
meta.add(short='r', long='remove', arguments=[str], conflicts=['-s', '-g', '-m', '-l'])
meta.add(short='g', long='get', arguments=[str], conflicts=['-s', '-r', '-m', '-l'])
meta.add(short='m', long='missing', conflicts=['-s', '-r', '-g'])
meta.add(short='l', long='list', conflicts=['-s', '-r', '-g'])
meta.add(short='p', long='pretty')
meta.add(long='reset', arguments=[str])

mirrors = clap.parser.Parser()
mirrors.add(long='add', requires=['-u', '-p', '-c'], conflicts=['--edit', '--remove'])
mirrors.add(long='edit', arguments=[str], needs=['--url', '--push-url', '--cwd'], conflicts=['--add', '--remove'])
mirrors.add(long='remove', arguments=[str], conflicts=['--add', '--edit'])
mirrors.add(long='main')
mirrors.add(short='u', long='url', arguments=[str])
mirrors.add(short='p', long='push-url', arguments=[str])
mirrors.add(short='c', long='cwd', arguments=[str])

push = clap.parser.Parser()
push.add(short='m', long='only-main')
push.add(short='f', long='fallback')
push.add(short='i', long='installed')
push.add(short='d', long='dont-push')
push.add(short='D', long='dont-force')
push.add(short='A', long='ask-once')

packages = clap.parser.Parser()
packages.add(short='r', long='register', arguments=[str])
packages.add(short='d', long='delete', arguments=[str])
packages.add(short='A', long='dir-also', requires=['--delete'])
packages.add(short='u', long='update')

def url(string):
    """Returns passed string if it's valid URL.
    Raises ValueError otherwise.
    """
    url_regexp = re.compile('^([a-z]+://)?(www[0-9]*.)?([a-z0-9-]+.)+[a-z]+/(.+[^/])?$')
    if not re.match(url_regexp, string): raise ValueError(string)
    return string
nodes = clap.parser.Parser()
nodes.add(short='s', long='set', arguments=[url])
nodes.add(short='u', long='update')
nodes.add(short='l', long='list')

options = clap.modes.Parser(list(formater))
options.addMode('init', init)
options.addMode('meta', meta)
options.addMode('mirrors', mirrors)
options.addMode('push', push)
options.addMode('packages', packages)
options.addMode('nodes', nodes)
options.addOption(short='h', long='help')
options.addOption(short='v', long='version')
options.addOption(short='C', long='component', arguments=[str], requires=['--version'])
options.addOption(short='V', long='verbose', conflicts=['--quiet'])
options.addOption(short='Q', long='quiet', conflicts=['--verbose'])
options.addOption(short='R', long='root', arguments=[str])


options = ui.checkinput(options)


if '--version' in options:
    ui.printversion(options)
    exit()

if '--help' in options:
    print(ui.gethelp(__doc__, options=options))
    exit()


#### Actual program logic begins here

#   Alert messages
#
#   When we want to notify the user that something happened we can use
#   following types of alert:
#   *   fail:       normally not printed, can be enabled with --verbose option,
#   *   fatal:      normally printed, can be disabled with --quiet option,
#   *   message:    normally printed, can be disabled with --quiet option,
#
#   When you run the program and it does not accomplish the task you set for it and
#   just finish saying: `pakenode: fatal: ...` you can usually rerun the program with
#   the same options and arguments but add --verbose option on the beginning and
#   it will show you why it fatal'ed (will print you `fail` messages).
#
#   All these types print messages of specific format:
#
#   *   fail:       pakenode: fail: MESSAGE
#   *   fatal:      pakenode: fatal: MESSAGE
#   *   message:    pakenode: MESSAGE
#
#   When they are printed
#
#   `fail` alert is printed when something goes wrong during program execution and
#   we want to notify the user that something bad happened.
#   `fatal` is used when something REALY bad happend and we can't recover.
#   `message` is printed when there is a need to notify user about something.


root = os.path.expanduser('~')
if '--root' in options: root = options.get('--root')
root = os.path.join(root, '.pakenode')
if '--debug' in options: print('pakenode: root set to {0}'.format(root))

message = ''
if str(options) == 'init':
    """Logic for `init` mode.

    This mode has two reasons to be used:
    *   initialization of a new node,
    *   reinitialization of a node.
    """

    #   if we are running in --dry mode pake will actually not do anything
    if '--dry' in options and '--quiet' not in options: print('pakenode: performing dry run')

    #   this is empty, if the --re option is passed this string will adjusted later
    reinit = ''
    try:
        #   first try to create directories required by pake to create a node
        if '--dry' in options:
            #   if it's a dry run...
            if os.path.isdir(root):
                #   check if node is already there
                raise FileExistsError(root)
            else:
                pake.node.makedirs(root)
                shutil.rmtree(root)
        else:
            pake.node.makedirs(root)
        success = True
    except FileExistsError:
        if '--re' in options:
            #   if node exists and --re option was passed we're reinitializing
            if '--preserve' in options:
                #   if --preserve option was passed user wants to store his config and
                #   recreate it after reinitialization,
                #   here are all config files
                meta = pake.config.node.Meta(root)
                mirrors = pake.config.node.Mirrors(root)
                nodes = pake.config.node.Nodes(root)
                pushers = pake.config.node.Pushers(root)
                packages = pake.config.node.Packages(root)
                installed = pake.config.node.Installed(root)
                registered = pake.config.node.Registered(root)
            if '--dry' not in options:
                #   if it's not a dry run remove old tree and create brand new one
                shutil.rmtree(root)
                pake.node.makedirs(root)
            if '--verbose' in options: print('pakenode: removed old node repository')
            reinit = 're'
            success = True
        else:
            #   if --re option was not passed FileExistsError means that we shouldn't continue
            #   print message if --verbose and set success flag to False (don't do anyhting from this point)
            if '--verbose' in options: print('pakenode: fail: node repository found in {0}'.format(root))
            success = False
    except Exception as e:
        #   an unhandled exception was raised we notify the user even if not --verbose and
        #   set success flag to False
        print('pakenode: fatal: unhandled exception: {0}'.format(e))
        success = False
    finally:
        if success and '--dry' not in options:
            #   if all previous actions ended with success and this is not a dry run we
            #   want to create configuration files for the user
            if '--preserve' in options:
                #   if --preserve was passed it means that config files were read before and
                #   we should just write them now (it means that this is a reinitialization)
                meta.write()
                mirrors.write()
                nodes.write()
                pushers.write()
                packages.write()
                installed.write()
                registered.write()
            else:
                #   if no --preserve was passed then create new config files with
                #   default values
                pake.node.makeconfig(root)
    #   set final messages
    if success: message = 'pakenode: {0}initialized node in {1}'.format(reinit, root)
    else: message = 'pakenode: fatal: cannot initialize repository in {0}'.format(root)
elif str(options) == 'meta':
    """Logic for `meta` mode.
    """

    if '--set' in options:
        #   With this option user can add new key to meta or
        #   overwrite old value of some key with new one.
        try:
            #   This mode requires two non-option arguments to be passed:
            #   key and value. Example:
            #
            #       pakenode meta --set foo 'Bar Baz'
            #
            #   If two arguments were passed we set given `key` to given `value` and
            #   set success flag to True.
            k = options.arguments[0]
            v = options.arguments[1]
            pake.config.node.Meta(root).set(key=k, value=v)
            success = True
        except IndexError as e:
            #   This error means that only one or no arguments were passed.
            #   Notify the user and set success flag to False.
            if '--verbose': print('pakenode: fail: two arguments are required')
            success = False
        except Exception as e:
            #   when an unhandled exception is caught print it's message
            #   and set success flag to False
            if '--verbose': print('pakenode: fail: {0}'.format(e))
            success = False
        finally:
            if success:
                #   if everything went OK print appropriate message
                if '--verbose' in options: message = 'pakenode: meta.json: key stored'
            else:
                #   if there were any errors during execution print
                #   fatal message
                message = 'pakenode: fatal: meta.json: key was not stored'
    elif '--remove' in options:
        pake.config.node.Meta(root).remove(options.get('--remove'))
        if '--verbose' in options: message = 'pakenode: meta.json: key removed'
    elif '--get' in options:
        try:
            value = pake.config.node.Meta(root).get(options.get('--get'))
        except KeyError as e:
            if '--verbose' in options: print('pakenode: fail: meta.json: key {0} not found'.format(e))
            value = ''
        finally:
            message = value
    elif '--missing' in options:
        missing = pake.config.node.Meta(root).missing()
        message = ', '.join(missing)
    elif '--list' in options:
        meta = pake.config.node.Meta(root)
        c = sorted(list(meta.content.keys()))
        if '--verbose' in options:
            c = ['{0}: {1}'.format(k, meta[k]) for k in c]
            char = '\n'
        else: char = ', '
        message = char.join(c)
    if '--reset' in options:
        name = options.get('--reset')
        if name == 'meta.json':
            pake.config.node.Meta(root).reset()
        if name == 'mirrors.json':
            pake.config.node.Mirrors(root).reset()
        if name == 'pushers.json':
            pake.config.node.Pushers(root).reset()
        if name == 'nodes.json':
            pake.config.node.Nodes(root).reset()
    if '--pretty' in options: pake.config.node.Meta(root).write(pretty=True)
elif str(options) == 'mirrors':
    """Logic for `mirrors` mode.
    """

    if '--add' in options:
        #   adds new mirror to node's list of mirrors
        #
        #   set every needed variable
        url = options.get('--url')
        push_url = options.get('--push-url')
        cwd = options.get('--cwd')
        pushers = pake.config.node.Pushers(root)
        mirrors = pake.config.node.Mirrors(root)
        #   create pusher
        if not pushers.hasurl(url):
            pushers.add(url=url, push_url=push_url, cwd=cwd)
            success = True
        else:
            success = False
            if '--verbose' in options: print('pakenode: fail: cannot add two pushers with the same url')
        #   add mirror to list
        pake.config.node.Mirrors(root).add(url)
        #   set appropriate message
        if success:
            message = 'pakenode: mirror added'
            if '--verbose' in options: message += ': {0} -> {1}{2}'.format(url, push_url, cwd)
        else:
            message = 'pakenode: fatal: cannot add duplicate mirror'
        if '--main' in options:
            pake.config.node.Meta(root).set('url', url)
            if '--quiet' not in options: print('pakenode: main url is now: {0}'.format(url))
    elif '--edit' in options:
        message = 'pakenode: fail: not implemented'
    elif '--remove' in options:
        #   get URL which user wants to remove
        #   failure may be misleading because it may be a misspelling from
        #   the user so read messages carefully
        url = options.get('--remove')
        fail = False
        if pake.config.node.Pushers(root).remove(url) == -1:
            #   print fail alert that URL was not found in pushers
            if '--verbose' in options: print('pakenode: fail: {0} not found in pushers'.format(url))
            fail = True
        if pake.config.node.Mirrors(root).remove(url) == -1:
            #   print fail alert that URL was not found in mirrors
            if '--verbose' in options: print('pakenode: fail: {0} not found in mirrors'.format(url))
            fail = True
        #   set appropriate message
        if fail: message = 'pakenode: fatal: errors occured during execution'
        else: message = 'pakenode: mirror removed'
        if '--verbose' in options: message += ': {0}'.format(url)
elif str(options) == 'push':
    """Logic for `push` mode.
    """
    def getcredentials(url):
        """Returns two-tuple (username, password) for given URL.
        """
        username = input('Username for {0}: '.format(url))
        prompt = 'Password for {0}@{1}: '.format(username, pake.config.node.Pushers(root).get(url)['push-url'])
        password = getpass.getpass(prompt)
        return (username, password)

    main = pake.config.node.Meta(root).get('url')
    if '--only-main' in options:
        #   this means that we will push only to main mirror
        if main != '': urls = [main]
        else:
            #   this means that no main url is set in meta.json
            #   user should check his/hers meta.json
            #   print appropriate message
            if '--verbose' in options: print('pakenode: fail: no url set for main mirror: check your meta.json file')
            message = 'pakenode: fatal: push could not be initialized'
            urls = []
    else:
        #   this means that we are pushing to all mirrors (default)
        urls = list(pake.config.node.Mirrors(root))
    pushers = pake.config.node.Pushers(root)
    credentials = {}
    for url in urls:
        try:
            pusher = pushers.get(url)['push-url']
            if '--ask-once' in options and pusher in credentials: username, password = credentials[pusher]
            else: username, password = getcredentials(url)
            if '--ask-once' in options: credentials[pusher] = (username, password)
            installed = '--installed' in options
            fallback = '--fallback' in options
            if '--verbose' in options:
                alert = 'pake: pushing to node: {0}'.format(url)
                if url == main: alert += '\t(main mirror)'
                print(alert)
                if installed: print('pake: pushing also `installed.json` data')
                if fallback: print('pake: creating fallback files on server')
            pake.node.pushurl(root=root, url=url, username=username, password=password, installed=installed, fallback=fallback)
        except (KeyboardInterrupt, EOFError): print()
        except Exception as e: print('pakenode: fail: push failed: {0}'.format(e))
        finally:
            if '--dont-force' in options:
                break
            else:
                pass
elif str(options) == 'packages':
    """Logic for `packages` mode.
    """
    if '--register' in options:
        pake.node.registerrepo(options.get('--register'))
    if '--delete' in options:
        pake.node.removerepo(options.get('--delete'), directory=('--dir-also' in options))
    if '--update' in options:
        print('pake: node: this is not yet implemented')
        pake.node.updaterepo()
elif str(options) == 'nodes':
    """Logic for `nodes` mode.
    """
    if '--set' in options:
        pake.node.setnode(root, options.get('--set'))
    if '--update' in options:
        for url in pake.config.node.Nodes(root): pake.node.setnode(root, url)
    if '--list' in options:
        nodes = pake.config.node.Nodes(root)
        if '--verbose' not in options: print(', '.join([url for url in nodes]))
        else:
            for url in nodes:
                print('{0}: {1}'.format(url, ', '.join(nodes.getmirrors(url))))
            

if message and '--quiet' not in options: print(message)
