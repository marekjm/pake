#!/usr/bin/env python3


"""This program joins tokens which require this eg. floating point numbers.
It is used as a second step after tokenization to keep tokenizing code simpler.
"""


import re

from . import shared


def _joinfloats(tokens, with_lines):
    """Joins floating point numbers into single tokens.
    """
    joined = []
    i = 0
    while i < len(tokens):
        line, token = tokens[i]
        if shared.isinteger(token):
            if i < len(tokens)-2:
                if tokens[i+1][1] == '.' and shared.ismantissa(tokens[i+2][1]):
                    # joining ordinary floats
                    token = '{0}.{1}'.format(token, tokens[i+2][1])
                    i += 2
        elif token == '.' and i < len(tokens)-1 and shared.ismantissa(tokens[i+1][1]):
            # joining incomplete floats
            token = '0.{0}'.format(tokens[i+1][1])
            i += 1
        elif len(token) >= 2 and (token[:-1].isdigit() and token[-1] == 'e'):
            if i < len(tokens)-2 and tokens[i+1][1] in ['+', '-'] and shared.isinteger(tokens[i+2][1]):
                # joining mantissa containing expotential number
                token = '{0}{1}{2}'.format(token, tokens[i+1][1], tokens[i+2][1])
                i += 2
        joined.append((line, token))
        i += 1
    return joined


def _joinincrement(tokens, with_lines):
    """Join increment operators (two + characters) into single tokens.
    """
    joined = []
    i = 0
    source = tokens
    while i < len(tokens):
        line, token = tokens[i]
        if token == '+' and i < len(tokens)-1 and tokens[i+1][1] == '+':
            token = '++'
            i += 1
        i += 1
        joined.append((line, token))
    return joined


def _joindecrement(tokens, with_lines):
    """Join decrement operators (two - characters) into single tokens.
    """
    joined = []
    i = 0
    source = tokens
    while i < len(tokens):
        line, token = tokens[i]
        if token == '-' and i < len(tokens)-1 and tokens[i+1][1] == '-':
            token = '--'
            i += 1
        i += 1
        joined.append((line, token))
    return joined


def _joinequals(tokens, with_lines):
    """Joins various operators that consist of some grammar character and equality sign.
    """
    joined = []
    i = 0
    source = tokens
    while i < len(tokens):
        line, token = tokens[i]
        if token in ['=', '!', '+', '-', '*', '/', '^'] and i < len(tokens)-1 and tokens[i+1][1] == '=':
            token = '{0}='.format(token)
            i += 1
        i += 1
        joined.append((line, token))
    return joined


def join(tokens):
    """Returns list of tokens after joining process.
    Joining involves joining several tokens together when they make sense this way, e.g.
    floating point numbers, `!=` operator, increment/decrement operators and operators which are
    formed from more than one grammar character.
    """
    joined = []
    if type(tokens[0]) == tuple: with_lines = True
    else: with_lines=False
    # list of joining functions
    joining = [_joinfloats, _joinincrement, _joindecrement, _joinequals]
    for func in joining:
        while True:
            joined = func(tokens, with_lines=with_lines)
            if joined == tokens: break  # this means that there is nothing more to join
            tokens = joined
    return joined
