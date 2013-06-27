import json
import urllib.request

"""This module contains models shared between various elements of pake.
"""


class Node():
    """Object representing a remote node.
    """
    meta = {}

    def __init__(self, url='', meta={}):
        if url: meta['url'] = url
        self.meta = meta

    def __contains__(self, key):
        return key in self.meta

    def __get__(self, key):
        return self.meta[key]
    
    def fetch(self):
        """This method tries to fetch node metadata from it's url.
        """
        socket = urllib.request.urlopen('{0}/meta.json'.format(self.meta['url']))
        meta = str(socket.read(), encoding='utf-8')
        socket.close()
        self.meta = json.loads(meta)

    def valid(self):
        """Checks if node's metadata contains all required fields.
        """
        return self.missing() == []

    def missing(self):
        """Returns list of missing keys.
        """
        missing = []
        required = ['author', 'url', 'contact', 'mirrors']
        for key in required:
            if key not in self: missing.append(key)
        return missing
 

class Package():
    """Object representing a package.
    """
    meta = {}

    def __init__(self, meta):
        self.meta = meta

    def missing(self, package):
        """Returns list of required kesy missing from package's meta.
        """
        missing = []
        required = ['name', 'version', 'url', 'dependencies']
        for i in required:
            if i not in package: missing.append(i)
        return missing

    def valid(self):
        """Returns True if package metadata is valid.
        """
        return self.missing() == []
