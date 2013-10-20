#!/usr/bin/env python3

"""Backend for managing repositories registered in local node.

It contains functions that may be used to:
*   register a repository in the node,
*   remove a repository from the node,
*   synchronize repository's contents and contents of the package in the node,
"""


import json
import os
import warnings

from pake import config, errors


def _check(meta, path):
    """Checks if nest in given path has valid meta.json.
    """
    required_keys = ['name']
    for key in required_keys:
        if key not in meta:
            raise errors.PAKEError('missing information for nest in: {0}: {1}'.format(path, key))
        if not meta[key]:
            raise errors.PAKEError('missing information for nest in: {0}: {1}'.format(path, key))


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
    _check(meta.content, path)
    config.node.Nests(root).set(name=meta.get('name'), path=path).write()


def unregister(root, name):
    """Unregisters a nest.

    :param root: path to the root of the node
    :param name: name of the package
    """
    config.node.Nests(root).remove(name).write()


def genpkglist(root):
    """Create list of packages available on this node.
    """
    nests = config.node.Nests(root)
    ofstream = open(os.path.join(root, 'packages.json'), 'w')
    packages = []
    for name in nests:
        # if API specs will change to inlcude more data in packages.json this
        # is the place to add teh code
        packages.append(config.nest.Meta(nests.get(name)).get('name'))
    ofstream.write(json.dumps(packages))
    ofstream.close()
