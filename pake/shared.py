#!/usr/bin/env python3

"""This module contains routines, functions and variables shared between
various PAKE modules.
"""


import os
import getpass

# locations in which PAKE will search for configration files, UI files etc.
locations = [   ('.'),
                ('', 'home', getpass.getuser(), '.local', 'share', 'pake'),
                ('', 'usr', 'share', 'pake'),
                ]


def getuipath(ui, debug=False):
    """Returns appropriate UI file or returns None if file cannot be found.
    """
    uifile = ''
    base = os.path.join('ui', '{0}.json'.format(ui))
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


def getrootpath(debug):
    """Returns path to PAKE root.
    Returns empty string if root cannot be found.
    """
    path = os.path.expanduser('~')
    path = os.path.join(path, '.pakenode')
    if not os.path.isdir(path): path = ''
    return path
