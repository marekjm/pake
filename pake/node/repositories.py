#!/usr/bin/env python3

"""Backend for managing repositories registered in local node.

It contains functions that may be used to:
*   register a repository in the node,
*   remove a repository from the node,
*   synchronize repository's contents and contents of the package in the node,
"""


import os
import warnings

from pake import config


def registerrepo(root, repository):
    """Register PAKE repository in the node. This will allow to
    push the package provided to the Net.

    :param root: path to the root of your node
    :param repository: path to the root of the repository being registered
    """
    root = os.path.join(root, '.pakenode')
    meta = config.repository.Meta(repository)
    if 'name' not in meta or 'version' not in meta:
        raise Exception('invalid `meta.json` file for repository: {0}'.format(repository))
    name = meta.get('name')
    if not name:
        exit('cannot register unnamed package')
    config.node.Registered(root).add(name, repository)
    config.node.Packages(root).add(meta)
    package_dir = os.path.join(root, 'packages', name)
    os.mkdir(package_dir)
    meta.write(package_dir)
    config.repository.Dependencies(repository).write(package_dir)


def synchronize(root, repository):
    """Updates repository data, copies new packages to node etc.
    """
    root = os.path.join(root, '.pakenode')
    meta = config.repository.Meta(repository)
    package_dir = os.path.join(root, 'packages', meta.get('name'))
    meta.write(package_dir)
    config.repository.Dependencies(repository).write(package_dir)
    repository_versions_dir = os.path.join(repository, 'versions')
    for item in os.listdir(repository_versions_dir):
        if not os.path.isfile(os.path.join(package_dir, item)):
            shuilt.copy(os.path.join(repository_versions_dir, item), os.path.join(package_dir, item))


def remove(root, name, directory=False):
    """Removes previously registared repository.

    :param root: path to the root of the node
    :param name: name of the package
    :param directory: whether to remove also the directory containing packages
    """
    root = os.path.join(root, '.pakenode')
    config.node.Registered(root).remove(name)
    if directory: shutil.rmtree(os.path.join(root, 'packages', name))
