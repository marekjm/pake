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


def register(root, path):
    """Register PAKE repository in the node. This will allow to
    push the package provided to the Net.

    :param root: path to the root of your node
    :param repository: path to the root of the repository being registered
    """
    meta = config.repository.Meta(path)
    required_keys = ['name', 'version', 'license', 'origin']
    for key in required_keys:
        if key not in meta: raise Exception('missing information for this package: {0}'.format(key))
    name = meta.get('name')
    if not name: raise Exception('cannot register unnamed package')
    if not meta.get('origin'): raise Exception('cannot register package with empty origin')
    config.node.Registered(root).add(name, path)
    config.node.Packages(root).add(meta)


def delete(root, name, directory=False):
    """Removes previously registared repository.

    :param root: path to the root of the node
    :param name: name of the package
    :param directory: whether to remove also the directory containing packages
    """
    config.node.Registered(root).remove(name)
    if directory: shutil.rmtree(os.path.join(root, 'packages', name))
