#!/usr/bin/env python3

"""This is PAKE system test suite.
"""


import json
import os
import shutil
import unittest


import pake


from tests import helpers


# Test flags
VERBOSE = True

# Test variables
testdir = './testdir'
test_node_root = testdir + '/.pakenode'
test_nest_root = testdir + '/.pakenest'


# Test environment setup
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


def prepare(testdir):
    """Prepares test environment.
    """
    if not os.path.isdir(testdir):
        print('* creating test directory: {0}'.format(testdir))
        os.mkdir(testdir)
    if os.path.isdir(test_node_root):
        print('* removing old test node: {0}'.format(test_node_root))
        shutil.rmtree(test_node_root)
    if os.path.isdir(test_nest_root):
        print('* removing old test nest: {0}'.format(test_nest_root))
        shutil.rmtree(test_nest_root)
    print('* generating new node...')
    gennode(testdir)
    print('* generating new nest...')
    gennest(testdir)
    print()  # line break between prepare()'s output and test suite output


class NodeManagerTests(unittest.TestCase):
    def testNodeManagerDirectoriesWriting(self):
        """This test checks for correct initialization of all required directories.
        """
        ifstream = open('./env/node/required/directories.json')
        directories = json.loads(ifstream.read())
        ifstream.close()
        self.assertIn('.pakenode', os.listdir(testdir))
        for d in directories:
            path = os.path.join(test_node_root, d)
            self.assertEqual(True, os.path.isdir(path))

    def testNodeManagerConfigWriting(self):
        """This test checks for correct intialization of all required config files.
        """
        # (filename, desired_content)
        configs = [ ('meta.json', {}),
                    ('pushers.json', []),
                    ('aliens.json', {}),
                    ('nests.json', {}),
                    ]
        self.assertIn('.pakenode', os.listdir(testdir))
        for f, desired in configs:
            path = os.path.join(test_node_root, f)
            ifstream = open(path, 'r')
            self.assertEqual(desired, json.loads(ifstream.read()))
            ifstream.close()

    def testNodeManagerRemovingNode(self):
        """This test checks if node gets correctly deleted.
        """
        pake.node.manager.remove(root=testdir)
        self.assertNotIn('.pakenode', os.listdir(testdir))


class NestManagerTests(unittest.TestCase):
    def testNestManagerDirectoriesWriting(self):
        """This test checks for correct initialization of all required directories.
        """
        ifstream = open('./env/nest/required/directories.json')
        directories = json.loads(ifstream.read())
        ifstream.close()
        if VERBOSE: print()
        for d in directories:
            path = os.path.join(test_nest_root, d)
            if VERBOSE: print("'{0}'".format(path))
            self.assertEqual(True, os.path.isdir(path))

    def testNestManagerConfigWriting(self):
        """This test checks for correct intialization of all required config files.
        """
        # (filename, desired_content)
        configs = [ ('meta.json', {}),
                    ('versions.json', []),
                    ('dependencies.json', {}),
                    ('files.json', []),
                    ]
        if VERBOSE: print()
        for f, desired in configs:
            path = os.path.join(test_nest_root, f)
            if VERBOSE: print("'{0}'".format(path))
            ifstream = open(path, 'r')
            self.assertEqual(desired, json.loads(ifstream.read()))
            ifstream.close()

    def testNestManagerRemovingNode(self):
        """This test checks if node gets correctly deleted.
        """
        pake.nest.manager.remove(root=testdir)
        self.assertNotIn('.pakenest', os.listdir(testdir))




if __name__ == '__main__':
    prepare(testdir)
    unittest.main()
