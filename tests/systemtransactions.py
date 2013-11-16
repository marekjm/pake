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
        runner = pake.transactions.runner.Runner(root=testdir, requests=[{'act': 'node.manager.init', 'path': testdir}])
        ifstream = open('./env/node/required/directories.json')
        directories = json.loads(ifstream.read())
        ifstream.close()
        # test logic
        runner.run()
        self.assertIn('.pakenode', os.listdir(testdir))
        for d in directories:
            path = os.path.join(test_node_root, d)
            self.assertEqual(True, os.path.isdir(path))
        # cleanup
        helpers.rmnode(testdir)

    def testNodeManagerConfigWriting(self):
        """This test checks for correct intialization of all required config files.
        """
        runner = pake.transactions.runner.Runner(root=testdir, requests=[{'act': 'node.manager.init', 'path': testdir}])
        configs = [ ('meta.json', {}),      # (filename, desired_content)
                    ('pushers.json', []),
                    ('aliens.json', {}),
                    ('nests.json', {}),
                    ]
        # test logic
        runner.run()
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
        helpers.gennode(testdir)
        runner = pake.transactions.runner.Runner(root=testdir, requests=[{'act': 'node.manager.remove', 'path': testdir}])
        # code logic & cleanup - in this test it's the same
        runner.run()
        self.assertNotIn('.pakenode', os.listdir(testdir))


