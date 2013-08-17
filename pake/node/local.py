#!/usr/bin/env python3

"""Backend for managing local node.

It contains methods required to:
*   intialize a node,
*   pushing node to the mirrors.
"""


import ftplib
import os
import shutil
import urllib.request
import warnings

import json

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
                    #config.node.Installed,
                    config.node.Packages,
                    config.node.Registered,
                    ]


def makedirs(root):
    """Creates node directory structure in given root.
    If the .pakenode directory is already in root it will be deleted and
    new one will be created.

    :param root: node root directory
    :type root: str
    """
    os.mkdir(root)
    for name in node_directories: os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Creates empty pake config files in given root directory.
    Root defaults to home directory and should not be overridden
    unless for testing purposes.

    :param root: node root directory
    :type root: str
    """
    for o in config_objects: o(root).reset()


def remove(root):
    """Removes repository from root.
    """
    shutil.rmtree(root)


def _uploadconfig(root, remote, installed=False):
    """Uploads configuration files.

    :param remote: is a ftplib.FTP object capable of storing files
    """
    files = ['meta.json', 'packages.json', 'aliens.json', 'mirrors.json']
    if installed: files.append('installed.json')
    for name in files:
        """
        try:
            remote.delete(name)
        except ftplib.error_perm:
            pass
        finally:
            remote.storbinary('STOR {0}'.format(name), open(os.path.join(root, name), 'rb'), callback=None)
        """
        remote.storbinary('STOR {0}'.format(name), open(os.path.join(root, name), 'rb'), callback=None)


def _uploadpackages(root, remote):
    """Uploads packages.

    :param remote: is a ftplib.FTP object capable of storing files
    """
    if 'packages' not in [name for name, data in list(remote.mlsd())]: remote.mkd('packages')
    """
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
    """


def _upload(root, host, username, password, cwd='', installed=False):
    """Uploads node data to given host.
    
    :root: root directory of the local node
    :host: url of host server
    :username: FTP server username
    :passowrd: FTP password
    :cwd: directory to which PAKE will go after logging in
    """
    remote = ftplib.FTP(host)
    remote.login(username, password)
    if cwd: remote.cwd(cwd)
    _uploadconfig(root, remote, installed=installed)
    _uploadpackages(root, remote)
    remote.close()


def push(root, url, username, password, installed):
    """Pushes node to remote server.

    :param root: node root directory
    :param url: URL of a mirror from which data should be taken
    :param username: username for the server (not needed if stored)
    :param password: password for the server (not needed if stored)
    """
    pusher = config.node.Pushers(root).get(url)
    if pusher is None: raise Exception('no pusher found for URL: {0}'.format(url))
    host = pusher['host']
    cwd = pusher['cwd']
    _upload(root, host=host, username=username, password=password, cwd=cwd)


def _fetchalien(url):
    """Fetches data from alien node and creates a dictionary of it.
    """
    alien = {}
    for name in ['meta', 'mirrors']:
        resource = '{0}/{1}.json'.format(url, name)
        socket = urllib.request.urlopen(resource)
        alien[name] = json.loads(str(socket.read(), encoding='utf-8'))
        socket.close()
    return alien


def addalien(root, url):
    """Adds alien node to the list of aliens.json.
    If given url is not of the alien's main node it will be changed.

    :param root: node root directory
    :type root: str
    :param url: URL of the alien node
    :type url: str

    :returns: main url
    """
    alien = _fetchalien(url)
    if url in alien['mirrors']: url = alien['meta']['url']
    config.node.Aliens(root).set(url, alien)
    return url
