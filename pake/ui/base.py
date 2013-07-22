#!/usr/bin/env python3


"""This is base module for PAKE user interface.

It is not imported with:
    
    import pake

instead, you have to import it explicitly:

    import pake.ui

to use it.

This is written this way because users may want to use
different interfaces and not pull this module when doing
import to access the backend.

Also, we need to import `pake` itself to get version information
and if `pake` imported `ui` and `ui` imported `pake` then it
would cause an error (looped imports).
"""


import clap
import pake


def printversion(options):
    """Prints version information.

    By default it's version of pake backend but user can
    specify component which version he/she wants to print.

    Components are only libraries not found in standard Python 3
    library. Currently valid --component arguments are:
    *   clap:       version of CLAP library (used to build user interface),
    """
    version = ''
    if '--component' in options: component = options.get('--component')
    else: component = 'backend'
    if component in ['backend', 'pake']: version = pake.__version__
    elif component == 'clap': version = clap.__version__
    else: print('pake: fatal: no such component: {0}'.format(component))
    if '--verbose' in options and version: version = '{0} {1}'.format(component, version)
    if version: print(version)


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
