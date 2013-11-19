#!/usr/bin/env python3

"""Some tests are duplicated here and in systemtransactions.py
This is because some transactions can be told to act locally *or*
connect to the network.
"""

import unittest


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


class NodeConfigurationTests(unittest.TestCase):
    """Code for Meta() is shared between node and
    nest configuration interface so it's only tested here.

    Any tests passing for node will also pass for nests.
    """
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


if __name__ == '__main__':
    unittest.main()
else:
    class Suite(NodeConfigurationTests):
        """Wrapper class.
        """
        pass
