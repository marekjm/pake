#!/usr/bin/env python3


"""Module containing shared code for all config files interfaces.
"""


import json
import os
import warnings


class Config():
    """Base object for config files interfaces.
    It exposes basic API: functionality for reading from and
    writing to files.

    This base config object can be modified in-place but also
    provides a fluent API which is in some cases much more useful.
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

    def __list__(self):
        return list(self.content)

    def reset(self):
        """Resets config file to it's default value.
        """
        self.content = self.default
        return self

    def read(self):
        """Reads JSON from config file.
        """
        reraise = False
        try:
            ifstream = open(os.path.join(self.root, self.name))
            content = json.loads(ifstream.read())
            ifstream.close()
        except FileNotFoundError:
            content = self.default
        except ValueError as e:
            warnings.warn(e)
            print('the content read was:')
            print(content)
            content = self.default
        except (Exception) as e:
            # set reraise flag to True so any exception that is not handled before will be reraised
            reraise = e
        finally:
            if reraise: raise reraise
            self.content = content
        return self

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
        return self


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
        """Sets key in metadata. Part of PAKE fluent API.
        """
        self.content[key] = value
        return self

    def remove(self, key):
        """Removes key from metadata. Part of PAKE fluent API.
        """
        del self.content[key]
        return self

    def get(self, key):
        """Returns a value from metadata.
        """
        return self.content[key]

    def keys(self):
        """Returns dict_keys list of keys contained in meta.json file.
        """
        return self.content.keys()
