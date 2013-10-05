#!/usr/bin/env python3


"""Interface to PAKE nest.

SYNTAX:
    pakenest [global opts...] [mode [mode opts...]]

GLOBAL OPTIONS:
    These options can be placed before or after mode declaration.

    -v, --version           - print version information and exit
    -V, --verbose           - be more verbose
    -Q, --quiet             - be less verbose


MODES:

init:
    Mode used for initalization of the package nest.

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

    SUBMODES:

    set:
        Used for setting new dependencies.

        -m, --min-version STR   - set this version as minimum required
        -M, --max-version STR   - set this version as maximum allowed
        -o, --origin URL        - set URL from which the dependency can be downloaded (currently required
                                  but it will become optional once I implement package searching)
        -n, --name NAME         - name of the package

    update: *not implemented*
        Update information about the dependency.

    remove: *not implemented*
        Remove dependency.
 
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


uifile = pake.shared.getuipath('nest')
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


root = pake.shared.getnestpath()
fail = False

# this will execute the program if there is no nest on which to operate
# exception is when the program is called in `init` modes
# because it means that user will be initializing the nest
if not root and str(ui) != 'init': exit('pake: fatal: no nest found in current directory')

if str(ui) == 'init':
    """This mode is used for initialization of nest.
    Note, that when you'll reinitialize with --force option all config JSON will
    be overwritten.
    """
    if root:
        """This means that a nest already exists in current working directory.
        """
        if '--debug' in ui: print('pake: debug: nest already exists in {0}'.format(root))
        if '--force' in ui:
            """If --force option is given remove the old nest.
            """
            pake.nest.manager.remove(root)
            message = 'pake: removed old nest'
            if '--verbose' in ui: message += ' from {0}'.format(root)
            if '--quiet' not in ui: print(message)
        else:
            """If --force method is not given print error message and
            set fail flag to True.
            """
            message = 'pake: fatal: nest cannot be initialized'
            if '--verbose' in ui: message += ' in {0}'.format(root)
            if '--quiet' not in ui: print(message)
            fail = True
    if not fail:
        """If everything went OK so far try to create the nest: directory structure and
        basic config files.
        """
        root = pake.shared.getnestpath(check=False)
        pake.nest.manager.makedirs(root)
        pake.nest.manager.makeconfig(root)
        message = 'pake: nest initialized'
        if '--verbose' in ui: message += ' in {0}'.format(root)
        if '--quiet' not in ui: print(message)
elif str(ui) == 'meta':
    """Code used for meta.json management.
    """
    meta = pake.config.nest.Meta(root)
    if '--set' in ui:
        """Used to set values in meta.
        If a key already exists it will be overwritten.
        """
        key, value = ui.get('--set')
        meta.set(key, value).write()
    if '--remove' in ui:
        """This is used to remove the key from metadata.
        """
        meta.remove(ui.get('--remove')).write()
    if '--get' in ui:
        """This will print out value fo given key.
        """
        print(meta.get(ui.get('--get')))
    if '--list-keys' in ui:
        """This will print contents of meta.json for the nest.
        """
        if '--verbose' in ui:
            """If --verbose option is passed print data as '{key}: {value}' pairs, each in new line.
            """
            for key in sorted(meta.keys()): print('{0}: {1}'.format(key, meta.get(key)))
        else:
            """If --verbose is not given print a comma separated list of keys.
            """
            print(', '.join(sorted(meta.keys())))
    if '--reset' in ui:
        """This will reset meta.json to default (empty) state.
        """
        meta.reset().write()
    if '--pretty' in ui:
        """This should independent from every other option to enable the possibility
        of formating JSON in pretty way without making any actual changes.
        """
        meta.write(pretty=True)
elif str(ui) == 'deps':
    """Code used to manage dependencies for this nest.
    """
    ui = ui.parser  # this is needed because deps is a nested mode
    dependencies = pake.config.nest.Dependencies(root)
    if '--list' in ui:
        """This will print out all dependencies of current nest.
        """
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
        dependencies.set(name=name, dependency=dep).write()
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
    files = pake.config.nest.Files(root)

    """Here are options local to *files* mode and not its sub-modes, e.g. --list.
    """
    if '--list' in ui:
        for i in files: print(' * {0}'.format(i))

    if str(ui) == 'add':
        """If directories are found on arguments list they are added to file list
        of current nest.
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
    meta = pake.config.nest.Meta(root)
    if '--build' in ui:
        try:
            pake.nest.package.build(root)
            message = 'pake: nest: built {0}-{1}'.format(meta['name'], meta['version'])
        except FileExistsError as e:
            message = 'pake: fatal: build for version {0} already exists'.format(meta['version'])
        finally:
            if '--quiet' not in ui: print(message)
elif str(ui) == '': pass
else:
    if '--debug' in ui: print('pake: fail: mode `{0}` is not implemented yet'.format(str(ui)))
