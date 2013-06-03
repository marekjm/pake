#!/usr/bin/env python3

import json
import os
import shutil
import warnings


"""This modue is responsible for creating global pake repository and managing it.
It also provides interface to `meta.json` file -- which is metadata of the repository.
"""


def init(root='~'):
    """Sets up main repository in given root.
    Root defaults to home directory and should not be overridden
    unless for testing purposes.

    :param root: root dir in which repo will be created
    :type root: str
    """
    root = os.path.join(os.path.abspath(os.path.expanduser(root)), '.pake')
    reinit = ''
    if os.path.isdir(root):
        shutil.rmtree(root)
        reinit = 're'
    os.mkdir(root)
    os.mkdir(os.path.join(root, 'packages'))
    print('pake: repository {0}initialized in {1}'.format(reinit, root))


def setconfig(root='~'):
    """Creates empty pake config files in given root directory.
    Root defaults to home directory and should not be overridden
    unless for testing purposes.

    :param root: root directory in which files will be written
    :type root: str
    """
    root = os.path.join(os.path.abspath(os.path.expanduser(root)), '.pake')
    meta = open(os.path.join(root, 'meta.json'), 'w')
    meta.write(json.dumps({'author':'', 'contact':'', 'description':'', 'url':'', 'mirrors':[]}))
    meta.close()

    packages = open(os.path.join(root, 'packages.json'), 'w')
    packages.write('[]')
    packages.close()

    remotes = open(os.path.join(root, 'remotes.json'), 'w')
    remotes.write('[]')
    remotes.close()

    installed = open(os.path.join(root, 'installed.json'), 'w')
    installed.write('[]')
    installed.close()


class Meta():
    """Object representing repository metadata.
    Values are added, removed or overwritten immediately after
    calling the right method (it means 'when you remove something we write
    new version of meta to the file immediately, so be careful').

    Fields listed here are (marked `*`) or will be (marked `+`)
    supported by the `pake` and have special meaning.

    `meta.json` file HAS TO contain:
        * name: name of repository (regexp: '[0-9A-Za-z]+([_-][0-9A-Za-z]+)*')
        * url: url to repository
        * author: authors name

    `meta.json` file SHOULD contain:
        * mirrors: list of mirrors in case the main `url` is not working,
        * description: description for the repository.

    Other fields have no special meaning but may gain it in future.
    Although you can add some self-describing fileds to your `meta.json` you
    are then strongly encouraged to read RELEASE.md files for each release to
    make yourself informed about wheter some filed did or did not gain any
    meaning.

    Thank you for your cooperation.
    """
    root = '~/.pake/'
    meta = {}

    def __init__(self, root=''):
        if root: self.root = root
        self.root = os.path.abspath(os.path.expanduser(self.root))
        self._read()

    def _read(self):
        """Reads meta JSON.
        """
        meta = open(os.path.join(self.root, 'meta.json'))
        self.meta = json.loads(meta.read())
        meta.close()

    def _write(self):
        """Stores changes made to metadata.
        """
        meta = open(os.path.join(self.root, 'meta.json'), 'w')
        meta.write(json.dumps(self.meta))
        meta.close()

    def set(self, key, value):
        """Sets key in metadata.
        """
        self.meta[key] = value
        self._write()

    def get(self, key):
        """Returns a value from metadata.
        """
        return self.meta[key]

    def remove(self, key):
        """Removes key from metadata.
        """
        del self.meta[key]
        self._write()
