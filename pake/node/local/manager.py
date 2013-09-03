#!/usr/bin/env python3

"""File used to manage local node.
"""

import os
import shutil
import warnings

from pake import config


node_directories = ['db',
                    'cache',
                    'installing',
                    'prepared',
                    ]


config_objects = [  config.node.Meta,
                    config.node.Mirrors,
                    config.node.Pushers,
                    config.node.Aliens,
                    #config.node.Installed,
                    config.node.Packages,
                    config.node.Registered,
                    ]


def makedirs(root):
    """Creates node directory structure in given root.
    If the .pakenode directory is already in root it will be deleted and
    new one will be created.

    :param root: node root directory
    :type root: str
    """
    os.mkdir(root)
    for name in node_directories: os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Creates empty pake config files in given root directory.
    Root defaults to home directory and should not be overridden
    unless for testing purposes.

    :param root: node root directory
    :type root: str
    """
    for o in config_objects: o(root).reset()


def remove(root):
    """Removes repository from root.
    """
    shutil.rmtree(root)
