#!/usr/bin/env python3


"""Interface to PAKE package repository.

SYNTAX:
    pakepackage [global opts...] [mode [mode opts...]]

GLOBAL OPTIONS:
    These options can be placed before or after mode declaration.

    -v, --version           - print version information and exit
    -V, --verbose           - be more verbose
    -Q, --quiet             - be less verbose


MODES:

init:
    Mode used for initalization of the package repository.

    -f, --force             - force node initialization (used for reinitializing)


meta:
    Mode used for manipulation and checking of meta.json configuration file.

    -s, --set KEY VALUE     - used to set a key in meta.json
    -r, --remove KEY        - remove key from meta.json
    -l, --list-keys         - list keys in meta.json (if --verbose list format is KEY: VALUE\\n)
    -p, --pretty            - format JSON in a pretty way
    -r, --reset             - reset meta.json to default state


deps:
    Mode used for manipulating the list of dependencies for the package.

    -s, --set NAME          - set dependency
    -r, --remove NAME       - remove dependency
    -m, --min-version STR   - set this version as minimum required
    -M, --max-version STR   - set this version as maximum allowed
    -o, --origin URL        - set URL from which the dependency can be downloaded (currently required
                              but it will become optional once I implement package searching)


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


uifile = pake.shared.getuipath('package')
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


root = pake.shared.getrepopath()
fail = False

# this will execute the program if there is no node on which to operate
# exception is when the program is called in `init` modes
# because it means that user will be initializing the node
if not root and str(ui) != 'init': exit('pake: fatal: no repository found in current directory')

if str(ui) == 'init':
    """This mode is used for initialization of local node.
    Note, that when you'll reinitialize all config JSON will
    be overwritten.
    """
    if root:
        if '--debug' in ui: print('pake: debug: repository already exists in {0}'.format(root))
        if '--force' in ui:
            pake.repository.remove(root)
            message = 'pake: removed old repository'
            if '--verbose' in ui: message += ' from {0}'.format(root)
            if '--quiet' not in ui: print(message)
        else:
            message = 'pake: fatal: repository cannot be initialized'
            if '--verbose' in ui: message += ' in {0}'.format(root)
            if '--quiet' not in ui: print(message)
            fail = True
    if not fail:
        root = pake.shared.getrepopath(check=False)
        pake.repository.makedirs(root)
        pake.repository.makeconfig(root)
        message = 'pake: repository initialized'
        if '--verbose' in ui: message += ' in {0}'.format(root)
        if '--quiet' not in ui: print(message)
elif str(ui) == 'meta':
    """Logic for meta.json manipulation.
    """
    meta = pake.config.repository.Meta(root)
    if '--set' in ui:
        key, value = ui.get('--set')
        meta.set(key, value)
    if '--remove' in ui:
        meta.remove(ui.get('--remove'))
    if '--get' in ui:
        print(meta.get(ui.get('--get')))
    if '--list-keys' in ui:
        if '--verbose' in ui:
            for key in sorted(meta.keys()): print('{0}: {1}'.format(key, meta.get(key)))
        else:
            print(', '.join(sorted(meta.keys())))
    if '--reset' in ui:
        meta.reset()
    if '--pretty' in ui:
        #   this should be routine and independent from
        #   every other options to always enable the possibility
        #   to format JSON in pretty way
        meta.write(pretty=True)
elif str(ui) == 'deps':
    dependencies = pake.config.repository.Dependencies(root)
    if '--set' in ui:
        dep = {}
        name = ui.get('--set')
        dep['origin'] = ui.get('--origin')
        if '--min-version' in ui: dep['min'] = ui.get('-m')
        if '--max-version' in ui: dep['max'] = ui.get('-M')
        dependencies.set(name=name, dependency=dep)
    if '--list' in ui:
        if '--verbose' in ui:
            for d in list(dependencies):
                dep = dependencies[d]
                report = '{0} ({1})'.format(d, dep['origin'])
        else:
            print(', '.join(list(dependencies)))
else:
    if '--debug' in ui: print('pake: fail: mode `{0}` is implemented yet'.format(str(ui)))
