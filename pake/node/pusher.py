#!/usr/bin/env python3

"""File used for pushing local node to its mirrors.
"""


import ftplib
import json
import os
import warnings

from pake import config


def _uploadconfig(root, remote):
    """Uploads configuration files from ~/.pakenode to the
    root of a mirror. Root of a mirror is set by "cwd" field in pusher.

    :param remote: is a ftplib.FTP object capable of storing files
    :param root: root of the node
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
    print('+ pake: debug: switching to "packages" directory')
    remote.cwd('./packages')
    pkgs = config.node.Nests(root)
    for name in pkgs:
        print('+ pake: debug: uploading: {0}'.format(name))
        if name not in [name for name, data in list(remote.mlsd())]:
            print('+ pake: debug: creating "{0}" directory'.format(name))
            remote.mkd(name)
        print('+ pake: debug: switching to "{0}" directory'.format(name))
        remote.cwd('./{0}'.format(name))
        ifstream = open(os.path.join(pkgs.get(name), 'versions.json'), 'rb')
        remote.storbinary('STOR {0}'.format('versions.json'), ifstream, callback=None)
        ifstream.close()
        print('+ pake: debug: uploaded "versions.json" file')
        if 'versions' not in [name for name, data in list(remote.mlsd())]:
            print('+ pake: debug: creating "versions" directory'.format(name))
            remote.mkd('versions')
        print('+ pake: debug: switching to "versions" directory'.format(name))
        remote.cwd('./versions')
        versions = config.nest.Versions(pkgs.get(name))
        for v in versions:
            if v not in [name for name, data in list(remote.mlsd())]:
                print('+ pake: debug: creating "versions/{0}" directory'.format(v))
                remote.mkd(v)
        print('+ pake: debug: uploaded: {0}'.format(name))
        print(remote.pwd())
        remote.cwd('../../')
        print('+ pake: debug: returning to main package directory...')
        print(remote.pwd())


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
