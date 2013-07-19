#!/usr/bin/env python3

import json


class Config():
    """Base object for config files.
    Provides functionality for reading and writing these files.
    """
    name = 'blank.json'
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
        content = self.default
        try:
            ifstream = open(os.path.join(self.root, self.name))
            content = json.loads(ifstream.read())
            ifstream.close()
        except FileNotFoundError:
            pass
        finally:
            self.content = content

    def write(self):
        """Stores changes made to config file.
        """
        ofstream = open(os.path.join(self.root, self.name), 'w')
        ofstream.write(json.dumps(self.content))
        ofstream.close()


class Meta(Config):
    """Object representing repository metadata.
    Values are added, removed or overwritten immediately after
    calling the right method (it means 'when you remove something we write
    new version of meta to the file immediately, so be careful').

    Fields listed here are (marked `*`) or will be (marked `+`)
    supported by the `pake` and have special meaning.

    `meta.json` file HAS TO contain:
        * name: name of repository (regexp: '[0-9A-Za-z]+([_-][0-9A-Za-z]+)*')
        * url: url to repository
        * author: authors name

    `meta.json` file SHOULD contain:
        * mirrors: list of mirrors in case the main `url` is not working,
        * description: description for the repository.

    Other fields have no special meaning but may gain it in future.
    Although you can add some self-describing fileds to your `meta.json` you
    are then strongly encouraged to read RELEASE.markdown files for each release to
    make yourself informed about wheter some filed did or did not gain any
    meaning.

    Thank you for your cooperation.
    """
    name = 'meta.json'
    default = {'author':'', 'contact':'', 'description':'', 'url':''}
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
        required = list( self.default.keys())
        for i in required:
            if i not in self.content: missing.append(i)
            elif i in self.content and self.content[i] == '': missing.append('{} (empty)'.format(i))
        return missing


class Mirrors(Config):
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


class Pushers(Config):
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


class Nodes(Config):
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


class Installed(Config):
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

    def add(self, package):
        """Appends package to list of installed packages.
        """
        if type(package) is not models.Package: raise TypeError('expected {0} but got: {1}'.format(dict, type(package)))
        if not package.valid(): raise PackageError('meta.json: missing keys: {}'.format(', '.join(package.missing())))
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
