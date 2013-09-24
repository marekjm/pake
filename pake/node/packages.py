#!/usr/bin/env python3

"""Backend for managing repositories registered in local node.

It contains functions that may be used to:
*   register a repository in the node,
*   remove a repository from the node,
*   synchronize repository's contents and contents of the package in the node,
"""


import os
import warnings

from pake import config, errors


def _check(meta):
    """Checks if repository in given path has valid meta.json.
    """
    required_keys = ['name', 'version', 'license', 'origin']
    for key in required_keys:
        if key not in meta: raise errors.PAKEError('missing information for this package: {0}'.format(key))
        if not meta[key]: raise errors.PAKEError('missing information for this package: {0}'.format(key))


def register(root, path):
    """Register PAKE nest in the node. This will allow to
    push the package provided to the Net.

    :param root: path to the root of your node
    :param path: path to the root of the nest being registered
    """
    if not os.path.isabs(path):
        warnings.warn('path {0} is not absolute'.format(path))
        path = os.path.abspath(path)  # make the path absolute
    meta = config.nest.Meta(path)
    _check(meta.content)
    config.node.Nests(root).set(name=meta.get('name'), path=path).write()


def unregister(root, name):
    """Unregisters a nest.

    :param root: path to the root of the node
    :param name: name of the package
    """
    config.node.Nests(root).remove(name).write()


def makelist(root):
    """Create list of packages available on this node.
    """
    nests = config.node.Nests(root)
    packages = config.node.Packages(root)
    for name in nests:
        path = nests.get(name)
        packages.append(name=config.repository.Meta(path), latest=config.nest.Versions(path)[-1])
    packages.write()
