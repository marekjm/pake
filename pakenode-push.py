#!/usr/bin/env python3


import getpass
import os
import sys

import clap
import pake


formater = clap.formater.Formater(sys.argv[1:])
formater.format()

options = clap.parser.Parser(list(formater))
options.add(short='v', long='verbose')
options.add(long='root', type=str)
options.add(short='m', long='mirrors')
options.add(short='O', long='only-mirrors')
options.add(short='R', long='remote', type=str)
options.add(short='F', long='create-fallback')
options.add(short='d', long='dont-push')
options.add(short='s', long='store-auth')
options.add(short='u', long='use-auth')

try:
    options.check()
except clap.errors.UnrecognizedOptionError as e:
    print('pake: fatal: unrecognized option: {}'.format(e))
    exit(1)

options.parse()


if '--store-auth' not in options and '--dont-push' in options:
    print('pake: abort: this does not make sense')
    print('pake: try adding --store-auth or removing --dont-push')
    exit(1)


if '--root' in options: root = options.get('--root')
else: root = os.path.abspath(os.path.join(os.path.expanduser('~'), '.pakenode'))

if '--verbose' in options: verbose = True
else: verbose = False


if '--use-auth' in options:
    authfile = open(os.path.join(root, '.authfile'))
    data = authfile.readlines()
    username = data[0].strip()
    password = data[1].strip()
    authfile.close()
    if '--verbose' in options: print('pake: authentication data loaded')
else:
    try:
        node = pake.node.Meta(root).get('push-url')
        username = input("Username for '{0}': ".format(node))
        password = getpass.getpass("Password '{0}@{1}': ".format(username, node))
        go_ahead = True
    except (KeyboardInterrupt, EOFError):
        go_ahead = False
        print()
    finally:
        if not go_ahead: exit()

if '--store-auth' in options:
    authfile = open(os.path.join(root, '.authfile'), 'w')
    authfile.write('{0}\n{1}'.format(username, password))
    authfile.close()
    if '--verbose' in options: print('pake: authentication data stored')

if '--remote' in options:
    cwd = options.get('--remote')
    if verbose: print('pake: remote working directory will be changed to: {0}'.format(cwd))
else:
    cwd = ''

if '-F' in options:
    if verbose: print('pake: fallback files will be created')
    fallback = True
elif '-F' not in options and '--dont-push' in options:
    fallback = False
else:
    if verbose: print('pake: alert: no fallback files will be created!')
    fallback = False


fail = False
if '--dont-push' not in options and '--only-mirrors' not in options:
    if verbose:
        print('pake: uploading...\t', end='\t')
    try:
        pake.node.pushmain(root, username=username, password=password, cwd=cwd, fallback=fallback)
        message = '[  OK  ]'
    except (Exception) as e:
        message = '[ FAIL ]: {0}'.format(e)
        fail = True
    finally:
        pass
    if verbose: print(message)

if fail and verbose: print('pake: fail: push to main node failed')

if fail and '--mirrors' not in options:
    print('pake: fatal: push was not successful')
    exit()

fail = False
if '--mirrors' in options or '--only-mirrors' in options and '--dont-push' not in options:
    if verbose: print('pake: uploading mirrors...', end='\t')
    try:
        pake.node.pushmirrors(root, username=username, password=password, cwd=cwd, fallback=fallback)
        message = '[  OK  ]'
    except (Exception) as e:
        message = '[ FAIL ]: {0}'.format(e)
        fail = True
    finally:
        pass
    if verbose: print(message)

if fail and verbose: print('pake: fail: push to mirrors failed')

if fail: print('pake: fatal: push was not successful')
