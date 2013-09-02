#!/usr/bin/env python3

"""This file is concerned with releases of the repository.
"""

import os
import tarfile
import warnings

from pake import config


def makepackage(root, overwrite=False):
    """Makes a package from files contained in repository.

    :param root: root for the repository
    """
    meta = config.repository.Meta(root)
    files = config.repository.Files(root)
    if not files.content: warnings.warn('creating package with empty file list')
    name = '{0}-{1}.tar.xz'.format(meta['name'], meta['version'])
    path = os.path.join(root, 'releases', name)
    if not overwrite and os.path.isfile(path): raise FileExistsError(path)
    package = tarfile.TarFile(name=path, mode='w')
    package.xzopen(name=path, mode='w')
    for f in files: package.add(f)
    package.close()
