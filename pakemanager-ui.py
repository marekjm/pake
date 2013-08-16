#!/usr/bin/env python3


"""This is PAKE user interface.

Currently, it provides methods for:

    *   ...,
    *   ....

@help.begin_global
Syntax:

    pakemanager [global options] [MODE [mode options]]


Global options:
    -h, --help          - display this message
    -v, --version       - display version information
        --component STR - choose component (ui, backend) which version should be displayed (only with --version)
    -V, --verbose       - print more messages, conflicts with: --quiet
    -Q, --quiet         - print less messages, conflicts with: --verbose (doesn't really do anything)

@help.end_global
@help.footer
----


This script is published under GNU GPL v3 or any later version of this license.
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import sys

import clap
import pake

from pake.ui import base as ui

formater = clap.formater.Formater(sys.argv[1:])
formater.format()

options = clap.modes.Parser(list(formater))
options.addOption(short='h', long='help')
options.addOption(short='v', long='version')
options.addOption(short='C', long='component', arguments=[str], requires=['--version'])
options.addOption(short='V', long='verbose', conflicts=['--quiet'])
options.addOption(short='Q', long='quiet', conflicts=['--verbose'])

options = ui.checkinput(options)

if '--version' in options:
    ui.printversion(options)
    exit()

if '--help' in options:
    print(ui.gethelp(__doc__, options))
    exit()
