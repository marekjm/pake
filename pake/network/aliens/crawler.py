#!/usr/bin/env python3

"""This is file implementing node discovery feature used to
expand the network.
"""


import warnings

from pake import config
from pake import shared


def crawl(root):
    """Not implemented.
    """
    warnings.warn(NotImplemented)
    aliens = config.node.Aliens(shared.getnodepath(check=True))
    for a in aliens: pass
