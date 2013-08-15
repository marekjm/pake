#!/usr/bin/env python3


"""This is base module for PAKE user interface.

It is not imported with:

    import pake

instead, you have to import it explicitly:

    from pake.ui import base

to use it.

This is written this way because users may want to use
different interfaces and not pull this module when doing
import to access the backend.

Also, we need to import `pake` itself to get version information
and if `pake` imported `ui` and `ui` imported `pake` then it
would cause an error (recursive, looped imports - terrible thing).
"""

import re


import clap
import pake


def getuipath(ui, debug=False):
    """Returns appropriate UI file or returns None if file cannot be found.
    """
    uifile = ''
    base = os.path.join('ui', '{0}.json'.format(ui))
    locations = [   ('.'),
                    ('', 'home', getpass.getuser(), '.local', 'share', 'pake'),
                    ('', 'usr', 'share', 'pake'),
                    ]
    locations = [os.path.abspath(os.path.join(*l)) for l in locations]
    for l in locations:
        path = os.path.join(l, base)
        if debug: print(path, end='  ')
        if os.path.isfile(path):
            uifile = path
            if debug: print('[  OK  ]')
            break
        if debug: print('[ FAIL ]')
    return uifile


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
