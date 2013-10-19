#!/usr/bin/env python3


# Libraries from Python standard library a.k.a. batteries
import ftplib
import json
import os
import shutil
import tarfile
import unittest
import warnings


# External libraries PAKE uses
#
# "but" can be obtained from: https://github.com/marekjm/but
# only one object from it is needed: but.scanner.Scanner()
import but
# "clap" (UI library used by PAKE) can be obtained from: https://github.com/marekjm/clap
import clap


# PAKE import
import pake


# import test configuration
import testconf


# Flags
VERBOSE = True
# end: Flags


# Global variables

test_node_root = pake.shared.getnodepath(check=False, fake=os.path.abspath('./testdir'))
test_nest_root = pake.shared.getnestpath(check=False, fake=os.path.abspath('./testdir'))

# end: Global variables


# Test environment setup
print('* preparing local test environment...')
if os.path.isdir(test_node_root):
    print('  * removing old test node root', end='  ')
    shutil.rmtree(test_node_root)
    print('[  OK  ]')
if os.path.isdir(test_nest_root):
    print('  * removing old test nest root', end='  ')
    shutil.rmtree(test_nest_root)
    print('[  OK  ]')

print(' * creating new test node root')
pake.node.manager.makedirs(root=test_node_root)
print('   * created directories...')
pake.node.manager.makeconfig(root=test_node_root)
print('   * wrote config files...')
pake.node.packages.genpkglist(root=test_node_root)
print('   * generated (empty) packages list')
pake.node.pusher.genmirrorlist(root=test_node_root)
print('   * generated (empty) mirror list')
print(' + created new test node root')

print(' * creating new test nest root')
print('   * creating directories...')
pake.nest.manager.makedirs(root=test_nest_root)
print('   * writing config files...')
pake.nest.manager.makeconfig(root=test_nest_root)
print(' + created new test nest root')

print('+ successfully created test environment in {0}'.format(os.path.abspath('./testdir')))
print()  # to make a one-line break between setup messages and actual test messages


# Creating test network
test_network_url = 'http://127.0.0.1'  # without trailing slash
test_network_host = '127.0.0.1'
test_network_wd = 'paketest'
test_network_user = 'marekjm'
test_network_pass = 'pass'

print('* creating test network...')
remote = ftplib.FTP(test_network_host)
remote.login(test_network_user, test_network_pass)
if test_network_wd: remote.cwd(test_network_wd)
print('* creating test network in \'{0}\''.format(remote.pwd()))
ls = pake.node.pusher._lsdir(remote)
print(ls)
for i in range(8):  # create dummy aliens
    name = 'alien{0}'.format(i)
    # 1. create the directory if it does not exist
    if name not in ls: remote.mkd(name)
    # 2. change directory to this alien's directory
    remote.cwd(name)
    # 3. create fake meta file
    ofsmeta = open('./testfiles/tmp/meta.json', 'w')
    url = '{0}/{1}/{2}'.format(test_network_url, test_network_wd, name)
    if i % 2 == 0: ofsmeta.write(json.dumps({'url': url}))
    else: ofsmeta.write(json.dumps({'url': '{0}/{1}/alien{2}'.format(test_network_url, test_network_wd, i-1)}))
    ofsmeta.close()
    # 4. create fake mirrors file
    ofsmirrors = open('./testfiles/tmp/mirrors.json', 'w')
    mirrors = [url]
    if i % 2 == 0: mirrors.append('{0}/{1}/alien{2}'.format(test_network_url, test_network_wd, i+1))
    else: mirrors.append('{0}/{1}/alien{2}'.format(test_network_url, test_network_wd, i-1))
    ofsmirrors.write(json.dumps(mirrors))
    ofsmirrors.close()
    # 5. create fake aliens file
    ofsmirrors = open('./testfiles/tmp/aliens.json', 'w')
    if i+2 <= 5:  # we don't create fake mirrors alien8, alien9 etc.
        ofsmirrors.write(json.dumps(['{0}/{1}/alien{2}'.format(test_network_url, test_network_wd, i+2)]))
    else:  # so for aliens with 'i' greater or equal to 4 instead of adding we substract
        ofsmirrors.write(json.dumps(['{0}/{1}/alien{2}'.format(test_network_url, test_network_wd, i-4)]))
    ofsmirrors.close()
    # 6. push fake config files
    pake.node.pusher._sendlines(remote, './testfiles/tmp/meta.json')
    pake.node.pusher._sendlines(remote, './testfiles/tmp/mirrors.json')
    pake.node.pusher._sendlines(remote, './testfiles/tmp/aliens.json')
    # 7. return to parent directory to prepare for switching to another alien
    remote.cwd('..')

