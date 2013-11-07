#!/usr/bin/env python3

"""This is PAKE test suite code.

Apart from this file test suite consists of:

    * `./testdir/` directory - containing test node, nest and network,
    * `./testfiles/` directory - containing test transaction files,

To experience full joy of testing PAKE you must have a working FTP server available.
This is needed to test PAKE networking features (e.g. finding packages and
crawling aliens among other things).

Before you run any tests you should create your `testconf.py` file.
Read `testconf.mdown` file to learn more.
"""

# Libraries from Python standard library a.k.a. batteries
import ftplib
import json
import os
import random
import shutil
import tarfile
import unittest
import warnings


# External libraries PAKE uses
#
# * but can be obtained from: https://github.com/marekjm/but (only one object from it is needed: but.scanner.Scanner())
# * clap (UI library used by PAKE) can be obtained from: https://github.com/marekjm/clap
# * pyversion can be obtained from: https://github.com/marekjm/pyversion
# * fsrl can be obtained from: https://github.com/marekjm/fsrl
import but
import clap
import pyversion
import fsrl


# PAKE import
import pake


# Import test configuration
import testconf


print('* all imports successful')


# Flags
VERBOSE = True
SERVER_ENABLED_TESTS = testconf.SERVER_ENABLED_TESTS
print('* setting flags successful')


# Global variables
test_node_root = pake.shared.getnodepath(check=False, fake=os.path.abspath('./testdir'))
test_nest_root = pake.shared.getnestpath(check=False, fake=os.path.abspath('./testdir'))
test_network_url = testconf.test_network_url
test_network_host = testconf.test_network_host
test_network_wd = testconf.test_network_wd
test_network_user = testconf.test_network_user
test_network_pass = testconf.test_network_pass
test_server_url = testconf.test_server_url
test_server_host = testconf.test_server_host
test_server_cwd = testconf.test_server_cwd
test_server_username = testconf.test_server_username
test_server_password = testconf.test_server_password
print('* setting global test variables successful')

print()  # line break between variable and flags setup and environment setup

# Helper functions
def getrandomstring(n=16):
    """Returns random string containing characters a-zA-Z0-9 from ASCII range.
    """
    lowercase = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    uppercase = [char.upper() for char in lowercase]
    digits = [str(i) for i in range(10)]
    string = ''
    chars = lowercase + uppercase + digits
    for i in range(n): string += random.choice(chars)
    return string

def createTestNode(path):
    """Creates test node in given path.
    """
    print(' * creating new test node root in {0}'.format(path))
    pake.node.manager.makedirs(root=test_node_root)
    print('   * created directories...')
    pake.node.manager.makeconfig(root=test_node_root)
    print('   * wrote config files...')
    pake.node.packages.genpkglist(root=test_node_root)
    print('   * generated (empty) packages list')
    pake.node.pusher.genmirrorlist(root=test_node_root)
    print('   * generated (empty) mirror list')
    print(' + created new test node root')

def createTestNest(path):
    """Creates test nest.
    """
    print(' * creating new test nest root in {0}'.format(path))
    print('   * creating directories...')
    pake.nest.manager.makedirs(root=test_nest_root)
    print('   * writing config files...')
    pake.nest.manager.makeconfig(root=test_nest_root)
    print(' + created new test nest root')

def createFakeAlien(remote, n):
    """Creates fake alien.
    """
    name = 'alien{0}'.format(n)
    if name not in remote.ls(): remote.mkd(name)
    # change directory to this alien's directory
    remote.cwd(name)
    # create fake meta file
    ofsmeta = open('./testfiles/tmp/meta.json', 'w')
    url = '{0}/{1}'.format(test_network_url, name)
    print('  * url for {0}: {1}'.format(name, url))
    if i % 2 == 0: ofsmeta.write(json.dumps({'url': url}))
    else: ofsmeta.write(json.dumps({'url': '{0}/{1}/alien{2}'.format(test_network_url, test_network_wd, n-1)}))
    ofsmeta.close()
    # create fake mirrors file
    ofsmirrors = open('./testfiles/tmp/mirrors.json', 'w')
    mirrors = [url]
    if n % 2 == 0: mirrors.append('{0}/{1}/alien{2}'.format(test_network_url, test_network_wd, n+1))
    else: mirrors.append('{0}/{1}/alien{2}'.format(test_network_url, test_network_wd, n-1))
    ofsmirrors.write(json.dumps(mirrors))
    ofsmirrors.close()
    # create fake aliens file
    ofsmirrors = open('./testfiles/tmp/aliens.json', 'w')
    if n+2 <= 5:  # we don't create fake mirrors alien8, alien9 etc.
        ofsmirrors.write(json.dumps(['{0}/{1}/alien{2}'.format(test_network_url, test_network_wd, n+2)]))
    else:  # so for aliens with 'i' greater or equal to 4 instead of adding we substract
        ofsmirrors.write(json.dumps(['{0}/{1}/alien{2}'.format(test_network_url, test_network_wd, n-4)]))
    ofsmirrors.close()
    # push fake config files
    remote.sendlines('./testfiles/tmp/meta.json').sendlines('./testfiles/tmp/mirrors.json').sendlines('./testfiles/tmp/aliens.json')
    # return to parent directory to prepare for switching to another alien
    remote.cwd('..')

