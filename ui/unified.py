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
    -l, --list-keys         - list keys in meta.json (if --verbose list format is KEY:VALUE\\n)
    -p, --pretty            - format JSON in a pretty way

push:
    Mode used to push contents of the local node to mirrors.

    -m, --main              - push to main mirror (== --only $(pakenode meta -g url))
    -M, --mirrors           - push to all mirrors except main
    -o, --only URL          - push only to this mirror
    -C, --create-fallback   - create fallback files on the mirrors


----

This program is part of the PAKE toolset and is published under GNU GPL v3+ license.
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import getpass
import os
import sys

import clap
import pake


uifile = pake.shared.getuipath('unified')
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

if not root and str(ui) != 'node': exit('pake: fatal: no root found')

if str(ui) == 'node':
    # we're going one mode down in the tree
    ui = ui.parser
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
        if '--pretty' in ui:
            #   this should be routine and independent from
            #   every other options to always enable the possibility
            #   to format JSON in pretty way
            pake.config.node.Meta(root).write(pretty=True)
    else:
        if '--debug' in ui: print('pake: fail: mode `{0}` is implemented yet'.format(str(ui)))
