import unittest
import tests


class SystemTests(tests.system.Suite):
    pass


class SystemTransactionsTests(tests.systemtransactions.Suite):
    pass


# Before enabling network tests a fake network must be created, ergo - fully tested system-* part of PAKE
#class NetworkTransactionsTests(tests.networktransactions.Suite):


if __name__ == '__main__':
    tests.helpers.prepare(tests.conf.testdir)
    unittest.main()
