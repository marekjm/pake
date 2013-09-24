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
        """Adds URL to mirrors list if it's not already there.
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
        Why URL? Because it has to be unique. Hostname and cwd can be the same for several URLs.

        :returns: index of removed mirror, -1 means that no pusher was removed
        """
        index = self._getindex(url)
        if index > -1: del self.content[index]
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
        return self.all()

    def __contains__(self, url):
        """Checks if nodes.json file contain node of given URL.
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

    def urls(self):
        """Return list of alien URLs registered in node's network.
        """
        return list(self.content.keys())

    def all(self):
        """Return list of all alien nodes.
        """
        aliens = []
        for u in self.urls():
            # ad -- single "alien dictionary"
            ad = {'url': u}
            d = self.get(u)
            ad['mirrors'] = d['mirrors']
            ad['meta'] = d['meta']
            aliens.append(ad)
        return aliens


class Packages(base.Config):
    """Interface to packages.json file.

    Packages in this file are visible to users who added you to their aliens list.
    It is basically a list of names of all available packages.

    **Notice:** this object is designed to be reset and rebuilt each time it's sent to
    server. Hence, only .append() method is available and not .remove(), .get() etc.
    """
    name = 'packages.json'
    default = []
    content = []

    def append(self, name, latest):
        """Appends package to the list of provided packages. Part of PAKE fluent API.
        Name is removed from metadata before storing it.

        :param name: name of the package
        :type name: str
        :param latest: most recent version fo the package
        :type latest: str
        """
        self.content.append((name, latest))
        return self

    def names(self):
        """Return names of all packages.
        """
        return [name for name, version in self.content]


class Nests(base.Config):
    """This is a list of registered nests.
    A nest is a directory on your local machine containing
    files for a package.
    """
    name = 'nests.json'
    default = {}
    content = {}

    def set(self, name, path):
        """Registers a nest.

        :param name: name of a package
        :param path: path to the nest
        """
        self.content[name] = path
        return self

    def remove(self, name):
        """Removes a name from the list of registered nests.

        :param name: name of a package whose nest to remove
        """
        del self.content[name]
        return self

    def get(self, name):
        """Returns path to the nest.

        :param name: name of the package
        """
        return self.content[name]

    def paths(self):
        """Returns list of paths to all nests.
        """
        return [self.get(k) for k in self]
