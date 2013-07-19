#!/usr/bin/env python3


"""This is the interface to PAKE node (the `~/.pakenode` directory).

Currently, it provides methods for:

    *   (re)initializing the node,
    *   uploading it to server,
    *   editing `*.json` config files,
    *   registering new PAKE repositories,

Syntax:

    pakenode [global options] [MODE [mode options]]


Global options:
    -h, --help          - display this message
    -v, --version       - display version information
        --component STR - choose component (ui, backend) which version should be displayed (only with --version)
    -V, --verbose       - print more messages, conflicts with: --quiet
    -Q, --quiet         - print less messages, conflicts with: --verbose (doesn't really do anything)
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

These options define what to do. They conflict with each other. 

        --add           - add new mirror
        --edit URL      - edit a mirror, URL defines what mirror is edited
        --remove URL    - removes mirror which has given URL

These options add details.

    -u, --url STR       - url from which other users fetch data
    -p, --push-url STR  - url which is used to connect to node server
    -c, --cwd STR       - directory to which pake should go after connecting to server
    -m, --main          - if this option is passed with a mirror, it will be set as main in meta.json

----

push:

This mode is used for pushing to mirrors. Before every push you will be asked for username and 
password used for logging in to the remote server. By default push goes to every mirror.

    -m, --only-main     - if passed pushes only to main mirror
    -f, --fallback      - create fallback files
    -d, --dont-push     - don't actually push anything, useful for updating credentials
    -D, --dont-force    - if push to one node fails don't continue with the others

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


import getpass
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
__version__ = '0.0.9'

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
mirrors.add(long='add', requires=['-u', '-p', '-c'], conflicts=['--edit', '--remove'])
mirrors.add(long='edit', argument=str, needs=['--url', '--push-url', '--cwd'], conflicts=['--add', '--remove'])
mirrors.add(long='remove', argument=str, conflicts=['--add', '--edit'])
mirrors.add(long='main')
mirrors.add(short='u', long='url', argument=str)
mirrors.add(short='p', long='push-url', argument=str)
mirrors.add(short='c', long='cwd', argument=str)

push = clap.parser.Parser()
push.add(short='m', long='only-main')
push.add(short='f', long='fallback')
push.add(short='d', long='dont-push')
push.add(short='D', long='dont-force')

options = clap.modes.Parser(list(formater))
options.addMode('init', init)
options.addMode('meta', meta)
options.addMode('mirrors', mirrors)
options.addMode('push', push)
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
    """Prints version information.

    By default it's version of pake backend but user can
    specify component which version he/she wants to print.

    Components are only libraries not found in standard Python 3
    library. Currently valid --component arguments are:
    *   backend:    backend version,
    *   ui:         version of UI,
    *   clap:       version of CLAP library (used to build user interface),
    """
    version = 'pakenode {0}'.format(__version__)
    if '--verbose' in options:
        #   if --verbose if passed print also backend version
        version += ' (pake backend: {0})'.format(pake.__version__)
    if '--component' in options:
        #   if --component is passed print specified component's version
        component = options.get('--component')
        if component == 'backend': version = pake.__version__
        elif component == 'ui': version = __version__
        elif component == 'clap': version = clap.__version__
        else:
            print('pake: fatal: no such component: {0}'.format(component))
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
                #   check if file is there
                raise FileExistsError(root)
            else:
                pake.node.makedirs(root)
                shutil.rmtree(root)
        else:
            pake.node.makedirs(root)
        success = True
    except FileExistsError:
        if '--re' in options:
            #   if file exists and --re option was passed we're reinitializing
            if '--preserve' in options:
                #   if --preserve option was passed user wants to store his config and
                #   recreate it after reinitialization,
                #   here are all config files
                meta = pake.node.Meta(root)
                mirrors = pake.node.Mirrors(root)
                nodes = pake.node.Nodes(root)
                pushers = pake.node.Pushers(root)
                packages = pake.node.Packages(root)
                installed = pake.node.Installed(root)
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
                node_pusher.write()
                packages.write()
                installed.write()
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
            pake.node.Meta(root).set(key=k, value=v)
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
    """Logic for `mirrors` mode.
    """

    if '--add' in options:
        #   adds new mirror to node's list of mirrors
        #
        #   set every needed variable
        url = options.get('--url')
        push_url = options.get('--push-url')
        cwd = options.get('--cwd')
        pushers = pake.node.Pushers(root)
        mirrors = pake.node.Mirrors(root)
        #   create pusher
        if not pushers.hasurl(url):
            pushers.add(url=url, push_url=push_url, cwd=cwd)
            success = True
        else:
            success = False
            if '--verbose' in options: print('pakenode: fail: cannot add two pushers with the same url')
        #   add mirror to list
        pake.node.Mirrors(root).add(url)
        #   set appropriate message
        if success:
            message = 'pakenode: mirror added'
            if '--verbose' in options: message += ': {0} -> {1}{2}'.format(url, push_url, cwd)
        else:
            message = 'pakenode: fatal: cannot add duplicate mirror'
        if '--main' in options:
            pake.node.Meta(root).set('url', url)
            if '--quiet' not in options: print('pakenode: main url is now: {0}'.format(url))
    elif '--edit' in options:
        message = 'pakenode: fail: not implemented'
    elif '--remove' in options:
        #   get URL which user wants to remove
        #   failure may be misleading because it may be a misspelling from
        #   the user so read messages carefully
        url = options.get('--remove')
        fail = False
        if pake.node.Pushers(root).remove(url) == -1:
            #   print fail alert that URL was not found in pushers
            if '--verbose' in options: print('pakenode: fail: {0} not found in pushers'.format(url))
            fail = True
        if pake.node.Mirrors(root).remove(url) == -1:
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
        password = getpass.getpass('Password for {0}@{1}: '.format(username, pake.node.Pushers(root).get(url)['push-url']))
        return (username, password)

    if '--only-main' in options:
        #   this means that we will push only to main mirror
        url = pake.node.Meta(root).get('url')
        if url != '': urls = [url]
        else:
            #   this means that no main url is set in meta.json
            #   user should check his/hers meta.json
            #   print appropriate message
            if '--verbose' in options: print('pakenode: fail: no url set for main mirror: check your meta.json file')
            message = 'pakenode: fatal: push could not be initialized'
            urls = []
    else:
        #   this means that we are pushing to all mirrors (default)
        urls = list(pake.node.Mirrors(root))
    for url in urls:
        try:
            username, password = getcredentials()
            pake.node.pushurl(root=root, url=url, username=username, password=password)
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
    message = 'pakenode: fatal: packages mode is not yet implemented'
elif str(options) == 'nodes':
    """Logic for `nodes` mode.
    """
    message = 'pakenode: fatal: nodes mode is not yet implemented'

if message and '--quiet' not in options: print(message)
