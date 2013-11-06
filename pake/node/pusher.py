#!/usr/bin/env python3

"""File used for pushing local node to its mirrors.
"""


import ftplib
import json
import os
import warnings

from pake import config


class FTPPusher(ftplib.FTP):
    """Wrapper around ftplib's FTP object.
    """
    def sendlines(self, path):
        """Send file as lines.
        File is sent to the current working directory set in remote.

        :param path: path to a file to be sent
        """
        ifstream = open(path, 'rb')
        self.storlines('STOR {0}'.format(os.path.split(path)[-1]), ifstream, callback=None)
        ifstream.close()
        return self

    def sendbinary(self, path):
        """Send file as binary.
        File is sent to the current working directory set in remote.

        :param path: path to a file to be sent
        """
        ifstream = open(path, 'rb')
        self.storbinary('STOR {0}'.format(os.path.split(path)[-1]), ifstream, callback=None)
        ifstream.close()
        return self

    def ls(self, directory='.'):
        """Returns directory listing.
        Although .nlst() method is deprecated some servers (VSFTPd for example) don't accept
        .mlsd(). In such situations this method issues a warning and falls back to .nlst().
        Returns a list of strings.
        """
        listing = []
        try:
            listing = [name for name, data in self.mlsd(directory)]
        except ftplib.error_perm as e:
            warnings.warn('\'{0}\' was returned by .mlsd(): trying to use deprecated .nlst()'.format(e))
            listing = self.nlst(directory)
        finally:
            return listing


# Class methods
def _uploadconfig(root, remote):
    """Uploads configuration files from ~/.pakenode to the
    root of a mirror. Root of a mirror is set by "cwd" field in pusher.

    :param remote: is a ftplib.FTP object capable of storing files
    :param root: root of the node
    """
    files = ['meta.json', 'packages.json', 'aliens.json', 'mirrors.json']
    for name in files: remote.sendlines(path=os.path.join(root, name))


def _uploadpackages(root, remote, reupload=False):
    """Uploads packages.

    :param remote: is a ftplib.FTP object capable of storing files
    """
    for name in ['packages', 'cache']:
        if name not in remote.ls(): remote.mkd(name)
    remote.cwd('./packages')
    pkgs = config.node.Nests(root)
    for name in pkgs:
        print('+ pake: debug: uploading: {0}'.format(name))
        if name not in remote.ls():
            print('+ pake: debug: creating "{0}" directory'.format(name))
            remote.mkd(name)
        print('+ pake: debug: switching to "{0}" directory'.format(name))
        remote.cwd('./{0}'.format(name))
        remote.sendlines(path=os.path.join(pkgs.get(name), 'versions.json'))
        print('+ pake: debug: uploaded "versions.json" file')
        if 'versions' not in remote.ls():
            print('+ pake: debug: creating "versions" directory'.format(name))
            remote.mkd('versions')
        print('+ pake: debug: switching to "versions" directory'.format(name))
        remote.cwd('./versions')
        versions = config.nest.Versions(pkgs.get(name))
        for v in versions:
            absent = v not in remote.ls()
            if absent or reupload:
                print('+ pake: debug: creating "versions/{0}" directory'.format(v))
                if absent: remote.mkd(v)
                remote.cwd(v)
                for conffile in ['meta.json', 'dependencies.json']:
                    print('+ pake: debug: uploading "{0}" for version {1}'.format(conffile, v))
                    remote.sendlines(path=os.path.join(pkgs.get(name), 'versions', v, conffile))
                print('+ pake: debug: uploading build for version {0}'.format(v))
                remote.sendbinary(path=os.path.join(pkgs.get(name), 'versions', v, 'build.tar.xz'))
        print('+ pake: debug: uploaded package: {0}'.format(name))
        remote.cwd('../../')
        print('+ pake: debug: returning to main package directory...')


def _upload(root, host, username, password, cwd='', reupload=False):
    """Uploads node data to given host.

    :root: root directory of the local node
    :host: url of host server
    :username: FTP server username
    :passowrd: FTP password
    :cwd: directory to which PAKE will go after logging in
    """
    remote = FTPPusher(host)
    remote.login(username, password)
    if cwd: remote.cwd(cwd)
    _uploadconfig(root, remote)
    _uploadpackages(root, remote, reupload=reupload)
    remote.close()


def push(root, url, username, password, reupload=False):
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
    _upload(root, host=host, username=username, password=password, cwd=cwd, reupload=reupload)


def genmirrorlist(root):
    """Generates mirror list from pusher.json file.
    The mirror list is stored on server (pushers.json is not).
    """
    pushers = config.node.Pushers(root)
    ofstream = open(os.path.join(root, 'mirrors.json'), 'w')
    ofstream.write(json.dumps(pushers.geturls()))
    ofstream.close()
