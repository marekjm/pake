#!/usr/bin/env python3

import unittest

from pake.transactions import compiler


class TokenizerTests(unittest.TestCase):
    def testTokenization(self):
        src = "('foo', bar=\"baz\");\n(foo='foo', bar='bar', baz=\"baz\",)"
        desired = [(0, '('), (0, "'foo'"), (0, ','), (0, ' '), (0, 'bar'), (0, '='), (0, '"baz"'), (0, ')'), (0, ';'), (0, '\n'),
                   (1, '('), (1, 'foo'), (1, '='), (1, "'foo'"), (1, ','), (1, ' '),
                             (1, 'bar'), (1, '='), (1, "'bar'"), (1, ','), (1, ' '),
                             (1, 'baz'), (1, '='), (1, '"baz"'), (1, ','),
                   (1, ')'),
                   ]
        got = compiler.tokenizer.tokenize(src)
        self.assertEqual(got, desired)

    def testGettingLine(self):
        src = "('foo', bar=\"baz\");\n(foo='foo', bar='bar', baz=\"baz\",)"
        desired = [(0, '('), (0, "'foo'"), (0, ','), (0, ' '), (0, 'bar'), (0, '='), (0, '"baz"'), (0, ')'), (0, ';'), (0, '\n'),
                   ]
        got = compiler.tokenizer.getline(0, compiler.tokenizer.tokenize(src))
        self.assertEqual(got, desired)

    def testRebuildingLine(self):
        src = "('foo', bar=\"baz\");\n(foo='foo', bar='bar', baz=\"baz\",)"
        tokens = compiler.tokenizer.tokenize(src)
        desired = "('foo', bar=\"baz\");"
        got = ''.join(compiler.tokenizer.getline(0, tokens, lined=False))
        self.assertEqual(got, desired)
        self.assertEqual(compiler.tokenizer.rebuild(0, tokens), desired)

    def testStripping(self):
        src = "('foo', bar=\"baz\");\n(foo='foo', bar='bar', baz=\"baz\",)"
        desired = [(0, '('), (0, "'foo'"), (0, ','), (0, 'bar'), (0, '='), (0, '"baz"'), (0, ')'), (0, ';'),
                   ]
        got = compiler.tokenizer.strip(compiler.tokenizer.getline(0, compiler.tokenizer.tokenize(src)))
        self.assertEqual(got, desired)

    def testTokenizationOfFunctionHead(self):
        src = 'foo(x="");'
        desired = [(0, 'foo'), (0, '('), (0, 'x'), (0, '='), (0, '""'), (0, ')'), (0, ';'),
                ]
        got = compiler.tokenizer.tokenize(src)
        self.assertEqual(got, desired)


class TranslatorFunctionSupportTests(unittest.TestCase):
    def testTranslatingFunctionDeclaration(self):
        src = 'function void foo(x, y="", z=0);'
        desired = {'name': 'foo',
                   'return': 'void',
                   'params': {'x': {'type': 'undefined', 'default': None},
                              'y': {'type': 'undefined', 'default': '""'},
                              'z': {'type': 'undefined', 'default': '0'},
                              },
                   'param_order': ['x', 'y', 'z'],
                   'body': None}
        translator = compiler.translator.Translator().take(src).translate()
        got = translator.getfunctions()['foo']
        self.assertEqual(desired, got)

    def testTranslatingMultipleFunctionDeclarations(self):
        src = 'function void _set(string key, undefined value="");\nfunction undefined _get(string key);'
        desired = {'_set': {
                        'name': '_set',
                        'return': 'void',
                        'params': {
                            'key': {'type': 'string', 'default': None},
                            'value': {'type': 'undefined', 'default': '""'},
                        },
                        'param_order': ['key', 'value'],
                        'body': None
                    },
                    '_get': {
                         'name': '_get',
                         'return': 'undefined',
                         'params': {'key': {'type': 'string', 'default': None}},
                         'param_order': ['key'],
                         'body': None
                    },
                   }
        translator = compiler.translator.Translator().take(src).translate()
        got = translator.getfunctions()  #['set']
        self.assertEqual(desired, got)

    def testTranslatingFunctionCall(self):
        src1 = 'function void foo(x, answer);\nfoo(x="stuff", answer=42);'
        # src2 with comma at the end of parameters list
        src2 = 'function void foo(x, answer);\nfoo(x="stuff", answer=42,);'
        for src in [src2, src2]:
            translator = compiler.translator.Translator().take(src).translate()
            desired = {'call': 'foo', 'params': {'x': '"stuff"', 'answer': '42'}}
            self.assertEqual(desired, translator.getcalls()[0])

    def testTranslatingFunctionCallFailsBecauseNoDeclarationFound(self):
        src = 'foo(x="stuff", answer=42);'
        translator = compiler.translator.Translator().take(src)
        self.assertRaises(compiler.errors.UndeclaredReferenceError, translator.translate)


class TranslatorNamespaceSupportTests(unittest.TestCase):
    def testTranslatingEmptyNamespace(self):
        src = 'namespace Foo {}; namespace Bar {}; namespace Baz {};'
        translator = compiler.translator.Translator().take(src).translate()
        for n in ['Foo', 'Bar', 'Baz']:
            self.assertEqual({}, translator._namespaces[n].functions())
            self.assertEqual({}, translator._namespaces[n].vars())
            self.assertEqual({}, translator._namespaces[n].constants())
            self.assertEqual({}, translator._namespaces[n].classes())
            self.assertEqual({}, translator._namespaces[n].namespaces())

    def testTranslatingNestedNamespaces(self):
        src = 'namespace Foo { namespace Bar { namespace Baz { namespace Bay {}; }; }; };'
        translator = compiler.translator.Translator().take(src).translate()
        self.assertEqual(list(translator._namespaces['Foo'].namespaces().keys()), ['Bar'])
        self.assertEqual(list(translator._namespaces['Foo'].namespaces()['Bar'].namespaces().keys()), ['Baz'])
        self.assertEqual(list(translator._namespaces['Foo'].namespaces()['Bar'].namespaces()['Baz'].namespaces().keys()), ['Bay'])


if __name__ == '__main__':
    unittest.main()
