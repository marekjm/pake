#!/usr/bin/env python3

import os
import shutil
import sys

import pake
import clap


name = sys.argv[sys.argv.index('--name')+1]

root = '.'

reinit = ''
if os.path.isdir(os.path.join(root, '.pake')): reinit = 're'

pake.package.init(root)
pake.package.setconfig(root, name)

print('pake: repository {1}initialized in {2}'.format(reinit, root))
