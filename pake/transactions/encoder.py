#!/usr/bin/env python3

"""This object contains functions and objects needed for
encoding transactions to source code from their middle-form
created by parser or PAKE itself.
"""

import warnings


from pake import errors
from pake.transactions import shared


class Encoder():
    """This object can encode middle-form representation of transactions
    back to the source code.
    """
    def __init__(self, parsed):
        self._parsed = parsed  # this is middle-form of transaction
        self._source = []

    def encode(self):
        """Create source code from the middle-form representation of
        the transaction.
        """
        warnings.warn(NotImplemented)
        return self

    def getsource(self, joined=True):
        """Get lines of source generated code.

        :param joined: if True words will be joined with whitespace
        """
        return self._source

    def dump(self, path):
        """Write source to the file specified during initialization
        of the object.
        """
        ofstream = open(path, 'w')
        for line in self.getsource(): ofstream.write('{0}\n'.format(line))
        ofstream.close()
