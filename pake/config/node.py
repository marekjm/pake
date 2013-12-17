#!/usr/bin/env python3


"""This module contains interfaces to node configuration files.
"""


from . import base


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

    def set(self, url, host, cwd=''):
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

    def geturls(self):
        """Returns list of URLs of all pushers which
        is, basically, a list of mirrors.
        """
        return [pusher['url'] for pusher in self.content]


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

    def remove(self, what, by='name'):
        """Removes a nest from the list of registered nests.

        :param what: name of a package whose nest to remove OR path of the nest to rmeove
        :param by: 'name' or 'path'
        """
        if by == 'name': pass
        elif by == 'path':
            for k in self:
                if self[k] == what:
                    what = k
                    break
        else:
            raise ArgumentError('by can be either "name" or "path": cannot remove by "{0}"'.format(by))
        del self.content[what]
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

    def names(self):
        """Returns names of registered nests.
        """
        return [k for k in self]
