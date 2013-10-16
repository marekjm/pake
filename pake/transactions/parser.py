#!/usr/bin/env python3

"""This file contains PAKE transactions parser code.
"""

from pake import errors
from pake.transactions import shared


def dequote(s):
    """Remove quotes from string ends.
    """
    if not s: return s  # return empty string
    if len(s) == 1: return s  # string is single char and thus can't be dequoted
    if s[0] == '"' and s[-1] == '"': s = s[1:-1]
    elif s[0] == "'" and s[-1] == "'": s = s[1:-1]
    return s


def tokenize(line, dequoted=False):
    """This function will tokenize the line.

    :param dequoted: if True - strings will have surrounding quotes removed
    :type dequoted: bool
    """
    tokens, word = [], ''
    for i in range(len(line)):
        char = line[i]
        if char == '"' and word and word[0] == '"':
            word += char
            if word: tokens.append(word)  # just don't append empty words
            word = ''  # reset word
        elif char == "'" and word and word[0] == "'":
            word += char
            if word: tokens.append(word)  # just don't append empty words
            word = ''  # reset word
        elif char == ' ' and word and word[0] in ['"', "'"]:
            word += char
        elif char == ' ':
            if word: tokens.append(word)  # just don't append empty words
            word = ''  # reset word
        else:
            word += char
    if word: tokens.append(word)
    if dequoted: tokens = [dequote(word) for word in tokens]
    return tokens


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

    def _tokenizelines(self):
        """Tokenize read lines.
        """
        self._lines = [tokenize(l, dequoted=True) for l in self._lines]

    def load(self):
        """Load file lines into object's memory.
        """
        self._readlines()
        self._purgelines()
        self._tokenizelines()
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
        for arg, req in args:  # checking for optional elements
            if arg in line:
                n = line.index(arg)  # index of the subkeyword
                target = line[n+1]   # argument comes next
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
        return self._parseline(line=line, req_name='fetch', args=shared.fetch_statement_subkeywords)

    def _parseinstall(self, line):
        """Takes list of words found in line containing INSTALL statement and
        returns request dictionary built from them.
        """
        return self._parseline(line=line, req_name='install', args=shared.install_statement_subkeywords)

    def _parseremove(self, line):
        """Takes list of words found in line containing REMOVE statement and
        returns request dictionary built from them.
        """
        return self._parseline(line=line, req_name='remove', args=shared.remove_statement_subkeywords)

    def _parsemeta(self, line):
        """Parse meta manipulation request and
        return appropriate translation into middle-form.
        """
        return self._parseline(line=line, req_name='meta', args=shared.meta_statement_subkeywords)

    def parse(self):
        """This method parses read lines into a form that can be understood by
        interpreter.
        """
        parsed = []
        for line in self._lines:
            request = {}
            keyword = line[0]  # main keyword is always first - if it's not it's a SyntaxError
            if keyword == 'FETCH':
                request = self._parsefetch(line)
            elif keyword == 'INSTALL':
                request = self._parseinstall(line)
            elif keyword == 'REMOVE':
                request = self._parseremove(line)
            elif keyword == 'META':
                request = self._parsemeta(line)
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
