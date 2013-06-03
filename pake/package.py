#!/usr/bin/env python3

import json
import os
import shutil

from pake import repository


"""This module contains objects responsible for:
    * creating new package-repos (repos for single package, not located in users home dir),
    * creating package directories in main repo,
    * managing package metadata,

    * building package archives,
    * installing packages archives,
    * removing packages archives,
"""


def init(name, root):
    """Initializes new package repo and package subdir in main repo.
    Root directory of main repo is the directory in which `.pake` subdir is
    located.

    :param name: name of package
    :type name: str
    :param root: absolute path to the root directory for main repo
    :type root: str
    """
    root = os.path.abspath(os.path.join(root, '.pake'))
    packdir = os.path.join(root, 'packages', name)
    curr = os.path.abspath(os.path.join('.', '.pake'))

    os.mkdir(curr)
    os.mkdir(packdir)


def setconfig(name, root):
    """Initializes empty package config in ocal repo and
    package subdir in main repo.
    Root directory of main repo is the directory in which `.pake` subdir is
    located.

    :param name: name of package
    :type name: str
    :param root: absolute path to the root directory for main repo
    :type root: str
    """
    empty = {   'name': name,
                'version': '0.0.0',
                'description': '',
                'author': repository.Meta().get('author'),
                'license': 'GNU GPL v3+ / GNU GPL v2+',
                'url': repository.Meta.get('url'),
                'mirrors': repository.Meta.get('mirrors'),
                'dependencies': [],
                }
    meta = open(os.path.join(curr, 'meta.json'), 'w')
    meta.write(json.dumps(empty))
    meta.close()
    shutil.copy(os.path.join(curr, 'meta.json'), os.path.join(root, '{0}.json'.format(name)))
