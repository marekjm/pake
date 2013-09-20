#!/usr/bin/env python3


import json
import os
import shutil
import unittest

import pake


# Flags
VERBOSE = False


# Global variables
test_node_root = pake.shared.getnodepath(check=False, fake=os.path.abspath('./testdir'))
test_nest_root = pake.shared.getnestpath(check=False, fake=os.path.abspath('./testdir'))


# Test environment setup
if os.path.isdir(test_node_root):
    print('- removing old test node root')
    shutil.rmtree(test_node_root)
if os.path.isdir(test_nest_root):
    print('- removing old test nest root')
    shutil.rmtree(test_nest_root)

print('+ creating new test node root')
pake.node.local.manager.makedirs(root=test_node_root)
pake.node.local.manager.makeconfig(root=test_node_root)

print('+ creating new test nest root')
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
        if VERBOSE: print()
        for d in directories:
            path = os.path.join(test_node_root, d)
            if VERBOSE: print("'{0}'".format(path))
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
                    ('nests.json', {}),
                    ]
        if VERBOSE: print()
        for f, desired in configs:
            path = os.path.join(test_node_root, f)
            if VERBOSE: print("'{0}'".format(path))
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
        if VERBOSE: print()
        for d in directories:
            path = os.path.join(test_nest_root, d)
            if VERBOSE: print("'{0}'".format(path))
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
        if VERBOSE: print()
        for f, desired in configs:
            path = os.path.join(test_nest_root, f)
            if VERBOSE: print("'{0}'".format(path))
            ifstream = open(path, 'r')
            self.assertEqual(desired, json.loads(ifstream.read()))
            ifstream.close()


