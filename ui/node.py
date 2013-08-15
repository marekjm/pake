#!/usr/bin/env python3


"""Interface to PAKE node.


This program is part of the PAKE toolset and is published under GNU GPL v3+ license.
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import getpass
import os
import sys

import clap
import pake


uifile = pake.shared.getuipath('node', debug=True)
if not uifile: exit('pake: ui: fatal: no ui file found')

formater = clap.formater.Formater(sys.argv[1:])
formater.format()

builder = clap.builder.Builder(path=uifile, argv=list(formater))
builder.build()

ui = pake.ui.base.checkinput(builder.get())


if '--version' in ui:
    print(pake.__version__)
    exit()

if '--help' in ui:
    print(__doc__)
    exit()


root = pake.shared.getrootpath()
fail = False

if str(ui) == 'init':
    """This mode is used for initialization of local node.
    Note, that when you'll reinitialize all config JSON will
    be overwritten.
    """
    if os.path.isdir(root):
        if '--verbose' in ui: print('pake: debug: repository already exists in {0}'.format(root))
        if '--force' in ui:
            pake.node.local.remove(root)
            message = 'pake: removed old repository'
            if '--verbose' in ui: message += ' from {0}'.format(root)
            if '--quiet' in ui: print(message)
        else:
            message = 'pake: fatal: repository cannot be initialized'
            if '--verbose' in ui: message += ' in {0}'.format(root)
            if '--quiet' not in ui: print(message)
            fail = True
    if not fail:
        pake.node.local.makedirs(root)
        pake.node.local.makeconfig(root)
    else:
        pass
