#!/usr/bin/env python3

"""This file contains PAKE transactions parser code.
"""


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

    def _parsefetch(self, line):
        """Takes list of words found in line containing FETCH statement and
        returns request dictionary built from them.
        """
        args = [('FROM', 'origin'), ('VERSION', 'version')]
        request = {'req': 'fetch'}
        if len(line) < 2: raise SyntaxError('no package name to fetch: {0}'.format(self._path))
        if line[1] in args: raise SyntaxError('no package name to fetch: {0}'.format(self._path))
        request['name'] = line[1]
        line = line[2:]  # removing obligatory elements of the line
        for arg, req in args:  # checking for optional elements
            if arg in line:
                n = line.index(arg)
                target = line[n+1]
                request[req] = target
            else:
                n = -1
            # remove used words from the line
            if n > -1: del line[n:n+2]
        return request

    def _parseinstall(self, line):
        """Takes list of words found in line containing INSTALL statement and
        returns request dictionary built from them.
        """
        args = [('VERSION', 'version')]
        request = {'req': 'install'}
        if len(line) < 2: raise SyntaxError('no package name to install: {0}'.format(self._path))
        if line[1] in args: raise SyntaxError('no package name to install: {0}'.format(self._path))
        request['name'] = line[1]
        line = line[2:]  # removing obligatory elements of the line
        for arg, req in args:  # checking for optional elements
            if arg in line:
                n = line.index(arg)
                target = line[n+1]
                request[req] = target
            else:
                n = -1
            # remove used words from the line
            if n > -1: del line[n:n+2]
        return request

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
