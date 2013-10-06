#!/usr/bin/env python3

"""Module provides interface for managing nest's package:
adding/removing files and directories.
"""

import os
import shutil
import tarfile
import warnings

#   but can be obtained from: https://github.com/marekjm/but
from but import scanner as butscanner

from pake import config, errors


def adddir(root, path, recursive=True, avoid=[], avoid_exts=[]):
    """Add path to list of files.

    :param root: root of nest
    :param path: path to add
    :param recursive: scan subdirectories recursively (or not)
    :param avoid: list of regexp strings which, if the macth is found, will cause file or directory not to be added
    :param avoid_exts: do not add files with these extensions
    """
    if not os.path.isdir(path): raise OSError('\'{0}\' is not a directory'.format(path))
    scanner = butscanner.Scanner(path)
    for i in avoid_exts: scanner.discardExtension(i)
    for i in avoid: scanner.discardRegexp(i)
    scanner.scan()
    files = config.nest.Files(root)
    for i in scanner.files: files.add(i)
    files.write()


def addfile(root, path):
    """Add file to list of files.

    :param root: root of the nest
    :param path: path to add
    """
    if not os.path.isfile(path): raise OSError('\'{0}\' is not a file'.format(path))
    config.nest.Files(root).add(path).write()


def build(root):
    """Builds a package from files contained in nest.
    Version for the build is taken from meta.
    This forces user to regularly update the metadata and
    prevents accidental errors like typing '0.11' instead of '0.1.1'.
    In meta this can be easily changed but after build it would require
    removal of the newly created directory, check, manual edit of versions.json and
    a rebuild.

    Archive file is named: build.tar.xz
    It is located in NESTROOT/versions/:version/build.tar.xz

    :param root: root for the nest
    """
    meta = config.nest.Meta(root)
    files = config.nest.Files(root)

    if meta['name'] == '': raise errors.PAKEError('name is not specified')
    if meta['version'] == '': raise errors.PAKEError('version is not specified')
    if not list(files): warnings.warn('creating empty package')

    path = os.path.join(root, 'versions', meta['version'])
    # raise exception if trying to rebuild a package second time with
    # the same version
    if os.path.isfile(path): raise FileExistsError(path)
    else: os.mkdir(path)

    tarname = os.path.join(path, 'build.tar.xz')
    package = tarfile.TarFile(name=tarname, mode='w')
    package.xzopen(name=tarname, mode='w')
    for f in files: package.add(f)
    package.close()

    for name in ['meta.json', 'dependencies.json']:
        shutil.copy(os.path.join(root, name), os.path.join(path, name))
