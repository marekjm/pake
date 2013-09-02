#!/usr/bin/env python3


"""Interface to PAKE package repository.

SYNTAX:
    pakepackage [global opts...] [mode [mode opts...]]

GLOBAL OPTIONS:
    These options can be placed before or after mode declaration.

    -v, --version           - print version information and exit
    -V, --verbose           - be more verbose
    -Q, --quiet             - be less verbose


MODES:

init:
    Mode used for initalization of the package repository.

    -f, --force             - force node initialization (used for reinitializing)


meta:
    Mode used for manipulation and checking of meta.json configuration file.

    -s, --set KEY VALUE     - used to set a key in meta.json
    -r, --remove KEY        - remove key from meta.json
    -l, --list-keys         - list keys in meta.json (if --verbose list format is KEY: VALUE\\n)
    -p, --pretty            - format JSON in a pretty way
    -r, --reset             - reset meta.json to default state


deps:
    Mode used for manipulating the list of dependencies for the package.

    -s, --set NAME          - set dependency
    -r, --remove NAME       - remove dependency
    -m, --min-version STR   - set this version as minimum required
    -M, --max-version STR   - set this version as maximum allowed
    -o, --origin URL        - set URL from which the dependency can be downloaded (currently required
                              but it will become optional once I implement package searching)


----

This program is part of the PAKE toolset and is published under GNU GPL v3+ license.
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import getpass
import os
import sys
import urllib
import warnings

import clap
import pake


uifile = pake.shared.getuipath('repo')
if not uifile: exit('pake: ui: fatal: no ui file found')

formater = clap.formater.Formater(sys.argv[1:])
formater.format()

builder = clap.builder.Builder(path=uifile, argv=list(formater))
builder.build()

ui = pake.shared.checkinput(builder.get())


if '--version' in ui:
    print(pake.__version__)
    exit()

if '--help' in ui:
    print(__doc__)
    exit()


root = pake.shared.getrepopath()
fail = False

# this will execute the program if there is no node on which to operate
# exception is when the program is called in `init` modes
# because it means that user will be initializing the node
if not root and str(ui) != 'init': exit('pake: fatal: no repository found in current directory')

if str(ui) == 'init':
    """This mode is used for initialization of local node.
    Note, that when you'll reinitialize all config JSON will
    be overwritten.
    """
    if root:
        if '--debug' in ui: print('pake: debug: repository already exists in {0}'.format(root))
        if '--force' in ui:
            pake.repository.remove(root)
            message = 'pake: removed old repository'
            if '--verbose' in ui: message += ' from {0}'.format(root)
            if '--quiet' not in ui: print(message)
        else:
            message = 'pake: fatal: repository cannot be initialized'
            if '--verbose' in ui: message += ' in {0}'.format(root)
            if '--quiet' not in ui: print(message)
            fail = True
    if not fail:
        root = pake.shared.getrepopath(check=False)
        pake.repository.makedirs(root)
        pake.repository.makeconfig(root)
        message = 'pake: repository initialized'
        if '--verbose' in ui: message += ' in {0}'.format(root)
        if '--quiet' not in ui: print(message)
elif str(ui) == 'meta':
    """Logic for meta.json manipulation.
    """
    meta = pake.config.repository.Meta(root)
    if '--set' in ui:
        key, value = ui.get('--set')
        meta.set(key, value)
    if '--remove' in ui:
        meta.remove(ui.get('--remove'))
    if '--get' in ui:
        print(meta.get(ui.get('--get')))
    if '--list-keys' in ui:
        if '--verbose' in ui:
            for key in sorted(meta.keys()): print('{0}: {1}'.format(key, meta.get(key)))
        else:
            print(', '.join(sorted(meta.keys())))
    if '--reset' in ui:
        meta.reset()
    if '--pretty' in ui:
        #   this should be routine and independent from
        #   every other options to always enable the possibility
        #   to format JSON in pretty way
        meta.write(pretty=True)
elif str(ui) == 'deps':
    ui = ui.parser
    dependencies = pake.config.repository.Dependencies(root)
    if '--list' in ui:
        if '--verbose' in ui:
            for d in list(dependencies):
                dep = dependencies[d]
                report = '  * {0} ({1})'.format(d, dep['origin'])
                if 'min' in dep: report += ' >={0}'.format(dep['min'])
                if 'max' in dep: report += ' <={0}'.format(dep['max'])
                print(report)
        else:
            report = ', '.join(list(dependencies))
            if report: print(report)

    if str(ui) == 'set':
        dep = {}
        name = ui.get('--name')
        dep['origin'] = ui.get('--origin')
        if '--min-version' in ui: dep['min'] = ui.get('-m')
        if '--max-version' in ui: dep['max'] = ui.get('-M')
        dependencies.set(name=name, dependency=dep)
    if str(ui) == 'remove':
        if ui.arguments:
            for i in ui.arguments:
                try:
                    dependencies.remove(i)
                    print('pake: repo: removed dependency: {0}'.format(i))
                except KeyError:
                    print('pake: warning: undefined dependency: {0}'.format(i))
                finally:
                    pass
elif str(ui) == 'files':
    ui = ui.parser
    files = pake.config.repository.Files(root)

    """Here are options local to *files* mode and not its sub-modes, e.g. --list.
    """
    if '--list' in ui:
        for i in files: print(' * {0}'.format(i))

    if str(ui) == 'add':
        """If directories are found on arguments list they are added to file list
        of current repository.
        Files inside these directories are added unless --not-recursive option is passed in which
        case only directories are added.
        """
        def scan(directory):
            """Recursively scan the directory and return its contents as list.
            """
            files = []
            for i in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, i)):
                    files.append(os.path.join(directory,i))
                elif os.path.isdir(os.path.join(directory, i)):
                    files.extend(scan(os.path.join(directory, i)))
                else:
                    warnings.warn('{0} is not a file or directory: dropped'.format(i))
            return files

        candidates = []
        accepted = []
        dropped = []

        # create list of candidate files
        for i in ui.arguments:
            if os.path.isfile(i): candidates.append(i)
            elif os.path.isdir(i): candidates.extend(scan(i))

        if '--regexp' in ui:
            # filter them according to given regular expression(s)
            regexp = re.compile(options.get('--regexp'))
            for item in candidates:
                if '--exclude' in ui:
                    # if regexp is used for excluding files
                    # drop all matching names and
                    # accept all thet do not
                    if regexp.match(item): dropped.append(item)
                    else: accepted.append(item)
                else:
                    # otherwise accept all matching names and
                    # drop the non-matching ones
                    if regexp.match(item): accepted.append(item)
                    else: dropped.append(item)
        else:
            accepted = candidates

        # append accepted files to JSON configuration
        for c in accepted:
            if '--verbose' in ui: print(' + {0}'.format(c))
            files.add(c)

        # inform user about dropped files
        if '--quiet' not in ui:
            for d in dropped: print(' !  {0}'.format(d))
        else:
            pass
elif str(ui) == 'release':
    """Logic for managing release archives.
    """
    if '--create' in ui:
        pake.repository.releases.makepackage(root)
else:
    if '--debug' in ui: print('pake: fail: mode `{0}` is implemented yet'.format(str(ui)))
