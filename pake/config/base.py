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

    def write(self, pretty=False):
        """Stores changes made to config file.
        """
        ofstream = open(os.path.join(self.root, self.name), 'w')
        if pretty: encoded = json.dumps(self.content, sort_keys=True, indent=4, separators=(',', ': '))
        else: encoded = json.dumps(self.content)
        ofstream.write(encoded)
        ofstream.close()
