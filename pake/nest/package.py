#!/usr/bin/env python3

"""Module provides interface for managing nest's package:
adding/removing files and directories.
"""

import os
import shutil
import tarfile
import warnings

import pyversion
from but import scanner as butscanner

from .. import config, errors


def addfile(root, path):
    """Add file to list of files.

    :param root: root of the nest
    :param path: path to add
    """
    if not os.path.isfile(path): raise errors.NotAFileError('\'{0}\' is not a file'.format(path))
    files = config.nest.Files(root)
    if os.path.normpath(path) not in [os.path.normpath(i) for i in files]: files.add(path)
    files.write()


def adddir(root, path, recursive=True, avoid=[], avoid_exts=[]):
    """Add path to list of files.

    :param root: root of nest
    :param path: path to add
    :param recursive: scan subdirectories recursively (or not)
    :param avoid: list of regexp strings which, if the match is found, will cause file or directory not to be added
    :param avoid_exts: do not add files with these extensions
    """
    if not os.path.isdir(path): raise OSError('\'{0}\' is not a directory'.format(path))
    scanner = butscanner.Scanner(path)
    for i in avoid_exts: scanner.discardExtension(i)
    for i in avoid: scanner.discardRegexp(i)
    for i in scanner.scan().files: addfile(root, i)


def build(root, version):
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

    warnings.warn('pake.nest.package.build(root={0}, version={1})'.format(repr(root), repr(version)))

    # checking for all the data required to build the package
    if meta['name'] == '': raise errors.PAKEError('name is not specified')
    if not pyversion.version.valid(version, strict=False): raise errors.InvalidVersionError(version)
    if not list(files): warnings.warn('creating empty package')

    releasepath = os.path.join(root, 'versions', version)
    # raise exception if trying to rebuild a package second time with
    # the same version
    if os.path.isdir(releasepath): raise FileExistsError(releasepath)
    else: os.mkdir(releasepath)

    tarname = os.path.join(releasepath, 'build.tar.xz')
    package = tarfile.TarFile(name=tarname, mode='w')
    package.xzopen(name=tarname, mode='w')
    for f in files:
        package.add(os.path.normpath(f))
    if 'install.fsrl' not in [os.path.normpath(i) for i in files]:
        warnings.warn('no installation script included in package {0}-{1}'.format(meta['name'], version))
    if 'remove.fsrl' not in [os.path.normpath(i) for i in files]:
        warnings.warn('no removal script included in package {0}-{1}'.format(meta['name'], version))

    package.close()

    for name in ['meta.json', 'dependencies.json']:
        shutil.copy(os.path.join(root, name), os.path.join(releasepath, name))

    config.nest.Versions(root).add(version).write()
