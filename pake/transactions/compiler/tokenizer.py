#!/usr/bin/env python3

"""This is used to tokenize Metal source files.
"""


from . import errors, shared


keywords = shared.getkeywords()
grammar_chars = shared.getgrammarchars()


def dequote(s):
    """Remove quotes from string ends.
    If string is empty - returns empty string.
    If string has length equal to 1 - return this string without dequoting.
    """
    if type(s) is not str: raise TypeError('expected string but got {0}'.format(type(s)))
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"': s = s[1:-1]
    elif len(s) >= 2 and s[0] == "'" and s[-1] == "'": s = s[1:-1]
    else: raise errors.MetalSyntaxError('unable to dequote string: {0}'.format(repr(s)))
    return s


def candequote(s):
    """Returns True if string can be dequoted.
    False otherwise.
    """
    result = True
    try: dequote(s)
    except SyntaxError: result = False
    finally: return result


def decomment(tokens):
    """Removes comments from tokens.
    This should be handled by translator but now it's here so that the code doesn't get bloated.
    It will be integrated into translator after a good design way is found.
    """
    decommented = []
    i = 0
    appending = True
    # comment can be:
    #   0   - no comment, append normally
    #   1   - single line, stop appending until next newline
    #   2   - block comment, stop appending until closing block comment
    comment = 0
    while i < len(tokens):
        line, tok = tokens[i]
        if comment == 0 and tok == '//': comment = 1
        elif comment == 0 and tok == '/*': comment = 2
        if comment == 0: decommented.append((line, tok))
        if (comment == 1 and tok == '\n') or (comment == 2 and tok == '*/'): comment = 0
        i += 1
    return decommented


def strip(tokens):
    """Strips tokens which contain only whitespace.
    """
    stripped = [(line, tok) for line, tok in tokens if tok.strip() != '']
    return stripped


def getlinecount(tokens):
    """Returns number of lines in a tokenized file.
    """
    n = -1
    for line, tok in tokens:
        if line > n: n = line
    return n+1


def getline(n, tokens, lined=True):
    """Returns tokens from the physical source code line with given index.
    Negative indexes return lines counted from the end of the file.

    :param n: line number to rebuild (must be lesser than the number of line in the tokenized file)
    :param tokens: tokens used for rebuilding
    """
    if n < 0: n = getlinecount(tokens)+n
    words = []
    for l, tok in tokens:
        if l == n:
            if lined: part = (l, tok)
            else: part = tok
            words.append(part)
    # this check will raise IndexError if given line index is greater than number of lines in tokenized file
    if words[-1] == '\n': words = words[:-1]
    return words


def rebuild(n, tokens):
    """Returns string containing physical line with given index.

    :param n: index of physical line
    :param tokens: tokenized source code
    """
    return ''.join(getline(n, tokens, lined=False))


def tokenize(string):
    """This function will tokenize the string.
    """
    tokens = []
    word = ""
    line = 0
    token = None
    for i in range(len(string)):
        char = string[i]

        if ((char == '"' and word and word[0] == '"') or (char == "'" and word and word[0] == "'")) and (word and word[-1] != '\\'):
            # support for strings
            word += char
            token = (line, word)
            tokens.append(token)
            word = ""
        elif (char == '"' and word and word[0] not in ['"', "'"]) or (char == "'" and word and word[0] not in ['"', "'"]):
            token = (line, word)
            tokens.append(token)
            word = char
        elif char == " " and word and (word[0] in ['"', "'"] or word[:2] == '//'):
            # don't finish word on whitespace if in string or comment
            word += char
        elif char in grammar_chars and word and (word[0] in ['"', "'"] or word[:2] == '//'):
            # don't finish word on grammar characters if in string or comment
            word += char
        elif char in grammar_chars or char == ' ':
            # finish word on grammar characters and whitespace
            token = (line, word)
            if word: tokens.append(token)
            token = (line, char)
            tokens.append(token)
            word = ''
        elif char == '\n':
            # finish word on newline
            token = (line, word)
            if word: tokens.append(token)
            token = (line, char)
            tokens.append(token)
            if word and ((word[0] == '"' and word[-1] != '"') or (word[0] == "'" and word[0] != "'")):
                raise errors.CompilationError('strings cannot be broken by newlines: line {0}: {1}'.format(line, rebuild(line, tokens)))
            line += 1
            word = ''
        else:
            word += char
    token = (line, word)
    if word: tokens.append(token)
    return tokens
