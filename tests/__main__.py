import unittest
import tests


class SystemTests(tests.system.Suite):
    pass


class SystemTransactionsTests(tests.systemtransactions.Suite):
    pass


if __name__ == '__main__':
    tests.helpers.prepare(tests.conf.testdir)
    unittest.main()
