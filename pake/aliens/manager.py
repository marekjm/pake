#!/usr/bin/env python3

"""This file holds responsibility for managing alien nodes
registered in current network.
"""

import json
import os
import urllib.request
import warnings

from pake import config


def fetchalien(url):
    """Fetches data from alien node and creates a dictionary of it.
    """
    alien = {}
    for name in ['meta', 'mirrors']:
        resource = '{0}/{1}.json'.format(url, name)
        socket = urllib.request.urlopen(resource)
        alien[name] = json.loads(str(socket.read(), encoding='utf-8'))
        socket.close()
    return alien


def add(root, url):
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
