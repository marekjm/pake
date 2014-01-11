#!/usr/bin/env python3

"""Functions shared between various Metal modules.
"""

import json
import re


mantissa_regex = '[0-9]+(e[+-]?)?[0-9]+'
number_regex = '[1-9][0-9]*'

is_int_re = re.compile("^{0}$".format(number_regex))
is_bin_re = re.compile("^0b[0-1]+$")
is_oct_re = re.compile("^0o[0-7]+$")
is_hex_re = re.compile("^0x[0-9a-fA-F]+$")
is_float_re = re.compile("^({0})?\.{1}$".format(number_regex, mantissa_regex))

valid_name_re = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')


def isvalidname(name):
    return valid_name_re.match(name) is not None


def isnumeral(s):
    """Returns True if given string is a numeral primitive.
    """
    result = False
    checks = [is_int_re, is_bin_re, is_oct_re, is_hex_re, is_float_re]
    for func in checks:
        if func.match(s):
            result = True
            break
    return result

def isinteger(s):
    """Returns true if given string can be interpreted as integer.
    """
    return is_int_re.match(s)

def ismantissa(s):
    """Returns true if given string can be interpreted as mantissa in a float.
    """
    return re.compile('^{0}$'.format(mantissa_regex)).match(s)

def isfloat(s):
    """Returns true if given string can be converted into a float.
    """
    return is_float_re.match(s)


def getkeywords():
    """Returns list of reserved keywords.
    """
    ifstream = open('./env/keywords.json')
    content = ifstream.read()
    ifstream.close()
    return json.loads(content)


def getgrammarchars():
    """Returns list of grammar chars.
    """
    ifstream = open('./env/grammar_chars.json')
    content = ifstream.read()
    ifstream.close()
    return json.loads(content)
