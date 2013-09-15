#!/usr/bin/env python3


"""This module contains interfaces to nest configuration files.
"""


from pake.config import base


class Meta(base.Meta):
    """Object representing package metadata.

    It is invalid unless it contains following fields:
        * name:     name of a package
        * version:  semantic version string (preferred) or other type of version string
        * license:  license used for this package
        * origin:   original node from which the package can be downloaded

    It should contain:
        * author: authors name
        * description: description for the repository.
    """
    pass


class Versions(base.Config):
    """Interface to a list of versions file.
    """
    name = 'versions.json'
    default = []
    content = []

    def add(self, version):
        """Adds new version to a list of versions.
        """
        if version not in self.content: self.content.append(version)
        return self


class Dependencies(base.Config):
    """Interface to package's `dependencies.json` file.

    Dependency is a dict describing a package (it's `meta.json`).
    """
    name = 'dependencies.json'
    default = {}
    content = {}

    def set(self, name, dependency):
        """Sets a dependency for package.
        Dependecies cannot be duplicated which means that there can be
        only one entry `foo` on the dependencies list.
        If a dependency with given name is already found it will be updated.

        :param name: name of the package
        :param dependency: dictionary containing dependency specification
        """
        self.content[name] = dependency
        return self

    def remove(self, name):
        """Removes a dependency.
        :returns: integer, -1 means that the dependency was not found
        """
        del self.content[name]
        return self

    def get(self, name):
        """Returns dependency dict.
        """
        return self.content[name]


class Files(base.Config):
    """Interface to package's `files.json` config file.
    """
    name = 'files.json'
    default = []
    content = []

    def add(self, string):
        """Adds file to the list.
        """
        if string not in self.content: self.content.append(string)
        return self

    def remove(self, string):
        """Removes file from the list.
        """
        self.content.remove(string)
        return self
