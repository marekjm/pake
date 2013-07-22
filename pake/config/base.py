#!/usr/bin/env python3


"""Module containing shared code for all config files interfaces.
"""


import json
import os


class Config():
    """Base object for config files interfaces.
    It exposes basic API: functionality for reading from and
    writing to files.
    """
    name = 'base.json'
    default = {}
    content = {}

    def __init__(self, root):
        self.root = root
        self.read()

    def __contains__(self, key):
        return key in self.content

    def __getitem__(self, item):
        return self.content[item]

    def __iter__(self):
        return iter(self.content)

    def reset(self):
        """Resets config file to it's default value.
        """
        self.content = self.default
        self.write()

    def read(self):
        """Reads JSON from config file.
        """
        try:
            ifstream = open(os.path.join(self.root, self.name))
            content = json.loads(ifstream.read())
            ifstream.close()
        except FileNotFoundError:
            content = self.default
        finally:
            self.content = content

    def write(self, root='', pretty=False):
        """Stores changes made to config file.

        :param pretty: enable pretty formating of JSON
        :param path: path to the root
        """
        if not root: root = self.root
        ofstream = open(os.path.join(root, self.name), 'w')
        if pretty: encoded = json.dumps(self.content, sort_keys=True, indent=4, separators=(',', ': '))
        else: encoded = json.dumps(self.content)
        ofstream.write(encoded)
        ofstream.close()


class Meta(Config):
    """Object representing some metadata.
    Values are added, removed or overwritten immediately after
    calling the right method (it means 'when you remove something we write
    new version to the file immediately, so be careful').

    The only thing needed when creating `meta.json` interface based on this object
    is overwrite of `default` field.
    """
    name = 'meta.json'
    default = {}
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

    def missing(self):
        """Returns list of missing or unset but required keys in meta.json file.
        """
        missing = []
        required = list(self.default.keys())
        for i in required:
            if i not in self.content or self.content[i] == '': missing.append(i)
        return missing
