#!/usr/bin/env python3

"""Backend for managing local node.

It contains methods required to:
*   intialize a node,
*   pushing node to the mirrors.
"""


import ftplib
import os
import shutil
import warnings

from pake import config


node_directories = ['db',
                    'downloaded',
                    'installing',
                    'prepared',
                    'packages',
                    ]


config_objects = [  config.node.Meta,
                    config.node.Mirrors,
                    config.node.Pushers,
                    config.node.Aliens,
                    config.node.Installed,
                    config.node.Packages,
                    config.node.Registered,
                    ]


def makedirs(root):
    """Creates node directory structure in given root.
    If the .pakenode directory is already in root it will be deleted and
    new one will be created.

    :param root: parent directory of the node directory
    :type root: str
    """
    root = os.path.join(root, '.pakenode')
    os.mkdir(root)
    for name in node_directories: os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Creates empty pake config files in given root directory.
    Root defaults to home directory and should not be overridden
    unless for testing purposes.

    :param root: parent directory of the node directory
    :type root: str
    """
    root = os.path.join(root, '.pakenode')
    for o in confg_objects: o(root).reset()


def remove(root):
    """Removes repository from root.
    """
    root = os.path.join(root, '.pakenode')
    shutil.rmtree(root)


def _push(root, url, username, password, cwd='', installed=False, fallback=False, callback=None):
    """Uploads node data to given url.
    """
    remote = ftplib.FTP(url)
    remote.login(username, password)
    if cwd: remote.cwd(cwd)
    files = ['meta.json', 'packages.json', 'aliens.json', 'mirrors.json']
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

    :param root: parent directory of the node directory
    :param url: URL of a mirror from which data should be taken
    :param username: username for the server (not needed if stored)
    :param password: password for the server (not needed if stored)
    :param installed: push also `installed.json` file, disabled by default
    :param fallback: create fallback files (fallback.*.json)
    """
    root = os.path.join(root, '.pakenode')
    pusher = config.node.Pushers(root).get(url)
    if pusher is None: raise Exception('no pusher found for URL: {0}'.format(url))
    url = pusher['push-url']
    cwd = pusher['cwd']
    _push(root, url=url, username=username, password=password, cwd=cwd, installed=installed, fallback=fallback)


def addalien(root, url):
    """Adds alien node to the list of aliens.json.

    :param root: parent directory of the node directory
    :type root: str
    :param url: URL of the alien node
    :type url: str
    """
    pass