class NodeConfigurationTests(unittest.TestCase):
    """Code for Meta() is shared between node and
    nest configuration interface so it's only tested here.

    Any tests passing for node will also pass for nests.
    """
    def testSettingKeyInMeta(self):
        pake.config.node.Meta(test_node_root).set('foo', 'bar').write()
        self.assertEqual(pake.config.node.Meta(test_node_root).get('foo'), 'bar')
        pake.config.node.Meta(test_node_root).reset().write()

    def testRemovingKeyFromMeta(self):
        pake.config.node.Meta(test_node_root).set('foo', 'bar').write().remove('foo').write()
        self.assertEqual(dict(pake.config.node.Meta(test_node_root)), {})

    def testGettingMetaKeys(self):
        pake.config.node.Meta(test_node_root).set('foo', 0).set('bar', 1).set('baz', 2).write()
        self.assertEqual(['bar', 'baz', 'foo'], sorted(pake.config.node.Meta(test_node_root).keys()))
        pake.config.node.Meta(test_node_root).reset().write()

    def testAddingMirror(self):
        pake.config.node.Mirrors(test_node_root).add('http://pake.example.com').write()
        self.assertEqual(['http://pake.example.com'], list(pake.config.node.Mirrors(test_node_root)))
        pake.config.node.Mirrors(test_node_root).reset().write()

    def testRemovingMirror(self):
        pake.config.node.Mirrors(test_node_root).add('http://pake.example.com').add('http://pake.example.net').add('http://pake.example.org').write()
        pake.config.node.Mirrors(test_node_root).remove('http://pake.example.net').write()
        self.assertNotIn('http://pake.example.net', list(pake.config.node.Mirrors(test_node_root)))
        pake.config.node.Mirrors(test_node_root).reset().write()

    def testAddingPusher(self):
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).add(**pusher).write()
        self.assertIn(pusher, pake.config.node.Pushers(test_node_root))
        pake.config.node.Pushers(test_node_root).reset().write()

    def testRemovingPusher(self):
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).add(**pusher).write()
        pake.config.node.Pushers(test_node_root).remove(url='http://pake.example.com').write()
        self.assertNotIn(pusher, pake.config.node.Pushers(test_node_root))

    def testGettingPusher(self):
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).add(**pusher).write()
        self.assertEqual(pusher, pake.config.node.Pushers(test_node_root).get(url='http://pake.example.com'))
        pake.config.node.Pushers(test_node_root).reset().write()

    def testCheckingForURLInPushers(self):
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).add(**pusher).write()
        self.assertEqual(True, pake.config.node.Pushers(test_node_root).hasurl('http://pake.example.com'))
        pake.config.node.Pushers(test_node_root).reset().write()

    def testAddingAlien(self):
        alien = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        pake.config.node.Aliens(test_node_root).set(**alien).write()
        self.assertIn('http://alien.example.com', pake.config.node.Aliens(test_node_root))
        pake.config.node.Aliens(test_node_root).reset().write()

    def testRemovingAlien(self):
        alien = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        pake.config.node.Aliens(test_node_root).set(**alien).write()
        pake.config.node.Aliens(test_node_root).remove(alien['url']).write()
        self.assertNotIn('http://alien.example.com', pake.config.node.Aliens(test_node_root))

    def testGettingAlien(self):
        alien = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        pake.config.node.Aliens(test_node_root).set(**alien).write()
        del alien['url']
        self.assertEqual(alien, pake.config.node.Aliens(test_node_root).get('http://alien.example.com'))
        pake.config.node.Aliens(test_node_root).reset().write()

    def testListingAlienURLs(self):
        foo = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        bar = {'url': 'http://alien.example.net', 'mirrors': [], 'meta': {}}
        baz = {'url': 'http://alien.example.org', 'mirrors': [], 'meta': {}}
        pake.config.node.Aliens(test_node_root).set(**foo).set(**bar).set(**baz).write()
        self.assertEqual(['http://alien.example.com', 'http://alien.example.net', 'http://alien.example.org'],
                             sorted(pake.config.node.Aliens(test_node_root).urls()))
        pake.config.node.Aliens(test_node_root).reset().write()

    def testListingAliens(self):
        foo = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        bar = {'url': 'http://alien.example.net', 'mirrors': [], 'meta': {}}
        baz = {'url': 'http://alien.example.org', 'mirrors': [], 'meta': {}}
        pake.config.node.Aliens(test_node_root).set(**foo).set(**bar).set(**baz).write()
        aliens = pake.config.node.Aliens(test_node_root).all()
        self.assertIn(foo, aliens)
        pake.config.node.Aliens(test_node_root).reset().write()

    def testAddingPackages(self):
        package = {'name': 'foo', 'license': 'WTFPL', 'version': '0.0.1', 'origin': 'http://pake.example.com'}
        pake.config.node.Packages(test_node_root).set(package).write()
        self.assertIn('foo', pake.config.node.Packages(test_node_root).names())
        pake.config.node.Packages(test_node_root).reset().write()

    def testRemovingPackages(self):
        package = {'name': 'foo', 'license': 'WTFPL', 'version': '0.0.1', 'origin': 'http://pake.example.com'}
        pake.config.node.Packages(test_node_root).set(package).write()
        pake.config.node.Packages(test_node_root).remove('foo').write()
        self.assertNotIn('foo', pake.config.node.Packages(test_node_root).names())

    def testGettingPackagesData(self):
        package = {'name': 'foo', 'license': 'WTFPL', 'version': '0.0.1', 'origin': 'http://pake.example.com'}
        pake.config.node.Packages(test_node_root).set(package).write()
        self.assertEqual(package, pake.config.node.Packages(test_node_root).get('foo'))
        pake.config.node.Packages(test_node_root).reset().write()

    def testGettingPackagesNames(self):
        foo = {'name': 'foo', 'license': 'WTFPL', 'version': '0.0.1', 'origin': 'http://pake.example.com'}
        bar = {'name': 'bar', 'license': 'WTFPL', 'version': '0.0.1', 'origin': 'http://pake.example.com'}
        baz = {'name': 'baz', 'license': 'WTFPL', 'version': '0.0.1', 'origin': 'http://pake.example.com'}
        pake.config.node.Packages(test_node_root).set(foo).set(bar).set(baz).write()
        self.assertEqual(['bar', 'baz', 'foo'], sorted(pake.config.node.Packages(test_node_root).names()))
        pake.config.node.Packages(test_node_root).reset().write()

    def testSettingNests(self):
        nest = {'name': 'foo', 'path': '~/Dev/foo'}
        pake.config.node.Nests(test_node_root).set(**nest).write()
        self.assertEqual('~/Dev/foo', pake.config.node.Nests(test_node_root).get('foo'))
        pake.config.node.Nests(test_node_root).reset().write()

    def testRemovingNests(self):
        nest = {'name': 'foo', 'path': '~/Dev/foo'}
        pake.config.node.Nests(test_node_root).set(**nest).write()
        pake.config.node.Nests(test_node_root).remove('foo').write()
        self.assertRaises(KeyError, pake.config.node.Nests(test_node_root).get, 'foo')
        pake.config.node.Nests(test_node_root).reset().write()
    
    def testGettingPathOfOneNest(self):
        foo = {'name': 'foo', 'path': '~/Dev/foo'}
        bar = {'name': 'bar', 'path': '~/Dev/bar'}
        baz = {'name': 'baz', 'path': '~/Dev/baz'}
        pake.config.node.Nests(test_node_root).set(**foo).set(**bar).set(**baz).write()
        self.assertEqual('~/Dev/foo', pake.config.node.Nests(test_node_root).get('foo'))
        self.assertEqual('~/Dev/bar', pake.config.node.Nests(test_node_root).get('bar'))
        self.assertEqual('~/Dev/baz', pake.config.node.Nests(test_node_root).get('baz'))
        pake.config.node.Nests(test_node_root).reset().write()

    def testGettingPathsOfAllNests(self):
        foo = {'name': 'foo', 'path': '~/Dev/foo'}
        bar = {'name': 'bar', 'path': '~/Dev/bar'}
        baz = {'name': 'baz', 'path': '~/Dev/baz'}
        pake.config.node.Nests(test_node_root).set(**foo).set(**bar).set(**baz).write()
        self.assertEqual(['~/Dev/bar', '~/Dev/baz', '~/Dev/foo'], sorted(pake.config.node.Nests(test_node_root).paths()))
        pake.config.node.Nests(test_node_root).reset().write()


