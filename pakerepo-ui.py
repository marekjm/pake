#!/usr/bin/env python3


"""This is the interface to PAKE repository (the `.pake` directory).

Currently, it provides methods for:

    *   initializing new repositories,
    *   building release packages,
    *   updating package metadata,
    *   adding and removing files from the package,

Syntax:

    pakenode [global options] [MODE [mode options]]


Global options:
    -h, --help          - display this message
    -v, --version       - display version information
        --component STR - choose component (ui, backend) which version should be displayed (only with --version)
    -V, --verbose       - print more messages, conflicts with: --quiet
    -Q, --quiet         - print less messages, conflicts with: --verbose (doesn't really do anything)


----

If one wants to register package in node database (packages.json) one should
use `pakenode` interface.

Easiest way to create and register new package is to create a PAKE repository,
add files and tell the node that a new package has been created.

    pakerepo --verbose init --name foo-package
    pakerepo --verbose files --add foo/__init__.py
    pakerepo --verbose meta --set version 0.0.1
    pakerepo --verbose dependencies --add bar --min 0.1.2 --max 2.1.0
    pakenode --verbose register .

What is important is properly crafted `meta.json` file
`pakenode` will scan it and refuse to register package if its contents are invalid.
Minimal contents are:
    *   name:           name of the package,
    *   version:        version of the package,
    *   license:        license used,
    *   author:         author(s) of the software.
    *   dependencies:   list of dependencies for the package,

Optional (but helpful) keys are:
    *   keywords:       keywords used when searching for package,
    *   description:    description of the package.

----


This script is published under GNU GPL v3 or any later version of this license. 
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import os
import shutil
import sys

import pake
import clap


__version__ = '0.0.3'


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
except clap.errors.NeededOptionNotFoundError as e:
    message = 'needed option not found: {0}'.format(e)
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
    version = 'pakerepo {0}'.format(__version__)
    if '--verbose' in options:
        #   if --verbose if passed print also backend version
        version += ' (pake backend: {0})'.format(pake.__version__)
    if '--component' in options:
        #   if --component is passed print specified component's version
        component = options.get('--component')
        if component in ['backend', 'pake']:
            version = pake.__version__
            component = 'pake'
        elif component == 'ui': version = __version__
        elif component == 'clap': version = clap.__version__
        else:
            print('pake: fatal: no such component: {0}'.format(component))
            version = ''
        if '--verbose' in options and version: version = '{0} {1}'.format(component, version)
    if version: print(version)
    exit()

if '--help' in options:
    print(__doc__)
    exit()


message = ''
if message and '--quiet' not in options: print('pakerepo: {0}'.format(message))
