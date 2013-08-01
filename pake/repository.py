#!/usr/bin/env python3

import os
import tarfile

from pake import config


"""This module contains objects responsible for:
    * creating new package-repos (repos for single package),
    * creating package directories in main repo,
    * managing package metadata,

    * building package archives,
    * installing packages archives,
    * removing packages archives,
"""


def makedirs(root):
    """Creates new PAKE repository.

    :param root: root of the repository
    :type root: str
    """
    subdirectories = ['packages', 'versions']
    os.mkdir(root)
    for name in subdirectories:
        os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Initializes empty PAKE repository.

    :param root: root for the repository
    :type root: str
    """
    config.repository.Meta(root).reset()
    config.repository.Dependencies(root).reset()
    config.repository.Files(root).reset()


def makepackage(root, overwrite=False):
    """Makes a package from files contained in repository.

    :param root: root for the repository
    """
    meta = config.repository.Meta(root)
    files = config.repository.Files(root)
    if not files.content: raise Exception('package will not be created: empty file list')
    name = '{0}-{1}.tar.xz'.format(meta['name'], meta['version'])
    path = os.path.join(root, name)
    if not overwrite and os.path.isfile(path): raise FileExistsError(path)
    archieve = tarfile.TarFile.xzopen(name=path, mode='w')
    for f in files: archieve.add(f)
    archives.close()