class NodeConfigurationTests(unittest.TestCase):
    """Code for Meta() is shared between node and
    nest configuration interface so it's only tested here.

    Any tests passing for node will also pass for nests.
    """
    def testSettingKeyInMeta(self):
        reqs = [{'act': 'node.manager.init', 'path': testdir},
                {'act': 'node.config.meta.set', 'key': 'foo', 'value': 'bar'}]
        # test logic
        pake.transactions.runner.Runner(root=testdir, requests=reqs).run()
        self.assertEqual(pake.config.node.Meta(test_node_root).get('foo'), 'bar')
        # cleanup
        helpers.rmnode(testdir)

    def testRemovingKeyFromMeta(self):
        reqs = [{'act': 'node.manager.init', 'path': testdir},
                {'act': 'node.config.meta.set', 'key': 'foo', 'value': 'bar'},
                {'act': 'node.config.meta.remove', 'key': 'foo'}]
        # test logic
        pake.transactions.runner.Runner(root=testdir, requests=reqs).run()
        self.assertEqual(dict(pake.config.node.Meta(test_node_root)), {})
        # cleanup
        helpers.rmnode(testdir)

    def testGettingValuesFromMeta(self):
        helpers.gennode(testdir)
        reqs = [{'act': 'node.config.meta.set', 'key': 'foo', 'value': 'bar'},
                {'act': 'node.config.meta.get', 'key': 'foo'}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        self.assertEqual('bar', runner.getstack()[-1])
        # cleanup
        helpers.rmnode(testdir)

    def testGettingMetaKeys(self):
        helpers.gennode(testdir)
        reqs = [{'act': 'node.config.meta.set', 'key': 'foo', 'value': 0},
                {'act': 'node.config.meta.set', 'key': 'bar', 'value': 1},
                {'act': 'node.config.meta.set', 'key': 'baz', 'value': 2},
                {'act': 'node.config.meta.getkeys'},
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        self.assertEqual(['bar', 'baz', 'foo'], sorted(runner.getstack()[-1]))
        self.assertEqual(['bar', 'baz', 'foo'], sorted(pake.config.node.Meta(test_node_root).keys()))
        pake.config.node.Meta(test_node_root).reset().write()
        # cleanup
        helpers.rmnode(testdir)

    def testAddingPusher(self):
        reqs = [{'act': 'node.manager.init', 'path': testdir},
                {'act': 'node.config.mirrors.set', 'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
                ]
        pake.transactions.runner.Runner(root=testdir, requests=reqs).run()
        # test logic
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        self.assertIn(pusher, pake.config.node.Pushers(test_node_root))
        # cleanup
        helpers.rmnode(testdir)

    def testRemovingPusher(self):
        reqs = [{'act': 'node.manager.init', 'path': testdir},
                {'act': 'node.config.mirrors.set', 'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'},
                {'act': 'node.config.mirrors.remove', 'url': 'http://pake.example.com'},
                ]
        pake.transactions.runner.Runner(root=testdir, requests=reqs).run()
        # test logic
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        self.assertNotIn(pusher, pake.config.node.Pushers(test_node_root))
        # cleanup
        helpers.rmnode(testdir)

    def testGettingPusher(self):
        helpers.gennode(testdir)
        reqs = [{'act': 'node.config.mirrors.set', 'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'},
                {'act': 'node.config.mirrors.get', 'url': 'http://pake.example.com'}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        pusher = {'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'}
        self.assertEqual(pusher, runner.getstack()[-1])
        # cleanup
        helpers.rmnode(testdir)

    def testMirrorlistGeneration(self):
        helpers.gennode(testdir)
        reqs = [{'act': 'node.config.mirrors.set', 'url': 'http://pake.example.com', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'},
                {'act': 'node.config.mirrors.set', 'url': 'http://pake.example.net', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'},
                {'act': 'node.config.mirrors.set', 'url': 'http://pake.example.org', 'host': 'example.com', 'cwd': '/domains/example.com/public_html/pake'},
                {'act': 'node.config.mirrors.genlist'},
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_node_root, 'mirrors.json'))
        self.assertEqual(['http://pake.example.com', 'http://pake.example.net', 'http://pake.example.org'], json.loads(ifstream.read()))
        ifstream.close()
        # cleanup
        helpers.rmnode(testdir)

    def testAddingAlien(self):
        helpers.gennode(testdir)
        reqs = [{'act': 'node.config.aliens.set', 'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}]
        pake.transactions.runner.Runner(root=testdir, requests=reqs).run()
        # test logic
        alien = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        self.assertIn('http://alien.example.com', list(pake.config.node.Aliens(test_node_root)))
        # cleanup
        helpers.rmnode(testdir)

    def testRemovingAlien(self):
        helpers.gennode(testdir)
        reqs = [{'act': 'node.config.aliens.set', 'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}},
                {'act': 'node.config.aliens.remove', 'url': 'http://alien.example.com'}
                ]
        pake.transactions.runner.Runner(root=testdir, requests=reqs).run()
        # test logic
        alien = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        self.assertNotIn('http://alien.example.com', pake.config.node.Aliens(test_node_root))
        # cleanup
        helpers.rmnode(testdir)

    def testGettingAlien(self):
        helpers.gennode(testdir)
        reqs = [{'act': 'node.config.aliens.set', 'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}},
                {'act': 'node.config.aliens.get', 'url': 'http://alien.example.com'}
                ]
        # test logic
        self.assertEqual({'mirrors': [], 'meta': {}}, pake.transactions.runner.Runner(root=testdir, requests=reqs).run().getstack()[-1])
        # cleanup
        helpers.rmnode(testdir)

    def testListingAlienURLs(self):
        helpers.gennode(testdir)
        reqs = [{'act': 'node.config.aliens.set', 'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}},
                {'act': 'node.config.aliens.set', 'url': 'http://alien.example.net', 'mirrors': [], 'meta': {}},
                {'act': 'node.config.aliens.set', 'url': 'http://alien.example.org', 'mirrors': [], 'meta': {}}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        urls = ['http://alien.example.com', 'http://alien.example.net', 'http://alien.example.org']
        self.assertEqual(urls, sorted(pake.config.node.Aliens(test_node_root).urls()))
        # cleanup
        helpers.rmnode(testdir)

    def testListingAliens(self):
        helpers.gennode(testdir)
        reqs = [{'act': 'node.config.aliens.set', 'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}},
                {'act': 'node.config.aliens.set', 'url': 'http://alien.example.net', 'mirrors': [], 'meta': {}},
                {'act': 'node.config.aliens.set', 'url': 'http://alien.example.org', 'mirrors': [], 'meta': {}},
                {'act': 'node.config.aliens.getall'}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        foo = {'url': 'http://alien.example.com', 'mirrors': [], 'meta': {}}
        bar = {'url': 'http://alien.example.net', 'mirrors': [], 'meta': {}}
        baz = {'url': 'http://alien.example.org', 'mirrors': [], 'meta': {}}
        # test logic
        runner.run()
        aliens = runner.getstack()[-1]
        self.assertIn(foo, aliens)
        self.assertIn(bar, aliens)
        self.assertIn(baz, aliens)
        # cleanup
        helpers.rmnode(testdir)

    def testRegisteringNest(self):
        helpers.gennode(testdir)
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.meta.set', 'key': 'name', 'value': 'test'},
                {'act': 'node.config.nests.register', 'path': testdir}]
        pake.transactions.runner.Runner(root=testdir, requests=reqs).run()
        # test logic
        self.assertEqual(os.path.abspath(test_nest_root), pake.config.node.Nests(test_node_root).get('test'))
        # cleanup
        helpers.rmnode(testdir)
        helpers.rmnest(testdir)

    def testRemovingNest(self):
        helpers.gennode(testdir)
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.meta.set', 'key': 'name', 'value': 'test'},
                {'act': 'node.config.nests.register', 'path': testdir},
                {'act': 'node.config.nests.remove', 'name': 'test'}]
        pake.transactions.runner.Runner(root=testdir, requests=reqs).run()
        # test logic
        self.assertRaises(KeyError, pake.config.node.Nests(test_node_root).get, 'test')
         # cleanup
        helpers.rmnode(testdir)
        helpers.rmnest(testdir)

    def testGettingPathOfOneNest(self):
        helpers.gennode(testdir)
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.meta.set', 'key': 'name', 'value': 'test'},
                {'act': 'node.config.nests.register', 'path': testdir},
                {'act': 'node.config.nests.get', 'name': 'test'},
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        self.assertEqual(os.path.abspath(test_nest_root), runner.getstack()[-1])
        self.assertEqual(os.path.abspath(test_nest_root), pake.config.node.Nests(test_node_root).get('test'))
        # cleanup
        helpers.rmnode(testdir)
        helpers.rmnest(testdir)

    def testGettingPathsOfAllNests(self):
        helpers.gennode(testdir)
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.meta.set', 'key': 'name', 'value': 'test'},
                {'act': 'node.config.nests.register', 'path': testdir},
                {'act': 'node.config.nests.getpaths'}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        self.assertEqual([os.path.abspath(test_nest_root)], runner.run().getstack()[-1])
        # cleanup
        helpers.rmnode(testdir)
        helpers.rmnest(testdir)

    def testBuildingPackageList(self):
        helpers.gennode(testdir)
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.meta.set', 'key': 'name', 'value': 'foo'},
                {'act': 'node.config.nests.register', 'path': testdir},
                {'act': 'node.packages.genlist'},
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run(fatalwarns=True)
        desired = ['foo']
        ifstream = open(os.path.join(test_node_root, 'packages.json'))
        pkgs = json.loads(ifstream.read())
        ifstream.close()
        self.assertEqual(desired, pkgs)
        # cleanup
        helpers.rmnode(testdir)
        helpers.rmnest(testdir)


class NodePushingTests(unittest.TestCase):
    @unittest.skip('')
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
            pake.config.node.Pushers(test_node_root).add(url=url, host=host, cwd=cwd).write()
            pake.node.packages.register(root=test_node_root, path=test_nest_root)
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
        pake.transactions.runner.Runner(root=testdir, requests=[{'act': 'nest.manager.init', 'path': testdir}]).run()
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
        runner = pake.transactions.runner.Runner(root=testdir, requests=[{'act': 'nest.manager.init', 'path': testdir}])
        # (filename, desired_content)
        runner.run()
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
        runner = pake.transactions.runner.Runner(root=testdir, requests=[{'act': 'nest.manager.remove', 'path': testdir}])
        # test logic & cleanup
        runner.run()
        self.assertNotIn('.pakenest', os.listdir(testdir))


class NestConfigurationTests(unittest.TestCase):
    def testAddingVersions(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.versions.add', 'version': '0.0.1-alpha.1'},
                {'act': 'nest.config.versions.add', 'version': '0.0.1-beta.1'},
                {'act': 'nest.config.versions.add', 'version': '0.0.1-rc.1'},
                {'act': 'nest.config.versions.add', 'version': '0.0.1'},
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        self.assertEqual(['0.0.1-alpha.1', '0.0.1-beta.1', '0.0.1-rc.1', '0.0.1'], list(pake.config.nest.Versions(test_nest_root)))
        # cleanup
        helpers.rmnest(testdir)

    def testAddingVersionsButCheckingIfItsNotLowerThanTheLastOne(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.versions.add', 'version': '0.0.1-beta.1'},
                {'act': 'nest.config.versions.add', 'version': '0.0.1-alpha.17', 'check': True}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        self.assertRaises(ValueError, runner.run)
        # assertNotRaises -- just run it; if no exception is raise everything's fine
        reqs = [{'act': 'nest.config.versions.add', 'version': '0.0.1-beta.1'},
                {'act': 'nest.config.versions.add', 'version': '0.0.1', 'check': True}
                ]
        pake.transactions.runner.Runner(root=testdir, requests=reqs).run()
        # cleanup
        helpers.rmnest(testdir)

    def testRemovingVersions(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.versions.add', 'version': '0.0.1-beta.1'},
                {'act': 'nest.config.versions.remove', 'version': '0.0.1-beta.1'}
                ]
        pake.transactions.runner.Runner(root=testdir, requests=reqs).run()
        # test logic
        self.assertEqual([], list(pake.config.nest.Versions(test_nest_root)))
        # cleanup
        helpers.rmnest(testdir)

    def testAddingADependency(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingADependencyWithSpecifiedOrigin(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo', 'origin': 'http://pake.example.com'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'origin': 'http://pake.example.com'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingADependencyWithSpecifiedMinimalVersion(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo', 'min': '0.2.4'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'min': '0.2.4'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingADependencyWithSpecifiedMaximalVersion(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo', 'max': '2.4.8'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'max': '2.4.8'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingADependencyWithFullSpecification(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo', 'origin': 'http://pake.example.com', 'min': '0.2.4', 'max': '2.4.8'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'origin': 'http://pake.example.com', 'min': '0.2.4', 'max': '2.4.8'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testRemovingADependency(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo', 'origin': 'http://pake.example.com', 'min': '0.2.4', 'max': '2.4.8'},
                {'act': 'nest.config.dependencies.remove', 'name': 'foo'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testRedefiningADependency(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo', 'origin': 'http://pake.example.com', 'min': '0.2.4', 'max': '2.4.8'},
                {'act': 'nest.config.dependencies.set', 'name': 'foo', 'origin': 'http://pake.example.org'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'origin': 'http://pake.example.org'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testUpdatingADependency(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo', 'origin': 'http://pake.example.com', 'min': '0.2.4', 'max': '2.4.8'},
                {'act': 'nest.config.dependencies.update', 'name': 'foo', 'origin': 'http://pake.example.org'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_nest_root, 'dependencies.json'))
        dep = json.loads(ifstream.read())
        ifstream.close()
        desired = {'foo': {'origin': 'http://pake.example.org', 'min': '0.2.4', 'max': '2.4.8'}}
        self.assertEqual(desired, dep)
        # cleanup
        helpers.rmnest(testdir)

    def testGettingDependencyData(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo', 'origin': 'http://pake.example.com', 'min': '0.2.4', 'max': '2.4.8'},
                {'act': 'nest.config.dependencies.get', 'name': 'foo'}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        #pake.config.nest.Dependencies(test_nest_root).set(name='foo', origin='http://pake.example.com', min='0.2.4', max='2.4.8').write()
        desired = {'origin': 'http://pake.example.com', 'min': '0.2.4', 'max': '2.4.8'}
        #self.assertEqual(desired, pake.config.nest.Dependencies(test_nest_root).get(name='foo'))
        self.assertEqual(desired, runner.getstack()[-1])
        # cleanup
        helpers.rmnest(testdir)

    def testListingDependenciesNames(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo'},
                {'act': 'nest.config.dependencies.set', 'name': 'bar'},
                {'act': 'nest.config.dependencies.set', 'name': 'baz'},
                {'act': 'nest.config.dependencies.getnames'}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        #pake.config.nest.Dependencies(test_nest_root).set(name='foo').set(name='bar').set(name='baz').write()
        desired = ['foo', 'bar', 'baz']
        self.assertEqual(sorted(desired), sorted(list(pake.config.nest.Dependencies(test_nest_root))))
        self.assertEqual(sorted(desired), sorted(runner.getstack()[-1]))
        # cleanup
        helpers.rmnest(testdir)

    def testListingDependenciesDetails(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.dependencies.set', 'name': 'foo'},
                {'act': 'nest.config.dependencies.set', 'name': 'bar', 'origin': 'http://pake.example.com'},
                {'act': 'nest.config.dependencies.set', 'name': 'baz', 'origin': 'http://pake.example.net', 'min': '0.2.4'},
                {'act': 'nest.config.dependencies.list'}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        deps = runner.getstack()[-1]
        self.assertIn({'name': 'foo'}, deps)
        self.assertIn({'name': 'bar', 'origin': 'http://pake.example.com'}, deps)
        self.assertIn({'name': 'baz', 'origin': 'http://pake.example.net', 'min': '0.2.4'}, deps)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingFile(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.files.add', 'path': './pake/__init__.py'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_nest_root, 'files.json'))
        files = json.loads(ifstream.read())
        ifstream.close()
        desired = ['./pake/__init__.py']
        self.assertEqual(desired, files)
        # cleanup
        helpers.rmnest(testdir)

    def testRemovingFile(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.files.add', 'path': './pake/__init__.py'}, {'act': 'nest.config.files.remove', 'path': './pake/__init__.py'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        ifstream = open(os.path.join(test_nest_root, 'files.json'))
        files = json.loads(ifstream.read())
        ifstream.close()
        self.assertEqual([], files)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingFileFailsIfFileHasAlreadyBeenAdded(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.files.add', 'path': './pake/__init__.py'},
                {'act': 'nest.config.files.add', 'path': './pake/__init__.py'}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        self.assertRaises(FileExistsError, runner.run)
        # cleanup
        helpers.rmnest(testdir)

    def testAddingFileFailsIfPathIsNotAFile(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.files.add', 'path': './this_file_does_not.exist'}]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        self.assertRaises(pake.errors.NotAFileError, runner.run)
        # cleanup
        helpers.rmnest(testdir)

    def testListingFiles(self):
        helpers.gennest(testdir)
        reqs = [{'act': 'nest.config.files.add', 'path': './pake/__init__.py'},
                {'act': 'nest.config.files.add', 'path': './pake/shared.py'},
                {'act': 'nest.config.files.list'}
                ]
        runner = pake.transactions.runner.Runner(root=testdir, requests=reqs)
        # test logic
        runner.run()
        desired = ['./pake/__init__.py', './pake/shared.py']
        self.assertEqual(desired, runner.getstack()[-1])
        # cleanup
        helpers.rmnest(testdir)


class NestReleaseBuildingTests(unittest.TestCase):
    @unittest.skip('')
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

    @unittest.skip('')
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

    @unittest.skip('')
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

    @unittest.skip('')
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

    @unittest.skip('')
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


if __name__ == '__main__':
    prepare(testdir)
    unittest.main()
