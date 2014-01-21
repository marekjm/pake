#!/usr/bin/env python3

"""Functions shared between various Metal modules.
"""

import json
import os
import re


from ... import shared as pakeshared


valid_name_re = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')


def isvalidname(name):
    return valid_name_re.match(name) is not None


def isvalidreference(s):
    parts = s.split('.')
    ok = True
    for part in parts:
        ok = isvalidname(part)
        if not ok: break
    return ok


def getkeywords():
    """Returns list of reserved keywords.
    """
    ifstream = open(os.path.join(pakeshared.getenvpath(), 'transactions', 'lang', 'keywords.json'))
    content = ifstream.read()
    ifstream.close()
    return json.loads(content)


def getgrammarchars():
    """Returns list of grammar chars.
    """
    ifstream = open(os.path.join(pakeshared.getenvpath(), 'transactions', 'lang', 'grammar_chars.json'))
    content = ifstream.read()
    ifstream.close()
    return json.loads(content)
