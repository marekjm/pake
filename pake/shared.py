#!/usr/bin/env python3

"""This module contains routines, functions and variables shared between
various PAKE modules.

API clarifications:

    *   `fake` parameter is inteded to be used only for testing purposes,

    *   `fake` overcomes only default expansion (home and current working directory) and
        will still append .pake* directory to the path,

    *   `check` parameter checks if the roots are really present, it should
        be passed as False only during initialization of the node or
        repository,
"""


import json
import os
import urllib.request

import clap


# locations in which PAKE will search for configration files, UI files etc.
uilocations = [ ('.'),
                (os.path.expanduser('~'), '.local', 'share', 'pake'),
                (os.path.sep, 'usr', 'share', 'pake'),
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


def getnodepath(check=True, fake=''):
    """Returns path to PAKE node root.
    Returns empty string if node cannot be found.

    :param check: check if node really exists
    :type check: bool
    :param fake: fake node root, set by caller (disables expansion and allows to not use home directory)
    :type fake: str
    """
    if fake: path = fake
    else: path = os.path.expanduser('~')
    if check and not os.path.isdir(os.path.join(path, '.pakenode')): path = ''
    return path


def getnestpath(check=True, fake=''):
    """Returns path to PAKE nest in the current working directory.
    Returns empty string if nest cannot be found.

    :param check: check if nest root really exists
    :type check: bool
    :param fake: fake nest root, set by caller (disables expansion and allows to not use cwd)
    :type fake: str
    """
    if fake: path = fake
    else: path = os.path.abspath('.')
    path = os.path.join(path, '.pakenest')
    if check and not os.path.isdir(path): path = ''
    return path


def getenvpath(check=True, fake=''):
    """Returns path to a directory holding PAKE environment descriptions.
    Returns empty string if it cannot be found.
    """
    if fake: path = fake
    else:
        for l in uilocations:
            if os.path.isdir(os.path.join(l, 'env')):
                path = os.path.join(l, 'env')
                break
    if check and not os.path.isdir(path): path = ''
    return path


def fetchjson(url):
    """Fetches JSON from alien node and returns decoded data.

    :param url: url from which to fetch data
    """
    socket = urllib.request.urlopen(url)
    fetched = json.loads(str(socket.read(), encoding='utf-8'))
    socket.close()
    return fetched


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
    except clap.errors.WantedOptionNotFoundError as e:
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