pushers = pake.config.node.Pushers(test_node_root)
for i in range(4):  # create dummy mirrors
    name = 'mirror{0}'.format(i)
    if name not in ls:
        remote.mkd(name)
        print(' * created directory for dummy mirror {0}'.format(i))
    url = '{0}/{1}'.format(test_network_url, name)
    pushers.add(url=url, host=test_network_host, cwd='{0}/{1}'.format(test_network_wd, name)).write()
    print(' * added pusher for mirror {0}: {1}'.format(i, url))
    pake.node.pusher.push(root=test_node_root, url=url, username=test_network_user, password=test_network_pass, reupload=True)
    print(' * pushed to mirror {0}'.format(i))
remote.close()
print('+ successfully created test network')


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

    def testAddingNewFilesDirectly(self):
        pake.config.nest.Files(test_nest_root).add('./tests.py').write()
        self.assertIn('./tests.py', pake.config.nest.Files(test_nest_root))
        pake.config.nest.Files(test_nest_root).reset().write()

    def testAddingNewFilesViaNestInterface(self):
        pake.nest.package.addfile(test_nest_root, './tests.py')
        self.assertIn('./tests.py', pake.config.nest.Files(test_nest_root))
        pake.config.nest.Files(test_nest_root).reset().write()

    def testRefuseToAddNonexistentFile(self):
        self.assertRaises(FileNotFoundError, pake.config.nest.Files(test_nest_root).add, './this_file_does_not_exist.py')

    def testRefuseToAddFileThatIsAlreadyPresent(self):
        pake.config.nest.Files(test_nest_root).add('./tests.py').write()
        self.assertRaises(FileExistsError, pake.config.nest.Files(test_nest_root).add, './tests.py')
        pake.config.nest.Files(test_nest_root).reset().write()


class NestReleasesTests(unittest.TestCase):
    def testBuildingNonsignedPackage(self):
        # 1: setup minimal meta needed for build process
        pake.config.nest.Meta(test_nest_root).set('name', 'test').set('version', '0.0.1').write()
        # 2: create list of files
        pake.nest.package.addfile(test_nest_root, './tests.py')
        pake.nest.package.adddir(test_nest_root, './ui/', recursive=True, avoid=['__pycache__'], avoid_exts=['swp', 'pyc'])
        pake.nest.package.adddir(test_nest_root, './webui/', recursive=True, avoid_exts=['swp', 'pyc'])
        # 3: run build routine
        pake.nest.package.build(test_nest_root)
        # 4: check if the package was built
        # 4.1: check if the directory was created
        self.assertIn('0.0.1', os.listdir(os.path.join(test_nest_root, 'versions')))
        # 4.2: check if the meta has been copied
        self.assertIn('meta.json', os.listdir(os.path.join(test_nest_root, 'versions', '0.0.1')))
        # 4.3: check if the dependencies.json has been copied
        self.assertIn('dependencies.json', os.listdir(os.path.join(test_nest_root, 'versions', '0.0.1')))
        # 5: get names of files included in package
        test_pkg = tarfile.TarFile(os.path.join(test_nest_root, 'versions', '0.0.1', 'build.tar.xz'), 'r')
        names = test_pkg.getnames()
        test_pkg.close()
        # sixth: create list of files we expect to be included
        expected = ['./tests.py'] + but.scanner.Scanner('./ui/').discardExtension('pyc').scan().files + but.scanner.Scanner('./webui/').scan().files
        if VERBOSE: [print(i) for i in expected]
        # seventh: check if the two lists are equal
        self.assertEqual(expected, names)
        self.assertIn('0.0.1', pake.config.nest.Versions(test_nest_root))
        # eighth: cleanup (reset to default, empty state)
        shutil.rmtree(os.path.join(test_nest_root, 'versions', '0.0.1'))
        pake.config.nest.Files(test_nest_root).reset().write()
        pake.config.nest.Meta(test_nest_root).reset().write()


