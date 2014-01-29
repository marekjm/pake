#!/usr/bin/env python3

"""Simple test-compiler for Grass (PAKE metalanguage) used for debugging and development purposes.
It does not generate compiled files of any kind - its only purpose is to check whether
the Grass translator is able to correctly process given source code.

Usage: {0}

SWITCHES:
    --tokenize          - only tokenize the source (this also involves joining but not decommenting or stripping)
    --try               - try compiling the source (check for validity)
    --verbose           - display what tokenized/compiled code contains; allows for some debugging insights


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

usage = 'usage: python3 metalcompiler.py [--option ...] source.grass'

if len(argv) > 3 or len(argv) == 0: print(usage)

if '--verbose' in argv:
    VERBOSE = True
    argv.remove('--verbose')
else:
    VERBOSE = False


if argv[0] in ['-h', '--help']:
    print(__doc__.format(usage))
    exit(0)


if len(argv) == 2: path = argv.pop(1)
else: path = argv.pop(0)

if not os.path.isfile(path):
    print('fatal: "{0}" is not a file'.format(path))
    exit(1)

# make --try the default option
if argv == []: argv = ['--try']

if argv[0] == '--tokenize':
    ifstream = open(path)
    tokens = compiler.joiner.join(compiler.tokenizer.tokenize(ifstream.read()))
    ifstream.close()
    if VERBOSE: print(tokens)
elif argv[0] == '--try':
    ifstream = open(path)
    source = ifstream.read()
    ifstream.close()
    raw = compiler.tokenizer.tokenize(source)
    tokens = compiler.joiner.join(raw)
    tokens = compiler.tokenizer.decomment(tokens)
    tokens = compiler.tokenizer.strip(tokens)
    translator = compiler.translator.NamespaceTranslator2(tokens=tokens, source=raw).finalize()
    translator.translate()
    namespaces = translator.getnamspaces()
    funcs = translator.getfunctions()
    calls = translator.getcalls() 
    if VERBOSE:
        print('Declared:')
        print('variables: ({0})'.format(len(translator._var.keys())))
        print(translator._var)
        print('namespaces: ({0})'.format(len(namespaces.keys())))
        for n in namespaces:
            print(' * {0}'.format(n))
        print()
        print('functions: ({0})'.format(len(funcs.keys())))
        for f in funcs:
            print(' * {0}: {1}'.format(f, funcs[f]))
        print()
        print('Calls: ({0})'.format(len(calls)))
        for i, c in enumerate(calls):
            print('{0}.\t{1}: {2}'.format(i, c['call'], c['params']))
else:
    print('fatal: unknown switch: {0}'.format(argv[0]))
    exit(2)
