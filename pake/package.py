#!/usr/bin/env python3

import json
import os
import shutil

from pake import node


"""This module contains objects responsible for:
    * creating new package-repos (repos for single package, not located in users home dir),
    * creating package directories in main repo,
    * managing package metadata,

    * building package archives,
    * installing packages archives,
    * removing packages archives,
"""


def init(root):
    """Initializes new package repo and package subdir in main repo.
    Root directory of main repo is the directory in which `.pakenode` subdir is
    located.

    :param name: name of package
    :type name: str
    :param root: absolute path to the root directory for main repo
    :type root: str
    """
    root = os.path.abspath(os.path.join(root, '.pake'))
    if os.path.isdir(root): shutil.rmtree(root)
    os.mkdir(root)


def register(name):
    """Registers the package in node.
    """
    pass


def setconfig(root, name):
    """Initializes empty package config in ocal repo and
    package subdir in main repo.
    Root directory of main repo is the directory in which `.pake` subdir is
    located.

    :param name: name of package
    :type name: str
    :param root: absolute path to the root directory for main repo
    :type root: str
    """
    root = os.path.join(root, '.pake')
    empty = {   'name': name,
                'version': '0.0.0',
                'description': '',
                'author': node.Meta().get('author'),
                'license': 'GNU GPL v3+ / GNU GPL v2+',
                'url': node.Meta.get('url'),
                'mirrors': node.Meta.get('mirrors'),
                'dependencies': [],
                }
    meta = open(os.path.join(root, 'meta.json'), 'w')
    meta.write(json.dumps(empty))
    meta.close()
