#!/usr/bin/env python3

"""Functions shared between modules of pake/aliens.
"""


import json
import urllib


def fetchjson(url, name):
    """Fetches data from alien node and creates a dictionary of it.

    :param url: url from which to fetch data
    :param name: actual file name
    """
    resource = '{0}/{1}'.format(url, name)
    socket = urllib.request.urlopen(resource)
    fetched = json.loads(str(socket.read(), encoding='utf-8'))
    socket.close()
    return fetched
