#!/usr/bin/env python3


import json
import os
import shutil
import unittest

import pake


# Global variables
test_node_root = pake.shared.getnodepath(check=False, fake=os.path.abspath('./testdir'))
test_nest_root = pake.shared.getnestpath(check=False, fake=os.path.abspath('./testdir'))


# Test environment setup
if os.path.isdir(test_node_root):
    print('- removing old test node root...')
    shutil.rmtree(test_node_root)
if os.path.isdir(test_nest_root):
    print('- removing old test nest root...')
    shutil.rmtree(test_nest_root)

print('+ creating new test node root...')
pake.node.local.manager.makedirs(root=test_node_root)
pake.node.local.manager.makeconfig(root=test_node_root)

print('+ creating new test nest root...')
pake.nest.manager.makedirs(root=test_nest_root)
pake.nest.manager.makeconfig(root=test_nest_root)

print('\nSuccessfully created test environment in {0}'.format(os.path.abspath('./testdir')))
print()  # to make a one-line break between setup messages and actual test messages


class NodeInitializationTests(unittest.TestCase):
    def testDirectoriesWriting(self):
        """This test checks for correct initialization of all required directories.
        """
        ifstream = open('./env/node/required/directories.json')
        directories = json.loads(ifstream.read())
        ifstream.close()
        print()
        for d in directories:
            path = os.path.join(test_node_root, d)
            print("'{0}'".format(path))
            self.assertEqual(True, os.path.isdir(path))

    def testConfigWriting(self):
        """This test checks for correct intialization of all required config files.
        """
        # (filename, desired_content)
        configs = [ ('meta.json', {}),
                    ('mirrors.json', []),
                    ('pushers.json', []),
                    ('aliens.json', {}),
                    ('packages.json', {}),
                    ('registered.json', {}),
                    ]
        print()
        for f, desired in configs:
            path = os.path.join(test_node_root, f)
            print("'{0}'".format(path))
            ifstream = open(path, 'r')
            self.assertEqual(desired, json.loads(ifstream.read()))
            ifstream.close()


class NestInitializationTests(unittest.TestCase):
    def testDirectoriesWriting(self):
        """This test checks for correct initialization of all required directories.
        """
        ifstream = open('./env/nest/required/directories.json')
        directories = json.loads(ifstream.read())
        ifstream.close()
        print()
        for d in directories:
            path = os.path.join(test_nest_root, d)
            print("'{0}'".format(path))
            self.assertEqual(True, os.path.isdir(path))

    def testConfigWriting(self):
        """This test checks for correct intialization of all required config files.
        """
        # (filename, desired_content)
        configs = [ ('meta.json', {}),
                    ('versions.json', []),
                    ('dependencies.json', {}),
                    ('files.json', []),
                    ]
        print()
        for f, desired in configs:
            path = os.path.join(test_nest_root, f)
            print("'{0}'".format(path))
            ifstream = open(path, 'r')
            self.assertEqual(desired, json.loads(ifstream.read()))
            ifstream.close()


class NodeConfigurationTests(unittest.TestCase):
    def testAddingKeyToMeta(self):
        pake.config.node.Meta(test_node_root).set('foo', 'bar').write()
        self.assertEqual(pake.config.node.Meta(test_node_root).get('foo'), 'bar')
        pake.config.node.Meta(test_node_root).reset().write()



if __name__ == '__main__': unittest.main()
