#!/usr/bin/env python3

"""File used to manage local node.
"""

import json
import os
import shutil
import warnings

from pake import config, shared


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
    os.mkdir(root)
    for name in directories: os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Creates empty pake config files in given root directory.
    Root defaults to home directory and should not be overridden
    unless for testing purposes.

    :param root: node root directory
    :type root: str
    """
    config.node.Meta(root).reset().write()
    config.node.Mirrors(root).reset().write()
    config.node.Pushers(root).reset().write()
    config.node.Aliens(root).reset().write()
    # commented because I'm not sure how to
    # implement this functionality
    #config.node.Installed(root).reset().write()
    config.node.Packages(root).reset().write()
    config.node.Registered(root).reset().write()


def remove(root):
    """Removes repository from root.
    """
    shutil.rmtree(root)
