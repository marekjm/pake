#!/usr/bin/env python3

"""This is PAKE nest manager module. It provides functions to create and
remove a nest.
"""

import json
import os
import shutil

from pake import config, shared


def makedirs(root):
    """Creates new PAKE nest.

    :param root: root of the nest
    :type root: str
    """
    ifstream = open(os.path.join(shared.getenvpath(), 'nest', 'required', 'directories.json'))
    directories = json.loads(ifstream.read())
    ifstream.close()
    os.mkdir(root)
    for name in directories: os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Initializes empty PAKE nest.

    :param root: root for the nest
    :type root: str
    """
    config.nest.Versions(root).reset().write()
    config.nest.Dependencies(root).reset().write()
    config.nest.Files(root).reset().write()
    config.nest.Meta(root).reset().write()


def remove(root):
    """Removes nest.
    """
    shutil.rmtree(root)