def createFakeMirror(remote, n):
    """Creates fake mirror and pushes to it.
    """
    pushers = pake.config.node.Pushers(test_node_root)
    name = 'mirror{0}'.format(n)
    if name not in remote.ls(): remote.mkd(name)
    url = '{0}/{1}'.format(test_network_url, name)
    pushers.add(url=url, host=test_network_host, cwd='{0}/{1}'.format(test_network_wd, name)).write()
    pake.node.pusher.push(root=test_node_root, url=url, username=test_network_user, password=test_network_pass, reupload=True)
    print('  * pushed to test mirror {0}: {1}'.format(n, url))

def buildTestPackage(version='0.2.4.8'):
    """Builds test package.
    Returns version of built package.
    """
    pake.config.nest.Meta(test_nest_root).set('name', 'test').write()
    pake.nest.package.addfile(test_nest_root, './tests.py')
    pake.nest.package.addfile(test_nest_root, './install.fsrl')
    pake.nest.package.addfile(test_nest_root, './remove.fsrl')
    pake.nest.package.adddir(test_nest_root, './ui/', recursive=True, avoid=['__pycache__'], avoid_exts=['swp', 'pyc'])
    pake.nest.package.build(root=test_nest_root, version=version)
    return version


# Test environment setup
print('* preparing local test environment...')
if os.path.isdir(test_node_root):
    print('* removing old test node root')
    shutil.rmtree(test_node_root)
if os.path.isdir(test_nest_root):
    print('* removing old test nest root')
    shutil.rmtree(test_nest_root)


createTestNode(path=test_node_root)
createTestNest(path=test_nest_root)
print('+ successfully created test environment in {0}'.format(os.path.abspath('./testdir')))
print()  # to make a one-line break between test node and nest messages and test network messages


# Creating test network
#remote = ftplib.FTP(test_network_host)
remote = pake.node.pusher.FTPPusher(test_network_host)
remote.login(test_network_user, test_network_pass)
if test_network_wd: remote.cwd(test_network_wd)
print('* creating test network in \'{0}\''.format(remote.pwd()))

for i in range(8):  # create 8 fake aliens
    createFakeAlien(remote=remote, n=i)

for i in range(4):  # create 4 fake mirrors
    createFakeMirror(remote=remote, n=i)
remote.close()
print('+ successfully created test network')

print('\n')


# Tests of node features
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
                    ('pushers.json', []),
                    ('aliens.json', {}),
                    ('nests.json', {}),
                    ]
        if VERBOSE: print()
        for f, desired in configs:
            path = os.path.join(test_node_root, f)
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

    def testSettingNests(self):
        pake.config.node.Nests(root=test_node_root).set('foo', './testdir/.pakenest').write()
        self.assertEqual('./testdir/.pakenest', pake.config.node.Nests(test_node_root).get('foo'))
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


class NodePackagesTests(unittest.TestCase):
    def testRegisteringPackages(self):
        pake.config.nest.Meta(test_nest_root).set('name', 'foo').write()
        pake.node.packages.register(root=test_node_root, path='./testdir/.pakenest')
        print('don\'t worry - this warning is supposed to appear in this test')
        # paths must be absolute to ensure that they are reachable from every directory
        self.assertEqual(os.path.abspath('./testdir/.pakenest'), pake.config.node.Nests(test_node_root).get('foo'))
        pake.node.packages.unregister(root=test_node_root, name='foo')
        pake.config.node.Nests(test_node_root).reset().write()
        pake.config.nest.Meta(test_nest_root).reset().write()

    def testBuildingPackageList(self):
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


