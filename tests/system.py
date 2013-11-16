#!/usr/bin/env python3

"""This is PAKE system test suite.
"""


import json
import os
import shutil
import tarfile
import unittest
import warnings


import pake


from tests import helpers, conf


# Test flags
VERBOSE = conf.VERBOSE
SERVER_ENABLED_TESTS = conf.SERVER_ENABLED_TESTS

# Test config data
test_remote_node_url = conf.test_remote_node_url
test_remote_node_host = conf.test_remote_node_host
test_remote_node_cwd = conf.test_remote_node_cwd

# Test environment
testdir = './testdir'
test_node_root = testdir + '/.pakenode'
test_nest_root = testdir + '/.pakenest'


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
        # cleanup
        helpers.rmnode(testdir)

    def testSettingPusher(self):
        helpers.gennode(testdir)
        # test logic
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).set(**pusher).write()
        self.assertIn(pusher, pake.config.node.Pushers(test_node_root))
        # cleanup
        helpers.rmnode(testdir)

    def testRemovingPusher(self):
        helpers.gennode(testdir)
        # test logic
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).set(**pusher).write()
        pake.config.node.Pushers(test_node_root).remove(url='http://pake.example.com').write()
        self.assertNotIn(pusher, pake.config.node.Pushers(test_node_root))
        # cleanup
        helpers.rmnode(testdir)

    def testGettingPusher(self):
        helpers.gennode(testdir)
        # test logic
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).set(**pusher).write()
        self.assertEqual(pusher, pake.config.node.Pushers(test_node_root).get(url='http://pake.example.com'))
        # cleanup
        helpers.rmnode(testdir)

    def testCheckingForURLInPushers(self):
        helpers.gennode(testdir)
        # test logic
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        pake.config.node.Pushers(test_node_root).set(**pusher).write()
        self.assertEqual(True, pake.config.node.Pushers(test_node_root).hasurl('http://pake.example.com'))
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

    def testSettingNest(self):
        helpers.gennode(testdir)
        # test logic
        pake.config.node.Nests(root=test_node_root).set('foo', './testdir/.pakenest').write()
        self.assertEqual('./testdir/.pakenest', pake.config.node.Nests(test_node_root).get('foo'))
        pake.config.node.Nests(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testRemovingNest(self):
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


class NodePackagesTests(unittest.TestCase):
    def testRegisteringNests(self):
        helpers.gennode(testdir)
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Meta(test_nest_root).set('name', 'foo').write()
        pake.node.packages.register(root=test_node_root, path=testdir)
        print('don\'t worry - this warning is supposed to appear in this test')
        # paths must be absolute to ensure that they are reachable from every directory
        self.assertEqual(os.path.abspath(test_nest_root), pake.config.node.Nests(test_node_root).get('foo'))
        pake.node.packages.unregister(root=test_node_root, name='foo')
        # cleanup
        helpers.rmnode(testdir)
        helpers.rmnest(testdir)

    def testBuildingPackageList(self):
        helpers.gennode(testdir)
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Meta(test_nest_root).set('name', 'foo').write()
        pake.config.node.Nests(test_node_root).set('foo', test_nest_root).write()
        pake.node.packages.genpkglist(test_node_root)
        ifstream = open(os.path.join(test_node_root, 'packages.json'))
        self.assertEqual(['foo'], json.loads(ifstream.read()))
        ifstream.close()
        # cleanup
        pake.config.node.Nests(test_node_root).reset().write()
        pake.config.nest.Meta(test_nest_root).reset().write()
        os.remove(os.path.join('.', 'testdir', '.pakenode', 'packages.json'))
        # cleanup
        helpers.rmnode(testdir)
        helpers.rmnest(testdir)


class NodePushingTests(unittest.TestCase):
    def testMirrorlistGeneration(self):
        helpers.gennode(testdir)
        # test logic
        pake.config.node.Pushers(test_node_root).set(url='http://pake.example.com', host='example.com', cwd='').write()
        pake.node.pusher.genmirrorlist(test_node_root)
        ifstream = open(os.path.join(test_node_root, 'mirrors.json'))
        self.assertEqual(['http://pake.example.com'], json.loads(ifstream.read()))
        ifstream.close()
        # cleanup
        helpers.rmnode(testdir)

    def testPushingToNode(self):
        helpers.gennode(testdir)
        helpers.gennest(testdir)
        version = helpers.buildTestPackage(path=test_nest_root, version='2.4.8.16')
        # test logic
        if SERVER_ENABLED_TESTS:
            # set all required variables
            url = conf.test_remote_node_url
            host = conf.test_remote_node_host
            cwd = conf.test_remote_node_cwd
            username = conf.test_remote_node_username
            password = conf.test_remote_node_pass
            # setup connection to test server
            remote = pake.node.pusher.FTPPusher(host)
            remote.login(username, password)
            if cwd: remote.cwd(cwd)
            # setup environment
            pake.config.nest.Meta(test_nest_root).set('name', 'test').write()
            pake.config.node.Pushers(test_node_root).set(url=url, host=host, cwd=cwd).write()
            pake.node.packages.register(root=test_node_root, path=testdir)
            pake.node.packages.genpkglist(root=test_node_root)
            pake.node.pusher.genmirrorlist(test_node_root)
            # push to remote node
            pake.node.pusher.push(root=test_node_root, url=url, username=username, password=password, reupload=True)
            # test if it went OK
            remote.cwd('./packages/test/versions/{0}'.format(version))
            files = remote.ls()
            self.assertIn('build.tar.xz', files)
            self.assertIn('meta.json', files)
            self.assertIn('dependencies.json', files)
            remote.close()
        else:
            warnings.warn('test not run: flag: SERVER_ENABLED_TESTS = {0}'.format(SERVER_ENABLED_TESTS))
        # cleanup
        helpers.rmnode(testdir)
        helpers.rmnest(testdir)
        if SERVER_ENABLED_TESTS:
            pass  # nothing is needed here (unless we want to wipe remote totally clean)



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


class NestConfigurationTests(unittest.TestCase):
    def testAddingVersions(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Versions(test_nest_root).add('0.0.1-alpha.1').add('0.0.1-beta.1').add('0.0.1-rc.1').add('0.0.1').write()
        self.assertEqual(['0.0.1-alpha.1', '0.0.1-beta.1', '0.0.1-rc.1', '0.0.1'], list(pake.config.nest.Versions(test_nest_root)))
        # cleanup
        helpers.rmnest(testdir)

    def testAddingVersionsButCheckingIfItsNotLowerThanTheLastOne(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Versions(test_nest_root).add('0.0.1-beta.1').write()
        self.assertRaises(ValueError, pake.config.nest.Versions(test_nest_root).add, '0.0.1-alpha.17', check=True)
        # assertNotRaises -- just run it; if no exception is raise everything's fine
        pake.config.nest.Versions(test_nest_root).add('0.0.1', check=True)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingADependency(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Dependencies(test_nest_root).set(name='foo').write()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingADependencyWithSpecifiedOrigin(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Dependencies(test_nest_root).set(name='foo', origin='http://pake.example.com').write()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'origin': 'http://pake.example.com'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingADependencyWithSpecifiedMinimalVersion(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Dependencies(test_nest_root).set(name='foo', min='0.2.4').write()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'min': '0.2.4'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingADependencyWithSpecifiedMaximalVersion(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Dependencies(test_nest_root).set(name='foo', max='2.4.8').write()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'max': '2.4.8'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingADependencyWithFullSpecification(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Dependencies(test_nest_root).set(name='foo', origin='http://pake.example.com', min='0.2.4', max='2.4.8').write()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'origin': 'http://pake.example.com', 'min': '0.2.4', 'max': '2.4.8'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testRemovingADependency(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Dependencies(test_nest_root).set(name='foo', origin='http://pake.example.com', min='0.2.4', max='2.4.8').write()
        pake.config.nest.Dependencies(test_nest_root).remove(name='foo').write()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testRedefiningADependency(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Dependencies(test_nest_root).set(name='foo', origin='http://pake.example.com', min='0.2.4', max='2.4.8').write()
        pake.config.nest.Dependencies(test_nest_root).set(name='foo', origin='http://pake.example.org').write()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'origin': 'http://pake.example.org'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testUpdatingADependency(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Dependencies(test_nest_root).set(name='foo', origin='http://pake.example.com', min='0.2.4', max='2.4.8').write()
        pake.config.nest.Dependencies(test_nest_root).update(name='foo', origin='http://pake.example.org').write()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'origin': 'http://pake.example.org', 'min': '0.2.4', 'max': '2.4.8'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testGettingDependencyData(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Dependencies(test_nest_root).set(name='foo', origin='http://pake.example.com', min='0.2.4', max='2.4.8').write()
        desired = {'origin': 'http://pake.example.com', 'min': '0.2.4', 'max': '2.4.8'}
        self.assertEqual(desired, pake.config.nest.Dependencies(test_nest_root).get(name='foo'))
        # cleanup
        helpers.rmnest(testdir)

    def testListingDependencies(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Dependencies(test_nest_root).set(name='foo').set(name='bar').set(name='baz').write()
        desired = ['foo', 'bar', 'baz']
        self.assertEqual(sorted(desired), sorted(list(pake.config.nest.Dependencies(test_nest_root))))
        # cleanup
        helpers.rmnest(testdir)

    def testAddingFile(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Files(test_nest_root).add(path='./pake/__init__.py').write()
        ifstream = open(os.path.join(test_nest_root, 'files.json'))
        files = json.loads(ifstream.read())
        ifstream.close()
        desired = ['./pake/__init__.py']
        self.assertEqual(desired, files)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingFileFailsIfFileHasAlreadyBeenAdded(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Files(test_nest_root).add(path='./pake/__init__.py').write()
        self.assertRaises(FileExistsError, pake.config.nest.Files(test_nest_root).add, path='./pake/__init__.py')
        # cleanup
        helpers.rmnest(testdir)

    def testAddingFileFailsIfPathIsNotAFile(self):
        helpers.gennest(testdir)
        # test logic
        self.assertRaises(pake.errors.NotAFileError, pake.config.nest.Files(test_nest_root).add, path='./this_file_does_not.exist')
        # cleanup
        helpers.rmnest(testdir)

    def testListingFiles(self):
        helpers.gennest(testdir)
        # test logic
        pake.config.nest.Files(test_nest_root).add(path='./pake/__init__.py').add('./pake/shared.py').write()
        desired = ['./pake/__init__.py', './pake/shared.py']
        self.assertEqual(desired, list(pake.config.nest.Files(test_nest_root)))
        # cleanup
        helpers.rmnest(testdir)


class NestReleaseBuildingTests(unittest.TestCase):
    def testPackageBuildCreatesAllNecessaryFiles(self):
        helpers.gennest(testdir)
        version = helpers.buildTestPackage(path=test_nest_root, version='0.2.4.8')
        # test logic
        self.assertIn(version, os.listdir(os.path.join(test_nest_root, 'versions')))
        self.assertIn('meta.json', os.listdir(os.path.join(test_nest_root, 'versions', version)))
        self.assertIn('dependencies.json', os.listdir(os.path.join(test_nest_root, 'versions', version)))
        self.assertIn('build.tar.xz', os.listdir(os.path.join(test_nest_root, 'versions', version)))
        # cleanup
        helpers.rmnest(testdir)

    def testAddingFile(self):
        helpers.gennest(testdir)
        # test logic
        pake.nest.package.addfile(test_nest_root, path='./pake/__init__.py')
        ifstream = open(os.path.join(test_nest_root, 'files.json'))
        files = json.loads(ifstream.read())
        ifstream.close()
        desired = ['./pake/__init__.py']
        self.assertEqual(desired, files)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingDirectory(self):
        helpers.gennest(testdir)
        # test logic
        pake.nest.package.adddir(test_nest_root, path='./ui', recursive=True, avoid=['__pycache__'], avoid_exts=['swp', 'pyc'])
        ifstream = open(os.path.join(test_nest_root, 'files.json'))
        files = json.loads(ifstream.read())
        ifstream.close()
        desired = ['./ui/nest.py', './ui/nest.json',
                   './ui/node.py', './ui/node.json',
                   './ui/packages.py', './ui/packages.json',
                   ]
        self.assertEqual(sorted(desired), sorted(files))
        # cleanup
        helpers.rmnest(testdir)

    def testIfArchieveContainsAllRequiredFiles(self):
        helpers.gennest(testdir)
        desired = ['./pake/__init__.py', './pake/shared.py']
        version = helpers.buildTestPackage(path=test_nest_root, version='2.4.8', files=desired, directories=[])
        # test logic
        test_pkg = tarfile.TarFile(os.path.join(test_nest_root, 'versions', version, 'build.tar.xz'), 'r')
        names = test_pkg.getnames()
        test_pkg.close()
        # create list of files we expect to be included
        if VERBOSE: [print(i) for i in names]
        self.assertEqual(sorted([os.path.normpath(i) for i in desired]), sorted(names))
        # cleanup
        helpers.rmnest(testdir)

    def testIfBuildIncludedNewVersionInVersionsFile(self):
        helpers.gennest(testdir)
        desired = []
        desired.append(helpers.buildTestPackage(test_nest_root, version='0.1.2', files=[], directories=[]))
        desired.append(helpers.buildTestPackage(test_nest_root, version='0.1.3', files=[], directories=[]))
        desired.append(helpers.buildTestPackage(test_nest_root, version='0.1.4', files=[], directories=[]))
        versions = pake.config.nest.Versions(test_nest_root)
        # test logic
        for i in desired:
            self.assertIn(i, versions)
        # cleanup
        helpers.rmnest(testdir)


# Wrapper class
class Suite(NodeManagerTests, NodeConfigurationTests, NodePackagesTests, NodePushingTests, NestManagerTests, NestConfigurationTests, NestReleaseBuildingTests):
    pass

if __name__ == '__main__':
    helpers.prepare(testdir)
    unittest.main()
