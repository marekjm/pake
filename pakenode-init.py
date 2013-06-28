#!/usr/bin/env python3

import os
import shutil
import sys

import clap
import pake



formater = clap.formater.Formater(sys.argv[1:])
formater.format()
options = clap.parser.Parser(list(formater))
options.add(long='re')
options.add(long='root')
options.add(long='verbose', short='v')
options.check()
options.parse()

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