class NodePushingTests(unittest.TestCase):
    def testMirrorlistGeneration(self):
        pake.config.node.Pushers(test_node_root).add(url='http://pake.example.com', host='example.com', cwd='').write()
        pake.node.pusher.genmirrorlist(test_node_root)
        ifstream = open(os.path.join(test_node_root, 'mirrors.json'))
        self.assertEqual(['http://pake.example.com'], json.loads(ifstream.read()))
        ifstream.close()
        # cleanup
        pake.config.node.Pushers(test_node_root).reset().write()
        os.remove(os.path.join(test_node_root, 'mirrors.json'))

    def testPushingToNode(self):
        version = '2.4.8.16'
        if SERVER_ENABLED_TESTS:  # testing code
            # set all required variables
            url = test_server_url
            host = test_server_host
            cwd = test_server_cwd
            username = test_server_username
            password = test_server_password
            remote = pake.node.pusher.FTPPusher(test_server_host)
            remote.login(username, password)
            if cwd: remote.cwd(cwd)

            pake.config.nest.Meta(test_nest_root).set('name', 'test').write()
            pake.node.packages.register(root=test_node_root, path='./testdir/.pakenest')
            pake.nest.package.addfile(test_nest_root, './tests.py')
            pake.nest.package.addfile(test_nest_root, './install.fsrl')
            pake.nest.package.addfile(test_nest_root, './remove.fsrl')
            pake.nest.package.adddir(test_nest_root, './ui/', recursive=True, avoid=['__pycache__'], avoid_exts=['swp', 'pyc'])
            pake.nest.package.adddir(test_nest_root, './webui/', recursive=True, avoid_exts=['swp', 'pyc'])
            pake.nest.package.build(test_nest_root, version=version)
            pake.node.packages.genpkglist(root=test_node_root)
            pake.config.node.Pushers(test_node_root).add(url=url, host=host, cwd=cwd).write()
            pake.node.pusher.genmirrorlist(test_node_root)

            print(os.listdir(os.path.join(test_nest_root, 'versions')))
            print(remote.ls('./packages/test/versions'))
            pake.node.pusher.push(root=test_node_root, url=url, username=username, password=password, reupload=True)

            exit()
            """

            remote.cwd('./packages/foo/versions/{0}'.format(version))
            files = remote.ls()
            if VERBOSE: print(files)
            self.assertIn('build.tar.xz', files)
            self.assertIn('meta.json', files)
            self.assertIn('dependencies.json', files)
            remote.close()
            """
        else:
            warnings.warn('test not run: flag: SERVER_ENABLED_TESTS = {0}'.format(SERVER_ENABLED_TESTS))
        if SERVER_ENABLED_TESTS:  # cleanup (reset to default, empty state)
            pake.config.node.Nests(test_node_root).reset().write()
            pake.config.nest.Files(test_nest_root).reset().write()
            pake.config.nest.Meta(test_nest_root).reset().write()


# Tests of nest features
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


class NestAddingFilesTests(unittest.TestCase):
    def testAddingNewFilesDirectly(self):
        pake.config.nest.Files(test_nest_root).add('./tests.py').write()
        self.assertIn('./tests.py', pake.config.nest.Files(test_nest_root))
        # cleanup
        pake.config.nest.Files(test_nest_root).reset().write()

    def testAddingNewFilesViaNestInterface(self):
        pake.nest.package.addfile(test_nest_root, './tests.py')
        self.assertIn('./tests.py', pake.config.nest.Files(test_nest_root))
        # cleanup
        pake.config.nest.Files(test_nest_root).reset().write()

    def testRefuseToAddNonexistentFile(self):
        self.assertRaises(pake.errors.NotAFileError, pake.config.nest.Files(test_nest_root).add, './this_file_does_not_exist.py')

    def testRefuseToAddFileThatIsAlreadyPresent(self):
        pake.config.nest.Files(test_nest_root).add('./tests.py').write()
        self.assertRaises(FileExistsError, pake.config.nest.Files(test_nest_root).add, './tests.py')
        # cleanup
        pake.config.nest.Files(test_nest_root).reset().write()


