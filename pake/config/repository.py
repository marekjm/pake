#!/usr/bin/env python3


"""This module contains interfaces to repository configuration files.
As for PAKE version 0.0.7 these files are:

    *   `meta.json`:    contains basic metadata for the package.
"""


import json

from pake.config import base


class Meta(base.Meta):
    """Object representing repository metadata.

    It is invalid unless it contains following fields:
        * name: name of a package
        * version: semantic version string (preferred) or other type of version string

    It should contain:
        * license: license used for this package
        * author: authors name
        * description: description for the repository.
    """
    default = { 'name': '',
                'version': '0.0.0',
                'description': '',
                'author': '',
                'license': '',
                }


class Dependencies(base.Config):
    """Interface to package's `dependencies.json` file.

    Dependency is a dict describing a package (it's `meta.json`).
    """
    name = 'dependencies.json'
    default = []
    content = []

    def _getindex(self, name):
        """Returns index of the dependency.
        -1 means that there is no such dependecy on the list.
        """
        index = -1
        for i, d in enumerate(self.content):
            if d['name'] == name:
                index = i
                break
        return index

    def set(self, name, min='', max=''):
        """Sets a dependency for package.
        Dependecies cannot be duplicated which means that there can be
        only one entry `foo` on the dependencies list.
        If a dependency with given name is already found it will be updated.

        :param name: name of the package
        :param min: minimal version required
        :param max: maximal version allowed
        :returns: integer, -1 means new dependency else means an update
        """
        n = self._getindex(name)
        dependency = {  'name': name,
                        'min': min,
                        'max': max,
                        }
        if n == -1: self.content.append(dependency)
        else: self.content[n] = dependency
        self.write()
        return n

    def remove(self, name):
        """Removes a dependency.
        :returns: integer, -1 means that the dependency was not found
        """
        n = self._getindex(name)
        if n != -1:
            del self.content[n]
            self.write()
        return n
