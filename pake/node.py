#!/usr/bin/env python3


"""This module is responsible for creating global pake repository and managing it.
It also provides interface to `meta.json` file -- which is metadata of the repository.
"""


import ftplib
import urllib.request
import os
import shutil
import json


from pake import config


def makedirs(root):
    """Creates node directory structure in given root.
    If the .pakenode directory is already in root it will be deleted and
    new one will be created.

    :param root: root directory in which files will be written
    :type root: str
    """
    subdirectories = ['db',
                      'downloaded',
                      'installing',
                      'prepared',
                      'packages',
                      ]
    os.mkdir(root)
    for name in subdirectories:
        os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Creates empty pake config files in given root directory.
    Root defaults to home directory and should not be overridden
    unless for testing purposes.

    :param root: root directory in which files will be written
    :type root: str
    """
    config.node.Meta(root).reset()
    config.node.Mirrors(root).reset()
    config.node.Pushers(root).reset()
    config.node.Nodes(root).reset()
    config.node.Installed(root).reset()
    config.node.Packages(root).reset()
    config.node.Registered(root).reset()


def push(root, url, username, password, cwd='', installed=False, fallback=False, callback=None):
    """Uploads node data to given url.
    """
    remote = ftplib.FTP(url)
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


def pushurl(root, url, username, password, installed=False, fallback=False):
    """Pushes node to remote server.

    :param root: root directory for config files
    :param url: URL of a mirror from which data should be taken
    :param username: username for the server (not needed if stored)
    :param password: password for the server (not needed if stored)
    :param installed: push also `installed.json` file, disabled by default
    :param fallback: create fallback files (fallback.*.json)
    """
    pusher = config.node.Pushers(root).get(url)
    if pusher is None: raise Exception('no pusher found for URL: {0}'.format(url))
    url = pusher['push-url']
    cwd = pusher['cwd']
    push(root, url=url, username=username, password=password, cwd=cwd, installed=installed, fallback=fallback)


def registerrepo(root, repository):
    """Register PAKE repository in the node. This will allow to
    push the package provided to the Net.

    :param root: root of your node
    :param repository: root of the repository being registered
    """
    meta = config.repository.Meta(repository)
    if 'name' not in meta or 'version' not in meta:
        raise Exception('invalid `meta.json` file for repository: {0}'.format(repository))
    name = meta.get('name')
    config.node.Registered(root).add(name, repository)
    config.node.Packages(root).add()
    package_dir = os.path.join(root, 'packages', name)
    os.mkdir(package_dir)
    meta.write(package_dir)
    config.repository.Dependencies(repository).write(package_dir)


def removerepo(root, name, directory=False):
    """Removes previously registared repository.
    """
    config.node.Registered(root).add(name)
    if directory: shutil.rmtree(os.path.join(root, 'packages', name))


def setnode(root, url):
    """Adds new node to network.
    Would not add duplictes.
    """
    socket = urllib.request.urlopen('{0}/mirrors.json'.format(url))
    mirrors = json.loads(str(socket.read(), encoding='utf-8'))
    socket.close()
    print(url, mirrors)
    config.node.Nodes(root).set(url, mirrors)
