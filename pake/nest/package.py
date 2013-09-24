#!/usr/bin/env python3

"""Module provides interface for managing nest's package:
adding/removing files and directories.
"""

import os
import re
import tarfile

#   but can be obtained from: https://github.com/marekjm/but
from but import scanner as butscanner

from pake import config


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
    """Makes a package from files contained in repository.
    Version is obtained from meta.
    Name format is:
        {name}-{version}.tar.xz

    :param root: root for the repository
    """
    meta = config.nest.Meta(root)
    files = config.nest.Files(root)
    if not files.content:
        warnings.warn('creating empty package')
    name = '{0}-{1}.tar.xz'.format(meta['name'], meta['version'])
    if meta['name'] == '': raise errors.PAKEError('name is not specified')
    if meta['version'] == '': raise errors.PAKEError('version is not specified')
    path = os.path.join(root, 'releases', name)
    # raise exception if trying to build a package second time with
    # the same version
    if os.path.isfile(path):
        raise FileExistsError(path)
    package = tarfile.TarFile(name=path, mode='w')
    package.xzopen(name=path, mode='w')
    for f in files: package.add(f)
    package.close()
