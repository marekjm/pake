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
def gennode():
    """Generates a node in the test directory.
    """
    pake.node.manager.makedirs(testdir)
    pake.node.manager.makeconfig(testdir)


def prepare():
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
    gennode()
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


if __name__ == '__main__':
    prepare()
    unittest.main()
