#!/usr/bin/env python3

"""Helper methods for PAKE test suite.
"""


import os


import pake


def gennode(path):
    """Generates a node in the test directory.
    """
    pake.node.manager.makedirs(path)
    pake.node.manager.makeconfig(path)


def rmnode(path):
    """Removes node from path.
    """
    pake.node.manager.remove(path)


def gennest(path):
    """Initialize nest in given path.
    """
    pake.nest.manager.makedirs(root=path)
    pake.nest.manager.makeconfig(root=path)


def rmnest(path):
    """Removes nest from given path.
    """
    pake.nest.manager.remove(root=path)
