#!/usr/bin/env python3

import json
import os
import shutil


"""This modue is responsible for creating global pake repository and managing it.
It also provides interface to `meta.json` file -- which is metadata of the repository.
"""


def makedirs(root):
    """Creates node directory structure in given root.
    If the .pakenode directory is already in root it will be deleted and
    new one will be created.

    :param root: root directory in which files will be written
    :type root: str
    """
    root = os.path.join(root, '.pakenode')
    subdirectories = [  'db',
                        'downloaded',
                        'installing',
                        'prepared',
                        'packages',
                        ]
    os.mkdir(root)
    for name in subdirectories:
        os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Creates empty pake config files in given root directory.
    Root defaults to home directory and should not be overridden
    unless for testing purposes.

    :param root: root directory in which files will be written
    :type root: str
    """
    root = os.path.join(root, '.pakenode')
    meta = open(os.path.join(root, 'meta.json'), 'w')
    meta.write(json.dumps({'author':'', 'contact':'', 'description':'', 'url':''}))
    meta.close()

    mirrors = open(os.path.join(root, 'mirrors.json'), 'w')
    mirrors.write(json.dumps([]))
    mirrors.close()

    packages = open(os.path.join(root, 'packages.json'), 'w')
    packages.write('[]')
    packages.close()

    remotes = open(os.path.join(root, 'remotes.json'), 'w')
    remotes.write('[]')
    remotes.close()

    installed = open(os.path.join(root, 'installed.json'), 'w')
    installed.write('[]')
    installed.close()


def setup(root):
    """Runs node setup process in given root directory.
    Unless you are testing the software root MUST be user's
    home directory.
    """
    makedirs(root)
    makeconfig(root)


class Config():
    """Base object for config files.
    Provides functionality for reading and writing these files.
    """
    name = 'blank.json'
    content = None

    def __init__(self, root):
        self.root = root
        self.read()

    def __contains__(self, key):
        return key in self.content

    def __iter__(self):
        return iter(self.content)

    def read(self):
        """Reads JSON from config file.
        """
        ifstream = open(os.path.join(self.root, self.name))
        self.content = json.loads(ifstream.read())
        ifstream.close()

    def write(self):
        """Stores changes made to config file.
        """
        ofstream = open(os.path.join(self.root, self.name), 'w')
        ofstream.write(json.dumps(self.content))
        ofstream.close()


class Meta(Config):
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
    are then strongly encouraged to read RELEASE.markdown files for each release to
    make yourself informed about wheter some filed did or did not gain any
    meaning.

    Thank you for your cooperation.
    """
    name = 'meta.json'
    content = {}

    def set(self, key, value):
        """Sets key in metadata.
        """
        self.content[key] = value
        self.write()

    def get(self, key):
        """Returns a value from metadata.
        """
        return self.content[key]

    def remove(self, key):
        """Removes key from metadata.
        """
        del self.content[key]
        self.write()


class Mirrors(Config):
    name = 'mirrors.json'

    def add(self, url):
        """Adds URL to mirrors list.
        Will create duplicates.
        """
        if url not in self.content:
            self.content.append(url)
            self.write()

    def remove(self, url):
        """Removes URL from list of mirrors.
        """
        self.content.remove(url)
        self.write()
