#!/usr/bin/env python3


"""This moduel holds functionality for dealing with aliens (nodes which
are not mirrors of the local node).
"""


import json
import os
import urllib.request
import warnings

from pake import config


def add(root, url):
    """Adds new node to network.
    Would not add duplictes.

    :param root: directory in which root node is located
    :param url: url to the alien node
    :returns: tuple -- (url, mirros of this url)
    """
    socket = urllib.request.urlopen('{0}/mirrors.json'.format(url))
    mirrors = json.loads(str(socket.read(), encoding='utf-8'))
    socket.close()
    config.node.Aliens(root).set(url, mirrors)
    return (url, mirrors)


def remove(root, url):
    """This will remove alien URL from aliens.json.
    """
    config.nodes.Aliens(root).remove(url, mirrors)
