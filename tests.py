#!/usr/bin/env python3


import json
import os
import shutil
import unittest

import pake


# global variables setup
testnoderoot = pake.shared.getrootpath(check=False, fake=os.path.abspath('./testdir'))
testreporoot = pake.shared.getrepopath(check=False, fake=os.path.abspath('./testdir'))


# test environment setup
if os.path.isdir(testnoderoot): shutil.rmtree(testnoderoot)
if os.path.isdir(testreporoot): shutil.rmtree(testreporoot)
pake.node.local.makedirs(root=testnoderoot)
pake.node.local.makeconfig(root=testnoderoot)


print()  # to make a one-line break between setup messages and actual test messages


class NodeInitializationTests(unittest.TestCase):
    def testDirectoriesWriting(self):
        """This test checks for correct initialization of all required directories.
        """
        directories = ['db', 'cache', 'installing', 'prepared']
        for d in directories:
            self.assertEqual(True, os.path.isdir(os.path.join(testnoderoot, d)))

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
        for f, desired in configs:
            ifstream = open(os.path.join(testnoderoot, f), 'r')
            self.assertEqual(desired, json.loads(ifstream.read()))
            ifstream.close()


if __name__ == '__main__': unittest.main()
