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
def prepare(testdir):
    """Prepares test environment.
    """
    if not os.path.isdir(testdir):
        print('* creating test directory: {0}'.format(testdir))
        os.mkdir(testdir)
    if os.path.isdir(test_node_root):
        print('* removing leftover test node: {0}'.format(test_node_root))
        shutil.rmtree(test_node_root)
    if os.path.isdir(test_nest_root):
        print('* removing old test nest: {0}'.format(test_nest_root))
        shutil.rmtree(test_nest_root)
    print()  # line break between prepare()'s output and test suite output


# Node related tests
class NodeManagerTests(unittest.TestCase):
    def testNodeManagerDirectoriesWriting(self):
        """This test checks for correct initialization of all required directories.
        """
        # preparation
        helpers.gennode(testdir)
        ifstream = open('./env/node/required/directories.json')
        directories = json.loads(ifstream.read())
        ifstream.close()
        # test logic
        self.assertIn('.pakenode', os.listdir(testdir))
        for d in directories:
            path = os.path.join(test_node_root, d)
            self.assertEqual(True, os.path.isdir(path))
        # cleanup
        helpers.rmnode(testdir)

    def testNodeManagerConfigWriting(self):
        """This test checks for correct intialization of all required config files.
        """
        # preparation
        helpers.gennode(testdir)
        configs = [ ('meta.json', {}),      # (filename, desired_content)
                    ('pushers.json', []),
                    ('aliens.json', {}),
                    ('nests.json', {}),
                    ]
        # test logic
        self.assertIn('.pakenode', os.listdir(testdir))
        for f, desired in configs:
            path = os.path.join(test_node_root, f)
            ifstream = open(path, 'r')
            self.assertEqual(desired, json.loads(ifstream.read()))
            ifstream.close()
        # cleanup
        helpers.rmnode(testdir)

    def testNodeManagerRemovingNode(self):
        """This test checks if node gets correctly deleted.
        """
        # preparation
        helpers.gennode(testdir)
        # code logic & cleanup - in this test it's the same
        pake.node.manager.remove(root=testdir)
        self.assertNotIn('.pakenode', os.listdir(testdir))


