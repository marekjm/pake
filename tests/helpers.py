#!/usr/bin/env python3

"""Helper methods for PAKE test suite.
"""


import os
import shutil


import pake

from tests import conf


def prepare(testdir):
    """Prepares test environment.
    """
    test_node_root = os.path.join(testdir, '.pakenode')
    test_nest_root = os.path.join(testdir, '.pakenest')
    if not os.path.isdir(testdir):
        print('* creating test directory: {0}'.format(testdir))
        os.mkdir(testdir)
    if os.path.isdir(test_node_root):
        print('* removing leftover test node: {0}'.format(test_node_root))
        shutil.rmtree(conf.test_node_root)
    if os.path.isdir(conf.test_nest_root):
        print('* removing old test nest: {0}'.format(conf.test_nest_root))
        shutil.rmtree(conf.test_nest_root)
    print()  # line break between prepare()'s output and test suite output


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


def buildTestPackage(path, version='0.2.4.8', files=['./pake/__init__.py', './pake/shared.py'],
        directories=[{'path': './ui/', 'recursive': True, 'avoid': ['__pycache__'], 'avoid_exts': ['swp', 'pyc']}]):
    """Builds test package.
    Returns version of built package.

    Directories param requires explanation.
    It is a list of directories given as dictionaries:

        {
            'path': './path/to/directory',
            'recursive': True/False,
            'avoid': [list, of, patterns, to, avoid],
            'avoid_exts': [list, of, file, extensions, to, avoid]
        }

    Only 'path' key is obligatory.

    :param path: path to root of the nest (with .pakenest part)
    :param version: version of the package
    :param files: list of files to add
    :param directories: list of dictionaries with directories
    """
    pake.config.nest.Meta(path).set('name', 'test').write()
    for i in files: pake.nest.package.addfile(path, i)
    for i in directories: pake.nest.package.adddir(path, **i)
    pake.nest.package.build(root=path, version=version)
    return version
