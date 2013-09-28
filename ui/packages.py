#!/usr/bin/env python3


"""Interface to PAKE packages.

SYNTAX:
    pake packages [global opts...] [mode [mode opts...]]

GLOBAL OPTIONS:
    These options can be placed before or after mode declaration.

    -v, --version           - print version information and exit
    -V, --verbose           - be more verbose
    -Q, --quiet             - be less verbose


----

This program is part of the PAKE toolset and is published under GNU GPL v3+ license.
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import os
import sys
import urllib
import warnings

import clap
import pake


uifile = pake.shared.getuipath('packages')
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


root = pake.shared.getnodepath()
fail = False

# this will execute the program if there is no nest on which to operate
# exception is when the program is called in `init` modes
# because it means that user will be initializing the nest
if not root: exit('pake: fatal: no root node found')

if str(ui) == '':
    """This is a place of non-global options like --gen-index.
    """
    if '--gen-index' in ui:
        if '--quiet' not in ui: print('pake: packages: building index...')
        index, errors = pake.packages.db.getindex(root)
        if '--verbose' in ui:
            print('pake: indexed {0} package(s)'.format(len(index)))
            print('pake: encountered {0} error(s)'.format(len(errors)))
        if '--debug' in ui:
            for e in errors: print('pake: error encountered: {0}'.format(e))
        if '--quiet' not in ui: print('pake: packages: finished building index')
else:
    if '--debug' in ui: print('pake: fail: mode `{0}` is not implemented yet'.format(str(ui)))