class NestConfigurationTests(unittest.TestCase):
    def testAddingVersions(self):
        pake.config.nest.Versions(test_nest_root).add('0.0.1-alpha.1').add('0.0.1-beta.1').add('0.0.1-rc.1').add('0.0.1').write()
        self.assertEqual(['0.0.1-alpha.1', '0.0.1-beta.1', '0.0.1-rc.1', '0.0.1'], list(pake.config.nest.Versions(test_nest_root)))
        pake.config.nest.Versions(test_nest_root).reset().write()

    def testAddingVersionsButChecking(self):
        pake.config.nest.Versions(test_nest_root).add('0.0.1-beta.1').write()
        self.assertRaises(ValueError, pake.config.nest.Versions(test_nest_root).add, '0.0.1-alpha.17', check=True)
        # assertNotRaises -- just run it; if no exception is raise everything's fine
        pake.config.nest.Versions(test_nest_root).add('0.0.1', check=True)
        pake.config.nest.Versions(test_nest_root).reset().write()

    def testAddingNewFiles(self):
        pake.config.nest.Files(test_nest_root).add('./tests.py').write()
        self.assertIn('./tests.py', pake.config.nest.Files(test_nest_root))
        pake.config.nest.Files(test_nest_root).reset().write()

    def testRefuseToAddNonexistentFile(self):
        self.assertRaises(FileNotFoundError, pake.config.nest.Files(test_nest_root).add, './this_file_does_not_exist.py')

    def testRefuseToAddFileThatIsAlreadyPresent(self):
        pake.config.nest.Files(test_nest_root).add('./tests.py').write()
        self.assertRaises(FileExistsError, pake.config.nest.Files(test_nest_root).add, './tests.py')
        pake.config.nest.Files(test_nest_root).reset().write()


if __name__ == '__main__': unittest.main()