class NodeConfigurationTests(unittest.TestCase):
    """Code for Meta() is shared between node and
    nest configuration interface so it's only tested here.

    Any tests passing for node will also pass for nests.
    """
    def testSettingKeyInMeta(self):
        helpers.gennode(testdir)
        # test logic
        pake.config.node.Meta(test_node_root).set('foo', 'bar').write()
        self.assertEqual(pake.config.node.Meta(test_node_root).get('foo'), 'bar')
        pake.config.node.Meta(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testRemovingKeyFromMeta(self):
        helpers.gennode(testdir)
        # test logic
        pake.config.node.Meta(test_node_root).set('foo', 'bar').write().remove('foo').write()
        self.assertEqual(dict(pake.config.node.Meta(test_node_root)), {})
        # cleanup
        helpers.rmnode(testdir)

    def testGettingMetaKeys(self):
        helpers.gennode(testdir)
        # test logic
        pake.config.node.Meta(test_node_root).set('foo', 0).set('bar', 1).set('baz', 2).write()
        self.assertEqual(['bar', 'baz', 'foo'], sorted(pake.config.node.Meta(test_node_root).keys()))
        pake.config.node.Meta(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testAddingPusher(self):
        helpers.gennode(testdir)
        # test logic
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).add(**pusher).write()
        self.assertIn(pusher, pake.config.node.Pushers(test_node_root))
        pake.config.node.Pushers(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testRemovingPusher(self):
        helpers.gennode(testdir)
        # test logic
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).add(**pusher).write()
        pake.config.node.Pushers(test_node_root).remove(url='http://pake.example.com').write()
        self.assertNotIn(pusher, pake.config.node.Pushers(test_node_root))
        # cleanup
        helpers.rmnode(testdir)

    def testGettingPusher(self):
        helpers.gennode(testdir)
        # test logic
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).add(**pusher).write()
        self.assertEqual(pusher, pake.config.node.Pushers(test_node_root).get(url='http://pake.example.com'))
        pake.config.node.Pushers(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testCheckingForURLInPushers(self):
        helpers.gennode(testdir)
        # test logic
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).add(**pusher).write()
        self.assertEqual(True, pake.config.node.Pushers(test_node_root).hasurl('http://pake.example.com'))
        pake.config.node.Pushers(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testAddingAlien(self):
        helpers.gennode(testdir)
        # test logic
        alien = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        pake.config.node.Aliens(test_node_root).set(**alien).write()
        self.assertIn('http://alien.example.com', pake.config.node.Aliens(test_node_root))
        pake.config.node.Aliens(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testRemovingAlien(self):
        helpers.gennode(testdir)
        # test logic
        alien = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        pake.config.node.Aliens(test_node_root).set(**alien).write()
        pake.config.node.Aliens(test_node_root).remove(alien['url']).write()
        self.assertNotIn('http://alien.example.com', pake.config.node.Aliens(test_node_root))
        # cleanup
        helpers.rmnode(testdir)

    def testGettingAlien(self):
        helpers.gennode(testdir)
        # test logic
        alien = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        pake.config.node.Aliens(test_node_root).set(**alien).write()
        del alien['url']
        self.assertEqual(alien, pake.config.node.Aliens(test_node_root).get('http://alien.example.com'))
        pake.config.node.Aliens(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testListingAlienURLs(self):
        helpers.gennode(testdir)
        # test logic
        foo = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        bar = {'url': 'http://alien.example.net', 'mirrors': [], 'meta': {}}
        baz = {'url': 'http://alien.example.org', 'mirrors': [], 'meta': {}}
        pake.config.node.Aliens(test_node_root).set(**foo).set(**bar).set(**baz).write()
        self.assertEqual(['http://alien.example.com', 'http://alien.example.net', 'http://alien.example.org'],
                             sorted(pake.config.node.Aliens(test_node_root).urls()))
        pake.config.node.Aliens(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testListingAliens(self):
        helpers.gennode(testdir)
        # test logic
        foo = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        bar = {'url': 'http://alien.example.net', 'mirrors': [], 'meta': {}}
        baz = {'url': 'http://alien.example.org', 'mirrors': [], 'meta': {}}
        pake.config.node.Aliens(test_node_root).set(**foo).set(**bar).set(**baz).write()
        aliens = pake.config.node.Aliens(test_node_root).all()
        self.assertIn(foo, aliens)
        pake.config.node.Aliens(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testSettingNests(self):
        helpers.gennode(testdir)
        # test logic
        pake.config.node.Nests(root=test_node_root).set('foo', './testdir/.pakenest').write()
        self.assertEqual('./testdir/.pakenest', pake.config.node.Nests(test_node_root).get('foo'))
        pake.config.node.Nests(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testRemovingNests(self):
        helpers.gennode(testdir)
        # test logic
        nest = {'name': 'foo', 'path': '~/Dev/foo'}
        pake.config.node.Nests(test_node_root).set(**nest).write()
        pake.config.node.Nests(test_node_root).remove('foo').write()
        self.assertRaises(KeyError, pake.config.node.Nests(test_node_root).get, 'foo')
        pake.config.node.Nests(test_node_root).reset().write()
         # cleanup
        helpers.rmnode(testdir)

    def testGettingPathOfOneNest(self):
        helpers.gennode(testdir)
        # test logic
        foo = {'name': 'foo', 'path': '~/Dev/foo'}
        bar = {'name': 'bar', 'path': '~/Dev/bar'}
        baz = {'name': 'baz', 'path': '~/Dev/baz'}
        pake.config.node.Nests(test_node_root).set(**foo).set(**bar).set(**baz).write()
        self.assertEqual('~/Dev/foo', pake.config.node.Nests(test_node_root).get('foo'))
        self.assertEqual('~/Dev/bar', pake.config.node.Nests(test_node_root).get('bar'))
        self.assertEqual('~/Dev/baz', pake.config.node.Nests(test_node_root).get('baz'))
        pake.config.node.Nests(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testGettingPathsOfAllNests(self):
        helpers.gennode(testdir)
        # test logic
        foo = {'name': 'foo', 'path': '~/Dev/foo'}
        bar = {'name': 'bar', 'path': '~/Dev/bar'}
        baz = {'name': 'baz', 'path': '~/Dev/baz'}
        pake.config.node.Nests(test_node_root).set(**foo).set(**bar).set(**baz).write()
        self.assertEqual(['~/Dev/bar', '~/Dev/baz', '~/Dev/foo'], sorted(pake.config.node.Nests(test_node_root).paths()))
        pake.config.node.Nests(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)


# Nest related tests
class NestManagerTests(unittest.TestCase):
    def testNestManagerDirectoriesWriting(self):
        """This test checks for correct initialization of all required directories.
        """
        # preparation
        helpers.gennest(testdir)
        ifstream = open('./env/nest/required/directories.json')
        directories = json.loads(ifstream.read())
        ifstream.close()
        # test logic
        if VERBOSE: print()
        for d in directories:
            path = os.path.join(test_nest_root, d)
            if VERBOSE: print("'{0}'".format(path))
            self.assertEqual(True, os.path.isdir(path))
        # cleanup
        helpers.rmnest(testdir)

    def testNestManagerConfigWriting(self):
        """This test checks for correct intialization of all required config files.
        """
        # preparation
        helpers.gennest(testdir)
        # (filename, desired_content)
        configs = [ ('meta.json', {}),
                    ('versions.json', []),
                    ('dependencies.json', {}),
                    ('files.json', []),
                    ]
        # test logic
        if VERBOSE: print()
        for f, desired in configs:
            path = os.path.join(test_nest_root, f)
            if VERBOSE: print("'{0}'".format(path))
            ifstream = open(path, 'r')
            self.assertEqual(desired, json.loads(ifstream.read()))
            ifstream.close()
        # cleanup
        helpers.rmnest(testdir)

    def testNestManagerRemovingNode(self):
        """This test checks if node gets correctly deleted.
        """
        # preparation
        helpers.gennest(testdir)
        # test logic & cleanup
        pake.nest.manager.remove(root=testdir)
        self.assertNotIn('.pakenest', os.listdir(testdir))


if __name__ == '__main__':
    prepare(testdir)
    unittest.main()
