#!/usr/bin/env python3


"""This module contains interfaces to node configuration files.
"""


import warnings

from pake.config import base


class Meta(base.Meta):
    """Object representing node metadata.

    It is invalid unless it contains following fields:
        * author: name of the author of the node,
        * contact: contact information (email, jabber, Diaspora* handle, GitHub username etc.)
        * url: URL of the main mirror,

    It should contain:
        * description: description of this node.

    """
    pass


class Mirrors(base.Config):
    """Interface to mirrors.json file.
    """
    name = 'mirrors.json'
    default = []
    content = []

    def __iter__(self):
        return iter(self.content)

    def __list__(self):
        return self.content

    def add(self, url):
        """Adds URL to mirrors list.
        Will create duplicates.
        """
        if url not in self.content: self.content.append(url)
        return self

    def remove(self, url):
        """Removes URL from list of mirrors.
        """
        if url in self.content: self.content.remove(url)
        return self


class Pushers(base.Config):
    """Interface to pushers.json file.
    """
    name = 'pushers.json'
    default = []
    content = []

    def __iter__(self):
        return iter(self.content)

    def __list__(self):
        return self.content

    def _getindex(self, url):
        """Returns index of a pusher.
        -1 means that pusher was not found.

        :param url: it is unique URL of a mirror, NOT A push-url
        """
        index = -1
        for i, pusher in enumerate(self.content):
            if pusher['url'] == url:
                index = i
                break
        return index

    def hasurl(self, url):
        """Returns True if pushers.json already has pusher with given url.
        """
        result = False
        for p in self:
            if p['url'] == url:
                result = True
                break
        return result

    def add(self, url, host, cwd=''):
        """Adds pusher to push.json list. Part of PAKE fluent API.
        """
        pusher = {'url': url, 'host': host, 'cwd': cwd}
        if pusher not in self.content: self.content.append(pusher)
        return self

    def get(self, url):
        """Returns pusher for given URL.
        Returns None if not found.
        """
        pusher = None
        for p in self:
            if p['url'] == url:
                pusher = p
                break
        return pusher

    def remove(self, url):
        """Removes URL from list of pushers. Part of PAKE fluent API.

        :returns: index of removed mirror, -1 means that no pusher was removed
        """
        index = self._getindex(url)
        if index > -1:
            del self.content[index]
        return self


class Aliens(base.Config):
    """Interface to aliens.json file.

    Alien dictionary:
        {
            "meta": {},     # metadata about the alien (/meta.json)
            "mirrors": []   # mirrorlist (/mirrors.json)
        }
    """
    name = 'aliens.json'
    default = {}
    content = {}

    def __list__(self):
        return list(self.content.keys())

    def __contains__(self, url):
        """Checks if nodes.json file contain node of given URL.

        :param node: URL of the node
        :type node: str
        """
        result = False
        for i in self.content:
            if i == url:
                result = True
            else:
                for mirror in self.content[i]:
                    if mirror == url:
                        result = True
                        break
            if result: break
        return result

    def set(self, url, mirrors, meta):
        """Sets node in your list of nodes.
        If a node with given URL already exists it's data is overwritten.
        Part of PAKE fluent API.
        """
        self.content[url] = {'mirrors': mirrors, 'meta': meta}
        return self

    def remove(self, url):
        """Removes alien from the dictionary. Part of PAKE fluent API.
        """
        del self.content[url]
        return self

    def get(self, url):
        """Returns alien dictionary.
        """
        return self.content[url]


class Packages(base.Config):
    """Interface to packages.json file.
    """
    name = 'packages.json'
    default = {}
    content = {}

    def set(self, meta):
        """Adds package to the list of provided packages. Part of PAKE fluent API.
        """
        self.content[meta['name']] = meta
        return self

    def remove(self, name):
        """Removes package
        """
        del self.content[name]
        return self

    def get(self, name):
        """Returns package metadata stored in packages.json.
        """
        return self.content[name]


class Registered(base.Config):
    """This is a list of registered repositories.
    A repository is a directory on your local machine containing
    files for a package.
    """
    name = 'registered.json'
    default = {}
    content = {}

    def set(self, name, path):
        """Registers a repository.
        """
        self.content[name] = path
        return self

    def getpath(self, name):
        """Returns path to the repository.
        """
        return self.content[name]

    def remove(self, name):
        """Removes a repository.
        """
        del self.content[name]
        return self
