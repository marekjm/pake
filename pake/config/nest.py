#!/usr/bin/env python3


"""This module contains interfaces to nest configuration files.
"""

import os

# pyversion can be found at: https://github.com/marekjm/pyversion
import pyversion

from . import base
from .. import errors


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

    def add(self, version, check=False, strict=True):
        """Adds new version to a list of versions.

        :param version: version string to append
        :type version: semver version string
        :param check: decide whether to check if last known version isn't greater than the one we want to add
        :type check: bool
        :param strict: whether to use strict semver strings or not (non-strict allow to use more than three digit-words in base version)
        :type strict: bool
        """
        if version not in self.content:
            if check and pyversion.version.Version(self[-1], strict=strict) > pyversion.version.Version(version, strict=strict):
                raise ValueError('{0} is lesser version then the last present: {1}'.format(version, self[-1]))
            self.content.append(version)
        return self

    def remove(self, version):
        """Remove version from the list (it will not be visible to outer network).

        :param version: version string to remove
        """
        if version in self: self.content.remove(version)
        return self


class Dependencies(base.Config):
    """Interface to package's `dependencies.json` file.

    Dependency is a dict describing a package (it's `meta.json`).
    """
    name = 'dependencies.json'
    default = {}
    content = {}

    def set(self, name, origin='', min='', max=''):
        """Sets a dependency for package.
        Dependecies cannot be duplicated which means that there can be
        only one entry `foo` on the dependencies list.
        If a dependency with given name is already found it will be updated.

        :param name: name of the package
        :type name: str
        :param origin: URL of node of origin
        :type origin: str
        :param min: minimal required version
        :type min: semver-based str
        :param max: maximal allowed version
        :type max: semver-based str
        """
        dep = {}
        if origin: dep['origin'] = origin
        if min: dep['min'] = min
        if max: dep['max'] = max
        self.content[name] = dep
        return self

    def update(self, name, origin='', min='', max=''):
        """Updated data on given dependency.
        Every information that is not updated is copied from old dependency.
        If the dependency is not found in a list of dependencies
        empty dictionary is used and
        new dependency will be added.

        :param name: name of the package
        :type name: str
        :param origin: URL of node of origin
        :type origin: str
        :param min: minimal required version
        :type min: semver-based str
        :param max: maximal allowed version
        :type max: semver-based str
        """
        if name in self: dep = self[name]
        else: dep = {}
        if origin: dep['origin'] = origin
        if min: dep['min'] = min
        if max: dep['max'] = max
        self.content[name] = dep
        return self

    def remove(self, name):
        """Removes a dependency.
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

    def add(self, path):
        """Adds file to the list.
        """
        if not os.path.isfile(path): raise errors.NotAFileError(path)
        for i in self:
            if os.path.abspath(path) == os.path.abspath(i): raise FileExistsError('file already added: {0}'.format(path))
        self.content.append(path)
        return self

    def remove(self, path):
        """Removes file from the list.
        """
        self.content.remove(path)
        return self
