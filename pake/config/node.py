#!/usr/bin/env python3


"""This module contains interfaces to node configuration files.
As for PAKE version 0.0.7 these files are:

    *   `meta.json`:        contains basic metadata for the node,
    *   `mirrors.json`:     list of mirrors for user's node,
    *   `pushers.json`:     list of pushers for every mirror of user's node,
    *   `nodes.json`:       list of known other nodes,
    *   `installed.json`:   list of all installed packages with brief
                            information about their status,
    *   `packages.json`:    list of packages this node provides.

"""


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
    default = {'author':'', 'contact':'', 'description':'', 'url':''}


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
        if url not in self.content:
            self.content.append(url)
            self.write()

    def remove(self, url):
        """Removes URL from list of mirrors.
        """
        index = -1
        for i, mirrot in enumerate(self.content):
            if mirror == url:
                index = i
                break
        if index > -1:
            self.content.pop(index)
            self.write()
        return index


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

    def hasurl(self, url):
        """Returns True if pushers.json already has pusher with given url.
        """
        result = False
        for p in self:
            if p['url'] == url:
                result = True
                break
        return result

    def add(self, url, push_url, cwd=''):
        """Adds pusher to push.json list.
        """
        pusher = {'url': url, 'push-url': push_url, 'cwd': cwd}
        if pusher not in self.content:
            self.content.append(pusher)
            self.write()


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
        """Removes URL from list of pushers.
        """
        index = -1
        for i, mirrot in enumerate(self.content):
            if mirror == url:
                index = i
                break
        if index > -1:
            self.content.pop(index)
            self.write()
        return index


class Nodes(base.Config):
    """Interface to nodes.json file.
    """
    name = 'nodes.json'
    default = []
    content = []

    def __list__(self):
        return self.content

    def __contains__(self, url):
        """Checks if nodes.json file contain node of given URL.

        :param node: URL of the node
        :type node: str
        """
        result = False
        for i in self.content:
            if i['url'] == url:
                result = True
                break
        return result

    def add(self, node):
        """Adds new node.
        Duplicates are checked by comparing URLs.
        If you want to update node metadata use update() method.
        """
        if type(node) is not models.Node: raise TypeError('expected {0} but got: {1}'.format(models.Node, type(node)))
        if node['url'] not in self and node.valid(): self.content.append(dict(node))
        elif node['url'] in self and node.valid(): raise DuplicateError('cannot duplicate node')
        else: raise NodeError('node is not valid: missing keys: {0}'.format(', '.join(self.missing(node))))
        self.write()


class Installed(base.Config):
    """Interface to installed.json file.
    """
    name = 'installed.json'
    default = []
    content = []

    def __contains__(self, package):
        """Checks if given package is installed.
        """
        result = False
        if type(package) is str: package = {'name': package}
        for i in self.content:
            if package['name'] == i['name']:
                result = True
                break
        return result

    def add(self, package, dependency=False):
        """Appends package to list of installed packages.

        :param dependency: whether package was installed independently or as a dependency
        """
        package['dependency'] = dependency
        index = -1
        for i in self.content:
            if package['name'] == i['name']:
                index = i
                break
        if index == -1: self.content.append(package)
        else: self.content[index] = package
        self.write()


class Packages(Installed):
    """Interface to packages.json file.
    """
    name = 'packages.json'

    def add(self, package):
        """Adds pakcge to the list of provided packages.
        """
