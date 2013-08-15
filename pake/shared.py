#!/usr/bin/env python3

"""This module contains routines, functions and variables shared between
various PAKE modules.
"""


import os
import getpass

import clap


# locations in which PAKE will search for configration files, UI files etc.
uilocations = [ ('.'),
                ('', 'home', getpass.getuser(), '.local', 'share', 'pake'),
                ('', 'usr', 'share', 'pake'),
                ]


def getuipath(ui, debug=False):
    """Returns appropriate UI file or returns None if file cannot be found.
    """
    uifile = ''
    base = os.path.join('ui', '{0}.json'.format(ui))
    locations = [os.path.abspath(os.path.join(*l)) for l in uilocations]
    for l in locations:
        path = os.path.join(l, base)
        if debug: print(path, end='  ')
        if os.path.isfile(path):
            uifile = path
            if debug: print('[  OK  ]')
            break
        if debug: print('[ FAIL ]')
    return uifile


def getrootpath(check=True):
    """Returns path to PAKE root.
    Returns empty string if root cannot be found.

    NOTICE: check parameter should be used only internally

    :param check: check if root really exists
    :type check: bool
    """
    path = os.path.expanduser('~')
    path = os.path.join(path, '.pakenode')
    if check and not os.path.isdir(path): path = ''
    return path


def checkinput(options):
    """Checks user input for errors.
    """
    message = ''
    try:
        options.define()
        options.check()
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
        if not message: options.parse()
    if message: exit('pake: fatal: {0}'.format(message))
    else: return options
