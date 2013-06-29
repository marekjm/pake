#!/usr/bin/env python3

import ftplib
import json
import os
import shutil


from pake import errors
from pake import models


"""This modue is responsible for creating global pake repository and managing it.
It also provides interface to `meta.json` file -- which is metadata of the repository.
"""


def makedirs(root=''):
    """Creates node directory structure in given root.
    If the .pakenode directory is already in root it will be deleted and
    new one will be created.

    :param root: root directory in which files will be written
    :type root: str
    """
    root = os.path.join(root, '.pakenode')
    subdirectories = [  'db',
                        'downloaded',
                        'installing',
                        'prepared',
                        'packages',
                        ]
    os.mkdir(root)
    for name in subdirectories:
        os.mkdir(os.path.join(root, name))


def makeconfig(root=''):
    """Creates empty pake config files in given root directory.
    Root defaults to home directory and should not be overridden
    unless for testing purposes.

    :param root: root directory in which files will be written
    :type root: str
    """
    root = os.path.join(root, '.pakenode')
    Meta(root).reset()
    Mirrors(root).reset()
    Pushers(root).reset()
    Nodes(root).reset()
    Installed(root).reset()
    Packages(root).reset()


def pushmain(root, username, password, cwd='', installed=False, fallback=False, callback=None):
    """Pushes to main node.
    """
    upload(root, Meta(root).get('push-url'), username, password, cwd, installed, fallback, callback)

def pushmirrors(root, username, password, cwd, installed=False, fallback=False, callback=None):
    """Pushes to mirrors.
    """
    for mirror in Mirrors(root):
        upload(root, mirror['push-url'], username, password, mirror['cwd'], installed, fallback, callback)


def upload(root, node, username, password, cwd='', installed=False, fallback=False, callback=None):
    """Uploads node to a main URL.
    """
    remote = ftplib.FTP(node)
    remote.login(username, password)
    if cwd: remote.cwd(cwd)
    files = ['meta.json', 'packages.json', 'nodes.json', 'mirrors.json']
    if installed: files.append('installed.json')
    for name in files:
        try:
            if fallback: remote.rename(name, 'fallback.{0}'.format(name))
            else: remote.delete(name)
        except ftplib.error_perm:
            pass
        finally:
            remote.storbinary('STOR {0}'.format(name), open(os.path.join(root, name), 'rb'), callback=callback)
    if 'packages' not in [name for name, data in list(remote.mlsd())]: remote.mkd('packages')
    remote.cwd('./packages')
    packages = os.listdir(os.path.join(root, 'packages'))
    for pack in packages:
        if pack not in [name for name, data in list(remote.mlsd())]: remote.mkd(pack)
        remote.cwd(pack)
        contents = os.listdir(os.path.join(root, 'packages', pack))
        try:
            if fallback: remote.rename('meta.json', 'fallback.meta.json')
            else: remote.delete('meta.json')
        except ftplib.error_perm:
            pass
        finally:
            for item in contents:
                if item not in remote.mlsd():
                    remote.storbinary('STOR {}'.format(item), open(os.path.join(root, 'packages', pack, item), 'rb'))
        remote.cwd('..')
    remote.close()



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
    default = {'author':'', 'contact':'', 'description':'', 'url':'', 'push-url':''}
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
        required = [key for key in self.default]
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
        if index > -1: self.content.pop(index)
        self.write()


class NodePusher(Config):
    """Interface to push.json file.
    """
    name = 'push.json'
    default = {'url': '', 'push-url': '', 'cwd': ''}
    content = {}

    def __setitem__(self, key, value):
        self.content[key] = value
        self.write()


class Pushers(Config):
    """Interface to pushers.json file.
    """
    name = 'pushers.json'
    default = []
    content = []

    def __list__(self):
        return self.content

    def add(self, url, push_url, cwd=''):
        """Adds pusher to push.json list.
        """
        pusher = {'url': url, 'push-url': push_url, 'cwd': cwd}
        if pusher not in self.content:
            self.content.append(pusher)
            self.write()

    def remove(self, url):
        """Removes URL from list of pushers.
        """
        index = -1
        for i, mirrot in enumerate(self.content):
            if mirror == url:
                index = i
                break
        if index > -1: self.content.pop(index)
        self.write()


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
