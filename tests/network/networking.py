#!/usr/bin/env python3

"""This is PAKE networking test suite.
"""


import unittest


from tests import helpers


class Suite():
    """Wrapper class for all tests.
    It must inerit methods from all test classes.
    """
    pass


if __name__ == '__main__':  # in case only networking tests are run
    unittest.main()
