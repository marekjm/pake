#!/usr/bin/env python3


"""This is the interface to PAKE repository (the `.pake` directory).

Currently, it provides methods for:

    *   initializing new repositories,
    *   building release packages,
    *   updating package metadata,
    *   adding and removing files from the package,

@help.begin_global
Syntax:

    pakerepo [global options] [MODE [mode options]]

Global options:
    -h, --help          - display this message
    -v, --version       - display version information
        --component STR - choose component (ui, backend) which version should be displayed (only with --version)
    -V, --verbose       - print more messages, conflicts with: --quiet
    -Q, --quiet         - print less messages, conflicts with: --verbose (doesn't really do anything)


@help.end_global
----

@help.begin_mode=init
If one wants to register package in node database (packages.json) one should
use `pakenode` interface.

Easiest way to create and register new package is to create a PAKE repository,
add files and tell the node that a new package has been created.

    pakerepo --verbose init --name foo-package
    pakerepo --verbose add foo/
    pakerepo --verbose meta --set version 0.0.1
    pakerepo --verbose dependencies --add bar --min 0.1.2 --max 2.1.0
    pakenode --verbose register .

What is important is properly crafted `meta.json` file
`pakenode` will scan it and refuse to register package if its contents are invalid.
Minimal contents are:
    *   name:           name of the package,
    *   version:        version of the package,
    *   license:        license used,
    *   author:         author(s) of the software.
    *   dependencies:   list of dependencies for the package,

Optional (but helpful) keys are:
    *   keywords:       keywords used when searching for package,
    *   description:    description of the package.

@help.end_mode=init
@help.begin_mode=files
This mode is used to manipulate files contained in the package.
Actions taken here do not have any actual effect on real files.

OPTIONS:
    -a, --add                   - add file to package
    -r, --rm                    - remove file from package
    -R, --regexp STR            - add/remove all names matching the pattern
@help.end_mode=files
@help.footer
----


This script is published under GNU GPL v3 or any later version of this license.
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import os
import shutil
import sys
import re

import clap
import pake

from pake.ui import base as ui

formater = clap.formater.Formater(sys.argv[1:])
formater.format()

init = clap.parser.Parser()
init.add(short='n', long='name', arguments=[str], required=True, not_with=['--help'])
init.add(short='f', long='force')

meta = clap.parser.Parser()
meta.add(short='s', long='set', arguments=[str, str],conflicts=['--rm'])
meta.add(short='r', long='rm', arguments=[str], conflicts=['--set'])
meta.add(short='g', long='get', arguments=[str], conflicts=['--set', '--rm'])
meta.add(short='l', long='list')

files = clap.parser.Parser()
files.add(short='a', long='add', conflicts=['--rm'])
files.add(short='r', long='rm', conflicts=['--add'])
files.add(short='R', long='regexp', arguments=[str], needs=['--add', '--rm'])
files.add(short='l', long='list')

dependencies = clap.parser.Parser()

package = clap.parser.Parser()
package.add(short='b', long='build')
package.add(short='O', long='overwrite')

options = clap.modes.Parser(list(formater))
options.addMode('init', init)
options.addMode('meta', meta)
options.addMode('files', files)
options.addMode('dependencies', dependencies)
options.addMode('package', package)
options.addOption(short='h', long='help')
options.addOption(short='v', long='version')
options.addOption(short='C', long='component', arguments=[str], requires=['--version'])
options.addOption(short='V', long='verbose', conflicts=['--quiet'])
options.addOption(short='Q', long='quiet', conflicts=['--verbose'])
options.addOption(short='D', long='debug')

options = ui.checkinput(options)

if '--version' in options:
    ui.printversion(options)
    exit()

if '--help' in options:
    print(ui.gethelp(__doc__, options))
    exit()

root = os.path.abspath(os.path.join('.', '.pakerepo'))
if str(options) == 'init':
    try:
        pake.repository.makedirs(root)
        if '--verbose' in options: print('pake: repo: directories created')
        fail = False
    except FileExistsError as e:
        if '--verbose' in options: print('pake: repo: fail: found old repository')
        if '--debug' in options: print('pake: repo: debug: {0}'.format(e))
        if '--force' in options:
            shutil.rmtree(root)
            if '--verbose' in options: print('pake: repo: removed old repository')
            pake.repository.makedirs(root)
            fail = False
        else:
            fail = True
    finally:
        if not fail:
            pake.repository.makeconfig(root)
            if '--verbose' in options: print('pake: repo: default config files written')
            pake.config.repository.Meta(root).set('name', options.get('--name'))
            message = 'pake: repo: initialized repository'
            if '--verbose' in options: message += ' in {0}'.format(os.path.split(root)[0])
            if '--quiet' not in options: print(message)
        else:
            message = 'pake: repo: fatal: cannot initialize repository'
            if '--verbose' in options: message += ' in {0}'.format(os.path.split(root)[0])
            if '--quiet' not in options: print(message)
elif str(options) == 'meta':
    meta = pake.config.repository.Meta(root)
    if '--set' in options:
        meta.set(*options.get('--set'))
        if '--verbose' in options: print('pake: repo: meta.json: {0} = {1}'.format(key, value))
    if '--get' in options:
        try:
            meta.get(options.get('--get'))
        except KeyError:
            if '--debug' in options:
                print('pake: repo: debug: meta.json: key \'{0}\' was not found'.format(options.get('-g')))
            value = ''
        finally:
            print(value)
    if '--rm' in options:
        meta.remove(options.get('--remove'))
    if '--list' in options:
        print(', '.join(sorted(meta.keys())))
elif str(options) == 'files':
    files = pake.config.repository.Files(root)
    if '--add' in options:
        candidates = options.arguments
        if '--regexp' in options:
            candidates = os.listdir('.')
            regexp = re.compile(options.get('--regexp'))
            accepted = []
            for item in candidates:
                if regexp.match(item): accepted.append(item)
            candidates = accepted
        for item in candidates:
            if (os.path.isfile(item) or os.path.isdir(item)) and item not in files:
                files.add(item)
            else:
                if '--quiet' not in options: print('pake: repo: fail: no such file or directory: {0}'.format(item))
    if '--rm' in options:
        for item in options.arguments:
            if item in files:
                files.remove(item)
            else:
                if '--quiet' not in options: print('pake: repo: files.json: fail: no such file or directory in: {0}'.format(item))
    if '--list' in options:
        for item in files: print(item)
elif str(options) == 'dependencies':
    pass
elif str(options) == 'package':
    if '--build' in options:
        pake.repository.makepackage(root=root, overwrite=('--overwrite' in options))
else: print('mode is not implemeted')
