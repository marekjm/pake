#!/usr/bin/env python3

"""This is file implementing node discovery feature used to
expand the network.
"""


import json
import warnings

from pake.aliens import shared as alshared
from pake import shared
from pake import config


def crawl(root):
    """Not implemented.
    """
    warnings.warn(NotImplemented)
    aliens = config.node.Aliens(shared.getnodepath(check=True))
