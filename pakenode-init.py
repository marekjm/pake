#!/usr/bin/env python3

import os
import shutil
import sys

import clap
import pake



formater = clap.formater.Formater(sys.argv[1:])
formater.format()
options = clap.parser.Parser(list(formater))
options.add(short='v', long='version')
options.add(short='h', long='help')
options.add(long='re', hint='required when reinitializing, it tells pake that it should remove old repository and create new')
options.add(short='R', long='root', type=str, hint='alternative root, warning: *only* for testing purposes')
options.add(long='verbose', short='v')
options.check()
options.parse()
if '--help' in options:
    options.help()
    exit()
if '--version' in options:
    if '--verbose' in options: print('pake: version: {0}'.format(pake.__version__))
    else: print(pake.__version__)
    exit()

root = os.path.abspath(os.path.expanduser('~'))
if '--root' in options: root = options.get('--root')
run = True
reinit = ''
message = ''


if os.path.isdir(os.path.join(root, '.pakenode')) and '--re' in options:
    shutil.rmtree(os.path.join(root, '.pakenode'))
    if '--verbose' in options: print('pake: removed old node repository')
    reinit = 're'
elif os.path.isdir(os.path.join(root, '.pakenode')) and '--re' not in options:
    run = False
    if '--verbose' in options: print('pake: fatal: node repository found, use --re to reinitialize')
    message = 'pake: fail: cannot initialize repository'


if run:
    pake.node.makedirs(root)
    pake.node.makeconfig(root)
    message = 'pake: repository {0}initialized in {1}'.format(reinit, os.path.join(root, '.pakenode'))


print(message)
