#!/usr/bin/env python3

"""This object contains functions and objects needed for
encoding transactions to source code from their middle-form
created by parser or PAKE itself.
"""


from pake import errors
from pake.transactions import shared


class Encoder():
    """This object can encode middle-form representation of transactions
    back to the source code.
    """
    def __init__(self, parsed):
        self._parsed = parsed  # this is middle-form of transaction
        self._source = []

    def _encodeline(self, statement, args=[]):
        """Create list of words in source code line encoded from
        middle form of translated statement.

        This method uses repr() function on all arguments so they will be enquoted.
        It is required for correct encoding of META statements where VALUE subkeywords can
        have arguments containing spaces.
        """
        line = [statement['req']]  # set main KEYWORD
        line.append(statement['context'])  # set context
        req_name = [kw for kw, req, argno, conflicts in args if kw == statement['req']][0]
        line.append(repr(statement[statement['context'].lower()]))  # append argument for context
        for kw, req, argno, conflicts in args:
            if kw in [statement['context'], statement['req']]: continue  # don't add it second time - it's the main KEYWORD or context
            if req in statement:
                line.append(kw)
                line.append(repr(statement[req]))
        return line

    def _encodepkg(self, statement):
        """Encodes PKG statements.
        """
        return self._encodeline(statement=statement, args=shared.statement_subkeywords_for_pkg)

    def _encodefetch(self, statement):
        """Encode FETCH statement.
        """
        return self._encodeline(statement=statement, st_name='FETCH', args=shared.fetch_statement_subkeywords)

    def _encodeinstall(self, statement):
        """Encode INSTALL statement.
        """
        return self._encodeline(statement=statement, st_name='INSTALL', args=shared.install_statement_subkeywords)

    def _encoderemove(self, statement):
        """Encode INSTALL statement.
        """
        return self._encodeline(statement=statement, st_name='REMOVE', args=shared.remove_statement_subkeywords)

    def _encodemeta(self, statement):
        """Encode META statement.
        """
        return self._encodeline(statement=statement, st_name='META', args=shared.meta_statement_subkeywords)

    def encode(self):
        """Create source code from the middle-form representation of
        the transaction.
        """
        source = []
        for statement in self._parsed:
            st = statement['req']
            if st == 'fetch':
                source.append(self._encodefetch(statement))
            elif st == 'install':
                source.append(self._encodeinstall(statement))
            elif st == 'remove':
                source.append(self._encoderemove(statement))
            elif st == 'meta':
                source.append(self._encodemeta(statement))
            elif st == 'PKG':
                source.append(self._encodepkg(statement))
            else:
                raise errors.EncodingError('does not know how to encode \'{0}\' statement'.format(st))
        self._source = source
        return self

    def getsource(self, joined=True):
        """Get lines of source generated code.

        :param joined: if True words will be joined with whitespace
        """
        if joined: return [' '.join(l) for l in self._source]
        else: return [l for l in self._source]

    def dump(self, path):
        """Write source to the file specified during initialization
        of the object.
        """
        ofstream = open(path, 'w')
        for line in self.getsource(): ofstream.write('{0}\n'.format(line))
        ofstream.close()