class NestReleaseBuildingTests(unittest.TestCase):
    def testPackageBuildCreatesAllNecessaryFiles(self):
        version = buildTestPackage()
        self.assertIn(version, os.listdir(os.path.join(test_nest_root, 'versions')))
        self.assertIn('meta.json', os.listdir(os.path.join(test_nest_root, 'versions', version)))
        self.assertIn('dependencies.json', os.listdir(os.path.join(test_nest_root, 'versions', version)))
        self.assertIn('build.tar.xz', os.listdir(os.path.join(test_nest_root, 'versions', version)))
        # cleanup
        pake.config.nest.Files(test_nest_root).reset().write()
        pake.config.nest.Meta(test_nest_root).reset().write()
        shutil.rmtree(os.path.join(test_nest_root, 'versions', version))

    def testIfArchieveContainsAllRequiredFiles(self):
        version = buildTestPackage()
        test_pkg = tarfile.TarFile(os.path.join(test_nest_root, 'versions', version, 'build.tar.xz'), 'r')
        names = test_pkg.getnames()
        test_pkg.close()
        # create list of files we expect to be included
        expected = ['./tests.py', './install.fsrl', './remove.fsrl']
        expected += but.scanner.Scanner('./ui/').discardExtension('pyc').scan().files
        expected = [os.path.normpath(i) for i in expected]
        if VERBOSE: [print(i) for i in names]
        self.assertEqual(sorted(expected), sorted(names))
        # cleanup
        pake.config.nest.Files(test_nest_root).reset().write()
        pake.config.nest.Meta(test_nest_root).reset().write()
        shutil.rmtree(os.path.join(test_nest_root, 'versions', version))

    def testIfBuildIncludedNewVersionInVersionsFile(self):
        version = buildTestPackage()
        self.assertIn(version, pake.config.nest.Versions(test_nest_root))
        # cleanup
        pake.config.nest.Files(test_nest_root).reset().write()
        pake.config.nest.Meta(test_nest_root).reset().write()
        shutil.rmtree(os.path.join(test_nest_root, 'versions', version))


# Tests for package-management features
class PackageManagerTests(unittest.TestCase):
    pass


# Tests of network features
class NetworkPackageIndexingTests(unittest.TestCase):
    def testGeneratingLocalPkgIndex(self):
        # set origin for the package
        version = '0.2.4.8'
        origin = '{0}/mirror0'.format(test_network_url)
        # add the origin to the metadata of the node
        pake.config.node.Meta(test_node_root).set('url', origin).write()
        # set name of the package in its metadata
        pake.config.nest.Meta(test_nest_root).set('name', 'foo').write()
        # register the package in node (so it becomes visible to the network)
        pake.node.packages.register(root=test_node_root, path=test_nest_root)
        pake.config.node.Pushers(test_node_root).add(url=origin, host=test_network_host, cwd=test_network_wd).write()
        index, errors = pake.network.pkgs.getlocalindex(test_node_root)
        desired = [{'name': 'foo', 'versions': [version], 'origin': origin}]
        self.assertEqual(desired, index)
        print(index)
        self.assertEqual([], errors)
        # cleanup...
        pake.config.nest.Meta(test_nest_root).reset().write()
        pake.config.node.Meta(test_node_root).reset().write()
        pake.config.node.Pushers(test_node_root).reset().write()


# Transaction-related tests
class TokenizationTests(unittest.TestCase):
    def testSimpleTokenization(self):
        tokens = pake.transactions.parser.tokenize('foo bar')
        self.assertEqual(['foo', 'bar'], tokens)

    def testTokenizationWithMultipleWhitespaceBetweenWords(self):
        tokens = pake.transactions.parser.tokenize('foo     bar')
        self.assertEqual(['foo', 'bar'], tokens)

    def testTokenizationWithQuotedStringsContainingWhitespace(self):
        tokens = pake.transactions.parser.tokenize('foo "  bar baz "', dequoted=True)
        self.assertEqual(['foo', '  bar baz '], tokens)

    def testTokenizationWithEmptyStrings(self):
        tokens = pake.transactions.parser.tokenize('foo "" bar \'\'', dequoted=True)
        self.assertEqual(['foo', '', 'bar', ''], tokens)


