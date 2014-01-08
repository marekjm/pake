#!/usr/bin/env python3

"""File used to manage local node.
"""

import json
import os
import shutil

from .. import config, shared


def makedirs(root):
    """Creates node directory structure in given root.
    If the .pakenode directory is already in root it will be deleted and
    new one will be created.

    :param root: node root directory
    :type root: str
    """
    ifstream = open(os.path.join(shared.getenvpath(), 'node', 'required', 'directories.json'))
    directories = json.loads(ifstream.read())
    ifstream.close()
    root = os.path.join(root, '.pakenode')
    os.mkdir(root)
    for name in directories: os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Creates empty pake config files in given root directory.
    Root defaults to home directory and should not be overridden
    unless for testing purposes.

    :param root: node root directory
    :type root: str
    """
    root = os.path.join(root, '.pakenode')
    config.node.Meta(root).reset().write()
    config.node.Nests(root).reset().write()
    config.node.Pushers(root).reset().write()
    config.network.Aliens(root).reset().write()


def remove(root):
    """Removes repository from root.
    """
    shutil.rmtree(os.path.join(root, '.pakenode'))
