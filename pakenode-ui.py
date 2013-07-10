#!/usr/bin/env python3


"""This is interface to Pake node (the `~/.pakenode` directory).

It provides methods for:

*   (re)initializing the node,
*   uploading it to server,
*   editing `*.json` config files,
*   registering new Pake repositories,
*   and possibly more.

Syntax is simple:

    python3 pakenode-ui.py [global options] [MODE [mode options]]

--------


pakenode-ui options vary depending on mode used. Below there is a listing of available 
modes and their options.


Global options:
    -h, --help          - display this message
    -v, --version       - display version information
        --component STR - choose component (ui, backend) which version should be displayed (only with --version)
    -V, --verbose       - print more messages, conflicts with: --quiet
    -Q, --quiet         - print less messages, conflicts with: --verbose
    -R, --root          - specify alternative root directory for initialization (default: ~);

**Warning:** use --root option only for testing!

Mode options:

init:
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

----

meta:
This mode is used for editing `meta.json` config file which is the most important file in 
your node. Without it being properly set up your node is considered `dead` to the rest of 
the network.

    -s, --set           - sets a key with given name (requires two arguments)
    -r, --remove KEY    - removes a key from meta.json
    -g, --get KEY       - prints value of given KEY, if KEY is not found returs empty string
    -m, --missing       - prints key missing in meta.json
    -l, --list          - prints comma separated list of keys in meta.json

----

mirrors:
This mode is used to manipulate `mirrors.json` file of the node.

These option define what to do. They conflict with each other. 

        --add           - add new mirror
        --edit          - edit a mirror, URL defines what mirror is edited
        --remove        - removes mirror which has given URL

All options in this mode (except --remove) are accompanied by these ones. Again, 
there is one exception: --edit may be accompanied by only one of them depending on
what you want to edit.

    -u, --url STR       - url from which other users fetch data
    -p, --push-url STR  - url which is used to connect to node server
    -c, --cwd STR       - directory to which pake should go after connecting to server

----

push:
This mode is not yet implemented.

----

packages:
This mode is not yet implemented.

----

nodes:
This mode is not yet implemented.

----


This script is published under GNU GPL v3 or any later version of this license. 
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import os
import shutil
import sys

import clap
import pake


#   this is version of the interface code
#   to get version of the pake backend use
#
#   >>> import pake
#   >>> pake.__version__
#
__version__ = '0.0.7'

formater = clap.formater.Formater(sys.argv[1:])
formater.format()

init = clap.parser.Parser()
init.add(short='r', long='re')
init.add(short='d', long='dry')
init.add(short='p', long='preserve', requires=['--re'])

meta = clap.parser.Parser()
meta.add(short='s', long='set', conflicts=['-r', '-g', '-m', '-l'])
meta.add(short='r', long='remove', argument=str, conflicts=['-s', '-g', '-m', '-l'])
meta.add(short='g', long='get', argument=str, conflicts=['-s', '-r', '-m', '-l'])
meta.add(short='m', long='missing', conflicts=['-s', '-r', '-g'])
meta.add(short='l', long='list', conflicts=['-s', '-r', '-g'])

mirrors = clap.parser.Parser()
mirrors.add(long='main', needs=['--add', '--edit', '--remove'])
mirrors.add(long='add', requires=['-u', '-p', '-c'], conflicts=['--main', '--edit', '--remove'])
mirrors.add(long='edit', argument=str, needs=['--url', '--push-url', '--cwd'], conflicts=['--main', '--add', '--remove'])
mirrors.add(long='remove', argument=str, requires=['--url'], conflicts=['--main', '--add', '--edit'])
mirrors.add(short='u', long='url', argument=str)
mirrors.add(short='p', long='push-url', argument=str)
mirrors.add(short='c', long='cwd', argument=str)

push = clap.parser.Parser()

options = clap.modes.Modes(list(formater))
options.addMode('init', init)
options.addMode('meta', meta)
options.addMode('mirrors', mirrors)
options.addOption(short='h', long='help')
options.addOption(short='v', long='version')
options.addOption(short='C', long='component', argument=str, requires=['--version'])
options.addOption(short='V', long='verbose', conflicts=['--quiet'])
options.addOption(short='Q', long='quiet', conflicts=['--verbose'])
options.addOption(short='R', long='root', argument=str)


try:
    options.define()
    options.check()
    message = ''
except clap.errors.UnrecognizedModeError as e: 
    message = 'unrecognized mode: {0}'.format(e)
except clap.errors.UnrecognizedOptionError as e:
    message = 'unrecognized option found: {0}'.format(e)
except clap.errors.RequiredOptionNotFoundError as e:
    message = 'required option not found: {0}'.format(e)
except clap.errors.MissingArgumentError as e:
    message = 'missing argument for option: {0}'.format(e)
except clap.errors.InvalidArgumentTypeError as e:
    message = 'invalid argument for option: {0}'.format(e)
except clap.errors.ConflictingOptionsError as e:
    message = 'conflicting options: {0}'.format(e)
finally:
    if message:
        print('pakenode: fatal: {0}'.format(message))
        exit(1)
    else:
        options.parse()


#### Actual program logic begins here

def getmodehelp(mode):
    """Returns help just for given mode.
    """
    begin_global = 'Global options:'
    end_global = '**Warning:** use --root option only for testing!'
    begin_global = __doc__.index(begin_global)
    end_global = __doc__.index(end_global)+len(end_global)
    ghelp = __doc__[begin_global:end_global].strip()

    begin_mode = __doc__.index('{}:'.format(mode))+len(mode)+2
    end_mode = __doc__[begin_mode:].index('----')+begin_mode
    mhelp = __doc__[begin_mode:end_mode].rstrip()

    credit = 'This script is published under GNU GPL'
    credit = __doc__.index(credit)
    credit = __doc__[credit:]

    string = 'Help for mode \'{0}\''.format(mode) + '\n\n' + ghelp + '\n\n' + mhelp + '\n\n' + credit
    return string.rstrip()

if '--version' in options:
    version = 'pake {0}'.format(pake.__version__)
    if '--verbose' in options:
        version += ' (ui: {0})'.format(__version__)
    if '--component' in options:
        component = options.get('--component')
        if component == 'backend': version = pake.__version__
        elif component == 'ui': version = __version__
        elif component == 'clap': version = clap.__version__
        else:
            print('pakenode: fail: no such component: {0}'.format(component))
            version = ''
    if version: print(version)
    exit()

if '--help' in options:
    mode = str(options)
    if mode: string = getmodehelp(mode)
    else: string = __doc__
    print(string)
    exit()


root = os.path.expanduser('~')
if '--root' in options: root = options.get('--root')
root = os.path.join(root, '.pakenode')
if '--verbose' in options: print('pakenode: root set to {0}'.format(root))


message = ''
if str(options) == 'init':
    if '--dry' in options: print('pakenode: performing dry run')
    reinit = ''
    try:
        if '--dry' in options:
            if os.path.isdir(root): raise FileExistsError(root)
            else:
                pake.node.makedirs(root)
                shutil.rmtree(root)
        else:
            pake.node.makedirs(root)
        success = True
    except FileExistsError:
        if '--re' in options:
            if '--preserve' in options:
                meta = pake.node.Meta(root)
                mirrors = pake.node.Mirrors(root)
                nodes = pake.node.Nodes(root)
                pushers = pake.node.Pushers(root)
                node_pusher = pake.node.NodePusher(root)
                packages = pake.node.Packages(root)
                installed = pake.node.Installed(root)
            if '--dry' not in options:
                shutil.rmtree(root)
                pake.node.makedirs(root)
            if '--verbose' in options: print('pakenode: removed old node repository')
            reinit = 're'
            success = True
        else:
            if '--verbose' in options: print('pakenode: fail: node repository found in {0}'.format(root))
            success = False
    except Exception as e:
        if '--verbose' in options: print('pakenode: fail: {0}'.format(e))
        success = False
    finally:
        if success and '--dry' not in options:
            if '--preserve' in options:
                meta.write()
                mirrors.write()
                nodes.write()
                pushers.write()
                node_pusher.write()
                packages.write()
                installed.write()
            else:
                pake.node.makeconfig(root)
    if success: message = 'pakenode: {0}initialized node in {1}'.format(reinit, root)
    else: message = 'pakenode: fatal: cannot initialize repository in {0}'.format(root)
elif str(options) == 'meta':
    if '--set' in options:
        try:
            k = options.arguments[0]
            v = options.arguments[1]
            pake.node.Meta(root).set(key=k, value=v)
            success = True
        except IndexError as e:
            print('pakenode: fail: two arguments are required')
            success = False
        except Exception as e:
            if '--verbose' in options: print('pakenode: fail: {0}'.format(e))
            success = False
        finally:
            if success:
                message = 'pakenode: meta.json: key stored'
                if '--verbose' in options: message += ': {0} = {1}'.format(k, v)
            else:
                message = 'pakenode: fatal: meta.json: key was not stored'
    elif '--remove' in options:
        pake.node.Meta(root).remove(options.get('--remove'))
        if '--verbose' in options: message = 'pakenode: meta.json: key removed'
    elif '--get' in options:
        try:
            value = pake.node.Meta(root).get(options.get('--get'))
        except KeyError as e:
            if '--verbose' in options: print('pakenode: fatal: meta.json: key {0} not found'.format(e))
            value = ''
        finally:
            message = value
    elif '--missing' in options:
        missing = pake.node.Meta(root).missing()
        message = ', '.join(missing)
    elif '--list' in options:
        meta = pake.node.Meta(root)
        c = sorted(list(meta.content.keys()))
        if '--verbose' in options:
            c = ['{0}: {1}'.format(k, meta[k]) for k in c]
            char = '\n'
        else: char = ', '
        message = char.join(c)
elif str(options) == 'mirrors':
    if '--add' in options:
        url = options.get('--url')
        push_url = options.get('--push-url')
        cwd = options.get('--cwd')
        message = 'pakenode: mirror added'
        if '--verbose' in options:
            message += ': {0} -> {1}{2}'.format(url, push_url, cwd))
     elif '--edit' in options:
         message = 'pakenode: fail: not implemented'
     elif '--remove' in options:
         message = 'pakenode: fail: not implemented'
elif str(options) == 'push':
    message = 'pakenode: fatal: push mode is not yet implemented'
elif str(options) == 'packages':
    message = 'pakenode: fatal: packages mode is not yet implemented'
elif str(options) == 'nodes':
    message = 'pakenode: fatal: nodes mode is not yet implemented'

if message: print(message)