#!/usr/bin/env python3


import os
import sys

import clap
import pake


root = os.path.join(os.path.abspath(os.path.expanduser('~')), '.pakenode')
verbose = False


def set(key, value):
    pake.node.Meta(root).set(key, value)
    if verbose: print('pake: key \'{0}\' set to value \'{1}\''.format(key, value))

def get(key):
    print(pake.node.Meta(root).get(key))

def remove(key):
    pake.node.Meta(root).remove(key)
    if verbose: print('pake: key \'{0}\' removed from meta'.format(key))

def echo():
    meta = pake.node.Meta(root)
    keys = sorted(list(meta.content.keys()))
    if not verbose: print(', '.join(keys))
    else: [print('{0}: {1}'.format(k, meta.get(k)))for k in keys]


formater = clap.formater.Formater(sys.argv[1:])
formater.format()
options = clap.parser.Parser(list(formater))
options.add(long='get')
options.add(long='set')
options.add(long='rm')
options.add(long='print')
options.add(long='verbose')
options.add(long='missing')

try:
    options.check()
except clap.errors.UnrecognizedOptionError as e:
    print('pake: fatal: unrecognized option: {0}'.format(e))
    exit()

options.parse()

if '--root' in options: root = options.get('--root')
if '--verbose' in options: verbose = True


if '--get' in options: get(options.arguments[0])
elif '--set' in options: set(options.arguments[0], options.arguments[1])
elif '--rm' in options: remove(options.arguments[0])
elif '--print' in options: echo()
elif '--missing' in options:
    message = '{0}'
    if verbose: message = 'pake: meta.json: missing keys: {0}'
    missing = pake.node.Meta(root).missing()
    if missing: print(message.format(', '.join(pake.node.Meta(root).missing())))
    elif not missing and verbose: print('pake: meta.json: all required keys are in place')
    else: pass
else: pass
