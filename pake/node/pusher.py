#!/usr/bin/env python3

"""File used for pushing local node to its mirrors.
"""


import ftplib
import json
import os
import warnings

from pake import config


def _uploadconfig(root, remote):
    """Uploads configuration files.

    :param remote: is a ftplib.FTP object capable of storing files
    """
    files = ['meta.json', 'packages.json', 'aliens.json', 'mirrors.json']
    for name in files:
        ifstream = open(os.path.join(root, name), 'rb')
        remote.storbinary('STOR {0}'.format(name), ifstream, callback=None)
        ifstream.close()


def _uploadpackages(root, remote):
    """Uploads packages.

    :param remote: is a ftplib.FTP object capable of storing files
    """
    for name in ['packages', 'cache']:
        if name not in [name for name, data in list(remote.mlsd())]: remote.mkd(name)
    #if 'packages' not in [name for name in list(remote.nlst())]: remote.mkd('packages')
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
    warnings.warn(NotImplemented)


def _upload(root, host, username, password, cwd=''):
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
    _uploadconfig(root, remote)
    _uploadpackages(root, remote)
    remote.close()


def push(root, url, username, password):
    """Pushes node to remote server.

    :param root: node root directory
    :param url: URL of a mirror from which data should be taken
    :param username: username for the server
    :param password: password for the server
    """
    pusher = config.node.Pushers(root).get(url)
    if pusher is None: raise Exception('no pusher found for URL: {0}'.format(url))
    host = pusher['host']
    cwd = pusher['cwd']
    _upload(root, host=host, username=username, password=password, cwd=cwd)


def genmirrorlist(root):
    """Generates mirror list from pusher.json file.
    The mirror list is stored on server (pushers.json is not).
    """
    pushers = config.node.Pushers(root)
    ofstream = open(os.path.join(root, 'mirrors.json'), 'w')
    ofstream.write(json.dumps(pushers.geturls()))
    ofstream.close()
