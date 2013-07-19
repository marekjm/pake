#!/usr/bin/env python3


"""This is PAKE user interface.

Currently, it provides methods for:

    *   ...,
    *   ....

Syntax:

    pake [global options] [MODE [mode options]]


Global options:
    -h, --help          - display this message
    -v, --version       - display version information
        --component STR - choose component (ui, backend) which version should be displayed (only with --version)
    -V, --verbose       - print more messages, conflicts with: --quiet
    -Q, --quiet         - print less messages, conflicts with: --verbose (doesn't really do anything)


----


This script is published under GNU GPL v3 or any later version of this license. 
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import os
import shutil
import sys

import pake
import clap


__version__ = '0.0.1'


formater = clap.formater.Formater(sys.argv[1:])
formater.format()

options = clap.modes.Parser(list(formater))
options.addOption(short='h', long='help')
options.addOption(short='v', long='version')
options.addOption(short='C', long='component', argument=str, requires=['--version'])
options.addOption(short='V', long='verbose', conflicts=['--quiet'])
options.addOption(short='Q', long='quiet', conflicts=['--verbose'])


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
        print('pakerepo: fatal: {0}'.format(message))
        exit(1)
    else:
        options.parse()

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
    version = 'pakeui {0}'.format(__version__)
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
    print(__doc__)
    exit()
