#!/usr/bin/env python3

import os
import sys

import clap
import pake


try:
    mode = sys.argv[1]
except IndexError:
    mode = ''
finally:
    pass

formater = clap.formater.Formater(sys.argv[2:])
formater.format()

options = clap.parser.Parser(list(formater))
options.add(long='verbose')
options.add(long='root')

try:
    options.check()
except clap.errors.UnrecognizedOptionError as e:
    print('pake: fatal: unrecognized option: {0}'.format(e))
    exit()

options.parse()

if '--root' in options: root = options.get('--root')
else: root = os.path.join(os.path.abspath(os.path.expanduser('~')), '.pakenode')

if '--verbose' in options: verbose = True
else: verbose = False


def add(url):
    pake.node.Mirrors(root).add(url)
    if verbose: print('pake: added URL to mirrors: {0}'.format(url))


def remove(url):
    pake.node.Mirrors(root).remove(url)
    if verbose: print('pake: removed URL from mirrors: {0}'.format(url))


def echo():
    mirrors = pake.node.Mirrors(root)
    for url in mirrors.content: print(url)


if mode == 'add': [add(url) for url in options.arguments]
elif mode == 'rm': [remove(url) for url in options.arguments]
elif mode == 'print': echo()
elif mode == '--help' or mode == '': print('available modes are: add, rm, print')
else: print('pake: fatal: unknown mode: {0}'.format(mode))
