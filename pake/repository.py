#!/usr/bin/env python3

import json
import os
import shutil

from pake import config
from pake import errors


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
    subdirectories = [  'versions',
                        ]
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
