#!/usr/bin/env python3

"""This file holds responsibility for managing alien nodes
registered in current network.
"""

import json
import os
import urllib.request
import warnings

from pake import config
from pake import shared


def fetchalien(url):
    """Fetches data from alien node and creates a dictionary of it.

    :param url: URL to alien root, e.g.: http://pake.example.com/node (without last slash)
    """
    alien = {}
    for name in ['meta', 'mirrors']: alien[name] = shared.fetchjson(url='{0}/{1}.json'.format(url, name))
    return alien


def add(root, url):
    """Adds alien node to the list of aliens.json.
    If given url is not of the alien's main node it will be changed.

    :param root: node root directory
    :type root: str
    :param url: URL of the alien node
    :type url: str

    :returns: dictionary containing fetched alien data
    """
    alien = fetchalien(url)
    if url in alien['mirrors']: url = alien['meta']['url']
    config.node.Aliens(root).set(url=url, mirrors=alien['mirrors'], meta=alien['meta']).write()
    return alien
