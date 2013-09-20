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
    if not os.path.isabs(path): warnings.warn('path {0} is not absolute'.format(path))
    path = os.path.abspath(path)
    meta = config.nest.Meta(path)
    _check(meta.content)
    config.node.Packages(root).set(meta.content)
    config.node.Registered(root).set(name=meta.get('name'), path=path)


def update(root, name):
    """Updates repository metadata for specified package.

    :param name: name of the package
    """
    path = config.node.Registered(root).getpath(name)
    meta = config.repository.Meta(path)
    _check(meta.content)
    config.node.Packages(root).set(meta.content)


def unregister(root, name):
    """Unregisters repository.

    :param root: path to the root of the node
    :param name: name of the package
    """
    config.node.Registered(root).remove(name)
