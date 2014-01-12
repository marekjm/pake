#!/usr/bin/env python3


"""Simple compiler for .pake metalanguage.

Usage: python3 metalcompiler.py [--switch] source.pake

SWITCHES:
    --tokenize          - only tokenize the source (print it out)
    --try               - try compiling the source (check for validity)


EXIT CODES:
    0   - everything went fine
    1   - given operand is not a file
    2   - unknown switch given


Copyright (c) 2014 Marek Marecki
"""


import json
import os
import sys


from pake.transactions import compiler


argv = sys.argv[1:]

if len(argv) > 2 or len(argv) == 0:
    print('usage: python3 metalcompiler.py [--option] source.pake')

if len(argv) == 2: path = argv.pop(1)
else: path = argv.pop(0)

if not os.path.isfile(path):
    print('fatal: "{0}" is not a file'.format(path))
    exit(1)

# make --try the default option
if argv == []: argv = ['--try']

if argv[0] == '--tokenize':
    ifstream = open(path)
    tokens = compiler.tokenizer.decomment(compiler.joiner.join(compiler.tokenizer.tokenize(ifstream.read())))
    ifstream.close()
    print(json.dumps(tokens))
elif argv[0] == '--try':
    ifstream = open(path)
    source = ifstream.read()
    ifstream.close()
    translator = compiler.translator.Translator().take(source).translate()
    print('Declared functions:')
    funcs = translator.getfunctions()
    for f in funcs:
        print(' * {0}'.format(f))
    print()
    calls = translator.getcalls() 
    print('Called functions:')
    for i, c in enumerate(calls):
        print('{0}.\t{1}'.format(i, c['call']))
else:
    print('fatal: unknown switch: {0}'.format(argv[0]))
    exit(2)
