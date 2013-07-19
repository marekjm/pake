import json
import urllib
import warnings

"""This module contains models shared between various elements of pake.
"""


class Remote():
    """Object representing a remote node.
    """
    url = ''
    meta = {}
    packages = []
    nodes = []

    def __init__(self, url, meta={}):
        if url: meta['url'] = url
        self.url = url
        self.meta = meta

    def __contains__(self, key):
        return key in self.meta

    def __get__(self, key):
        return self.meta[key]

    def _fetchjson(self, name, url=''):
        """Tries to fetch file from the node.
        If the main file is not available it will try to fetch
        fallback file.

        :param name: file name without .json extension
        """
        if not url: url = self.url
        resource = '{0}/{1}.json'.format(url, name)
        fallback = '{0}/fallback.{1}.json'.format(url, name)
        try:
            socket = urllib.request.urlopen(resource)
        except (urllib.error.URLError):
            socket = urllib.request.urlopen(fallback)
        finally:
            data = str(socket.read(), encoding='utf-8')
            socket.close()
        return json.loads(data)

    def _fetchmeta(self):
        """Tries to fetch meta.json from the node.
        """
        return self._fetchjson('meta')

    def _fetchmirrors(self):
        """Tries to fetch mirrors.json from the node.
        """
        return self._fetchjson('mirrors')

    def _fetchnodes(self):
        """Tries to fetch nodes.json file from the node.
        """
        return self._fetchjson('nodes')

    def _fetchpackages(self):
        """Tries to fetch packages.json from the node.
        """
        return self._fetchjson('packages')
  
    def fetch(self):
        """Tries to fetch node metadata from it's url.
        """
        meta = self._fetchmeta()
        meta['mirrors'] = self._fetchmirrors()
        self.meta = meta
        self.packages = self._fetchpackages()
        self.nodes = self._fetchnodes()

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
