#!/usr/bin/env python3

"""This file contains PAKE transactions parser code.
"""

from pake import errors

class Parser():
    """This object can be used to parse PAKE transaction files.

    It takes a file and converts it to a form that can be understood by PAKE
    interpreter.
    """
    def __init__(self, path):
        self._path = path
        self._lines = []
        self._parsed = []

    def _readlines(self):
        """Reads lines of file that _path points to.
        """
        ifstream = open(self._path, 'r')
        self._lines = [line.strip() for line in ifstream.readlines()]
        ifstream.close()

    def _purgelines(self):
        """This will purge empty lines and comments from read lines.
        """
        self._lines = [l for l in self._lines if l != '']       # purge empty lines
        self._lines = [l for l in self._lines if l[0] != '#']   # purge comments

    def _splitlines(self):
        """Splits read lines.
        """
        self._lines = [l.split(' ') for l in self._lines]

    def load(self):
        """Load file lines into object's memory.
        """
        self._readlines()
        self._purgelines()
        self._splitlines()
        return self

    def _parseline(self, line, req_name, args=[]):
        """Parse line and returns dictionary representing request.

        args are list of two-tuples containg `ARGUMENT_NAME` and `request_name`.
        `ARGUMENT_NAME` is a string looke for in list of words passed and
        `request_name` is a name under which it is saved in request dictionary.
        """
        request = {'req': req_name}
        if len(line) < 2: raise SyntaxError('no package name to install: {0}'.format(self._path))
        if line[1] in args: raise SyntaxError('no package name to install: {0}'.format(self._path))
        request['name'] = line[1]
        line = line[2:]  # removing obligatory elements of the line
        for arg, req in args:  # checking for optional elements
            if arg in line:
                n = line.index(arg)
                target = line[n+1]
                if target in args: # check whether target is another argument - it's a syntax error
                    raise SyntaxError('argument without target in file: {0}: {1}'.format(self._path, arg))
                request[req] = target
            else:
                n = -1  # indicate that given arg was not found
            if n > -1: del line[n:n+2]  # remove used words from the line
        # if any words can be found in the statement it means that
        # it is invalid as it contains words that were not caught by parser
        if line:
            raise SyntaxError('invalid FETCH statement in file: {0}'.format(self._path))
        return request

    def _parsefetch(self, line):
        """Takes list of words found in line containing FETCH statement and
        returns request dictionary built from them.
        """
        args = [('FROM', 'origin'), ('VERSION', 'version')]
        return self._parseline(line=line, req_name='fetch', args=args)

    def _parseinstall(self, line):
        """Takes list of words found in line containing INSTALL statement and
        returns request dictionary built from them.
        """
        args = [('VERSION', 'version')]
        return self._parseline(line=line, req_name='install', args=args)

    def parse(self):
        """This method parses read lines into a form that can be understood by
        interpreter.
        """
        parsed = []
        for line in self._lines:
            request = {}
            keyword = line[0]
            if keyword == 'FETCH':
                request = self._parsefetch(line)
            elif keyword == 'INSTALL':
                request = self._parseinstall(line)
            else:
                raise SyntaxError('unknown keyword found in file: {0}: {1}'.format(self._path, keyword))
            parsed.append(request)
        self._parsed = parsed
        return self

    def getlines(self):
        """Returns file lines stored in object's memory.
        """
        return self._lines

    def getparsed(self):
        """Returns parsed code.
        """
        return self._parsed


class Encoder():
    """This object can encode middle-form representation of transactions
    back to the source code.
    """
    def __init__(self, parsed):
        self._parsed = parsed  # this is middle-form of transaction
        self._source = []

    def _encodeline(self, statement, st_name, args=[]):
        """Create list of words in source code line encoded from
        moddle form of translated statement.
        """
        line = [st_name]
        line.append(statement['name'])
        for arg, req in args:
            if req in statement:
                line.append(arg)
                line.append(statement[req])
        return line

    def _encodefetch(self, statement):
        """Encode FETCH statement.
        """
        args = [('VERSION', 'version'), ('FROM', 'origin')]
        return self._encodeline(statement=statement, st_name='FETCH', args=args)

    def _encodeinstall(self, statement):
        """Encode INSTALL statement.
        """
        args = [('VERSION', 'version'), ('FROM', 'origin')]
        return self._encodeline(statement=statement, st_name='INSTALL', args=args)

    def encode(self):
        """Create source code from the middle-form representation of
        the transaction.
        """
        source = []
        for statement in self._parsed:
            st = statement['req']
            if st == 'fetch': source.append(self._encodefetch(statement))
            elif st == 'install': source.append(self._encodeinstall(statement))
            else: raise errors.EncodingError('does not know how to encode \'{0}\' statement'.format(st))
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