class NodePackagesTests(unittest.TestCase):
    def testRegisteringPackages(self):
        pake.config.nest.Meta(test_nest_root).set('name', 'foo').write()
        pake.config.nest.Meta(test_nest_root).set('version', '0.0.1').write()
        pake.config.nest.Meta(test_nest_root).set('license', 'GNU GPL v3+').write()
        pake.node.packages.register(root=test_node_root, path='./testdir/.pakenest')
        print('don\'t worry - this warning is supposed to appear in this test')
        # path smust be absolute to ensure that they are reachable from every other dir
        self.assertEqual(os.path.abspath('./testdir/.pakenest'), pake.config.node.Nests(test_node_root).get('foo'))
        pake.config.node.Nests(test_node_root).reset().write()
        pake.config.nest.Meta(test_nest_root).reset().write()

    def testBuildingPackageList(self):
        pake.config.nest.Meta(test_nest_root).set('name', 'foo').write()
        pake.config.node.Nests(test_node_root).set('foo', test_nest_root).write()
        pake.node.packages.genpkglist(test_node_root)
        ifstream = open(os.path.join(test_node_root, 'packages.json'))
        self.assertEqual(['foo'], json.loads(ifstream.read()))
        ifstream.close()


class NodePushingTests(unittest.TestCase):
    def testMirrorlistGeneration(self):
        pake.config.node.Pushers(test_node_root).add(url='http://pake.example.com', host='example.com', cwd='').write()
        pake.node.pusher.genmirrorlist(test_node_root)
        ifstream = open(os.path.join(test_node_root, 'mirrors.json'))
        self.assertEqual(['http://pake.example.com'], json.loads(ifstream.read()))
        ifstream.close()
        pake.config.node.Pushers(test_node_root).reset().write()

    def testPushingToNode(self):
        pake.config.nest.Meta(test_nest_root).set('name', 'test').set('version', '0.0.1').write()
        pake.nest.package.addfile(test_nest_root, './tests.py')
        pake.nest.package.adddir(test_nest_root, './ui/', recursive=True, avoid=['__pycache__'], avoid_exts=['swp', 'pyc'])
        pake.nest.package.adddir(test_nest_root, './webui/', recursive=True, avoid_exts=['swp', 'pyc'])
        pake.nest.package.build(test_nest_root)
        pake.config.node.Nests(root=test_node_root).set('foo', './testdir/.pakenest').write()

        if testconf.SERVER_ENABLED_TESTS:
            url = testconf.test_server_url
            host = testconf.test_server_host
            cwd = testconf.test_server_cwd
            pake.config.node.Pushers(test_node_root).add(url=url, host=host, cwd=cwd).write()
            username = testconf.test_server_username
            password = testconf.test_server_password
            pake.node.pusher.push(root=test_node_root, url=url, username=username, password=password, reupload=True)
            remote = ftplib.FTP(testconf.test_server_host)
            remote.login(testconf.test_server_username, testconf.test_server_password)
            if cwd: remote.cwd(cwd)
            remote.cwd('./packages/foo/versions/0.0.1')
            files = pake.node.pusher._lsdir(remote)
            if VERBOSE: print(files)
            self.assertIn('build.tar.xz', files)
            self.assertIn('meta.json', files)
            self.assertIn('dependencies.json', files)
            remote.close()
        else:
            warnings.warn('test not run: SERVER_ENABLED_TESTS is False')
        # cleanup (reset to default, empty state)
        pake.config.node.Nests(test_node_root).reset().write()
        pake.config.nest.Files(test_nest_root).reset().write()
        pake.config.nest.Meta(test_nest_root).reset().write()


class NetworkTests(unittest.TestCase):
    def testGeneratingPkgIndex(self):
        warnings.warn('implement me!')
        pass


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


#if __name__ == '__main__': unittest.main()
