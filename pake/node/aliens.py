#!/usr/bin/env python3


"""This moduel holds functionality for dealing with aliens (nodes which
are not mirrors of the local node).
"""


import json
import urllib.request
import warnings

from pake import config


def add(root, url):
    """Adds new node to network.
    Would not add duplictes.
    """
    socket = urllib.request.urlopen('{0}/mirrors.json'.format(url))
    mirrors = json.loads(str(socket.read(), encoding='utf-8'))
    socket.close()
    print(url, mirrors)
    config.node.Aliens(root).set(url, mirrors)