class TransactionParserTests(unittest.TestCase):
    def testLoadingPKGfetch(self):
        parsed = pake.transactions.parser.Parser(path='./testfiles/pkg.fetch.transaction').load().getlines()
        desired = [['PKG', 'FETCH', 'foo'],
                   ['PKG', 'FETCH', 'foo', 'FROM', 'http://pake.example.com'],
                   ['PKG', 'FETCH', 'foo', 'VERSION', '0.0.1'],
                   ['PKG', 'FETCH', 'foo', 'VERSION', '0.0.1', 'FROM', 'http://pake.example.com'],
                   ]
        self.assertEqual(desired, parsed)

    def testLoadingPKGinstall(self):
        parsed = pake.transactions.parser.Parser(path='./testfiles/pkg.install.transaction').load().getlines()
        desired = [['PKG', 'INSTALL', 'foo'],
                   ['PKG', 'INSTALL', 'foo', 'VERSION', '0.0.1'],
                   ]
        self.assertEqual(desired, parsed)

    def testLoadingPKGremove(self):
        parsed = pake.transactions.parser.Parser(path='./testfiles/pkg.remove.transaction').load().getlines()
        desired = [['PKG', 'REMOVE', 'foo']]
        self.assertEqual(desired, parsed)

    def testParsingPKGfetch(self):
        parsed = pake.transactions.parser.Parser(path='./testfiles/pkg.fetch.transaction').load().parse().getparsed()
        desired = [{'req': 'PKG', 'context': 'FETCH', 'fetch': 'foo'},
                   {'req': 'PKG', 'context':'FETCH', 'fetch': 'foo', 'origin': 'http://pake.example.com'},
                   {'req': 'PKG', 'context':'FETCH', 'fetch': 'foo', 'version': '0.0.1'},
                   {'req': 'PKG', 'context':'FETCH', 'fetch': 'foo', 'version': '0.0.1', 'origin': 'http://pake.example.com'},
                   ]
        self.assertEqual(desired, parsed)

    def testParsingPKGinstall(self):
        parsed = pake.transactions.parser.Parser(path='./testfiles/pkg.install.transaction').load().parse().getparsed()
        desired = [{'req': 'PKG', 'context': 'INSTALL', 'install': 'foo'},
                   {'req': 'PKG', 'context': 'INSTALL', 'install': 'foo', 'version': '0.0.1'},
                   ]
        self.assertEqual(desired, parsed)

    def testParsingPKGremove(self):
        parsed = pake.transactions.parser.Parser(path='./testfiles/pkg.remove.transaction').load().parse().getparsed()
        desired = [{'req': 'PKG', 'context': 'REMOVE', 'remove': 'foo'}]
        self.assertEqual(desired, parsed)


class TransactionEncoderTests(unittest.TestCase):
    def testEncodingPKGfetch(self):
        parser = pake.transactions.parser.Parser(path='./testfiles/pkg.fetch.transaction').load().parse()
        desired = [['PKG', 'FETCH', "'foo'"],
                   ['PKG', 'FETCH', "'foo'", 'FROM', "'http://pake.example.com'"],
                   ['PKG', 'FETCH', "'foo'", 'VERSION', "'0.0.1'"],
                   ['PKG', 'FETCH', "'foo'", 'VERSION', "'0.0.1'", 'FROM', "'http://pake.example.com'"],
                   ]
        encoder = pake.transactions.encoder.Encoder(parsed=parser.getparsed()).encode()
        self.assertEqual(desired, encoder.getsource(joined=False))

    def testEncodingPKGinstall(self):
        parser = pake.transactions.parser.Parser(path='./testfiles/pkg.install.transaction').load().parse()
        desired = [['PKG', 'INSTALL', "'foo'"],
                   ['PKG', 'INSTALL', "'foo'", 'VERSION', "'0.0.1'"],
                   ]
        encoder = pake.transactions.encoder.Encoder(parsed=parser.getparsed()).encode()
        self.assertEqual(desired, encoder.getsource(joined=False))

    def testEncodingPKGremove(self):
        parser = pake.transactions.parser.Parser(path='./testfiles/pkg.remove.transaction').load().parse()
        desired = [['PKG', 'REMOVE', "'foo'"]]
        encoder = pake.transactions.encoder.Encoder(parsed=parser.getparsed()).encode()
        self.assertEqual(desired, encoder.getsource(joined=False))


@unittest.skip('before transaction runner implement package indexing')
class TransactionRunnerTests(unittest.TestCase):
    def testFinalizingPackageFetch(self):
        request = {'req': 'PKG', 'context': 'FETCH', 'fetch': 'foo'}
        desired = {'req': 'PKG', 'context': 'FETCH', 'fetch': 'foo', 'version': '0.0.1', 'origin': 'http://pake.example.com'}
        runner = pake.transactions.runner.Runner(reqs=[request]).finalize()
        self.assertEqual(desired, runner._reqs[0])


if __name__ == '__main__': unittest.main()
