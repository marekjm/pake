#!/usr/bin/env python3

import unittest

from pake.transactions import compiler, runner
from pake import errors as pakeerrors


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


class TranslatorNamespaceSupportTests(unittest.TestCase):
    def testTranslatingEmptyNamespace(self):
        src = 'namespace Foo {}; namespace Bar {}; namespace Baz {};'
        translator = compiler.translator.Translator().take(src).translate()
        for n in ['Foo', 'Bar', 'Baz']:
            self.assertEqual({}, translator[n].functions())
            self.assertEqual({}, translator[n].vars())
            self.assertEqual({}, translator[n].constants())
            self.assertEqual({}, translator[n].classes())
            self.assertEqual({}, translator[n].namespaces())

    def testTranslatingNestedNamespaces(self):
        src = 'namespace Foo { namespace Bar { namespace Baz { namespace Bay {}; }; }; };'
        translator = compiler.translator.Translator().take(src).translate()
        self.assertEqual(list(translator['Foo'].namespaces().keys()), ['Bar'])
        self.assertEqual(list(translator['Foo'].namespaces()['Bar'].namespaces().keys()), ['Baz'])
        self.assertEqual(list(translator['Foo'].namespaces()['Bar'].namespaces()['Baz'].namespaces().keys()), ['Bay'])

    def testUsingDotAsAccessOperator(self):
        src = 'namespace Foo { namespace Bar { namespace Baz { namespace Bay {}; }; }; };'
        translator = compiler.translator.Translator().take(src).translate()
        self.assertEqual(list(translator['Foo.Bar'].namespaces().keys()), ['Baz'])
        self.assertEqual(list(translator['Foo.Bar.Baz'].namespaces().keys()), ['Bay'])
        self.assertEqual(translator['Foo.Bar.Baz.Bay'].namespaces(), {})

    def testAccessingNestedNamespacesFromSource(self):
        src = '''namespace Foo {
            namespace Bar {
                namespace Baz {
                    namespace Bay {};
                };
            };
        };
        Foo.Bar.
        Baz.Bay;'''
        translator = compiler.translator.Translator().take(src).translate()

    def testAccessingNestedNamespacesFromSourceFailsWithTwoDotsInARow(self):
        src = '''namespace Foo {
            namespace Bar {
                namespace Baz {
                    namespace Bay {};
                };
            };
        };
        Foo.Bar.
        .Baz.Bay;'''
        self.assertRaises(compiler.errors.CompilationError, compiler.translator.Translator().take(src).translate)

    def testAccessingNestedNamespacesFromSourceFailsWhenElementDoesNotExist(self):
        src = '''namespace Foo {
            namespace Bar {
                namespace Baz {
                    namespace Bay {};
                };
            };
        };
        Foo.Bar.Baz.Bay.Bax;'''
        self.assertRaises(compiler.errors.UndeclaredReferenceError, compiler.translator.Translator().take(src).translate)

    def testTranslatingFunctionsInNamespaces(self):
        src = 'namespace Foo { function void bar(); };'
        translator = compiler.translator.Translator().take(src).translate()


class TranslatorConstantsTests(unittest.TestCase):
    def testTranslatingDefinitionWithUnspecifiedType(self):
        src = 'const foo = "foo";'
        translator = compiler.translator.Translator().take(src).translate()
        self.assertEqual({'foo': {'type': 'undefined', 'value': '"foo"'}}, translator._ns.constants())
        self.assertEqual({'type': 'undefined', 'value': '"foo"'}, translator['foo'])

    def testTranslatingDefinitionWithDeclaredType(self):
        src = 'const string foo = "foo";'
        translator = compiler.translator.Translator().take(src).translate()
        self.assertEqual({'foo': {'type': 'string', 'value': '"foo"'}}, translator._ns.constants())
        self.assertEqual({'type': 'string', 'value': '"foo"'}, translator['foo'])

    def testTranslatingDefinitionFails(self):
        src0 = 'const = "foo";'
        src1 = 'const string = "foo";'
        src1 = 'const foo;'
        src1 = 'const string foo;'
        for src in [src0, src1]:
            translator = compiler.translator.Translator().take(src)
            self.assertRaises(compiler.errors.CompilationError, translator.translate)


class TranslatorVariablesTests(unittest.TestCase):
    def testTranslatingVariableDeclarationWithUnspecifiedType(self):
        src = 'var foo;'
        translator = compiler.translator.Translator().take(src).translate()
        self.assertEqual({'foo': {'type': 'undefined', 'value': None}}, translator._ns.vars())
        self.assertEqual({'type': 'undefined', 'value': None}, translator['foo'])

    def testTranslatingVariableDeclarationWithSpecifiedType(self):
        src = 'var string foo;'
        translator = compiler.translator.Translator().take(src).translate()
        self.assertEqual({'foo': {'type': 'string', 'value': None}}, translator._ns.vars())
        self.assertEqual({'type': 'string', 'value': None}, translator['foo'])

    def testTranslatingVarDefinitionWithUnspecifiedType(self):
        src = 'var foo = "foo";'
        translator = compiler.translator.Translator().take(src).translate()
        self.assertEqual({'foo': {'type': 'undefined', 'value': '"foo"'}}, translator._ns.vars())
        self.assertEqual({'type': 'undefined', 'value': '"foo"'}, translator['foo'])

    def testTranslatingVarDefinitionWithDeclaredType(self):
        src = 'var string foo = "foo";'
        translator = compiler.translator.Translator().take(src).translate()
        self.assertEqual({'foo': {'type': 'string', 'value': '"foo"'}}, translator._ns.vars())
        self.assertEqual({'type': 'string', 'value': '"foo"'}, translator['foo'])

    def testTranslatingVarDefinitionFailsWhenNoNameIsGiven(self):
        src0 = 'var = "foo";'
        src1 = 'var string = "foo";'
        for src in [src0, src1]:
            translator = compiler.translator.Translator().take(src)
            self.assertRaises(compiler.errors.CompilationError, translator.translate)


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
        src = 'function void set(string key, undefined value="");\nfunction undefined get(string key);'
        desired = {'set': {
                        'name': 'set',
                        'return': 'void',
                        'params': {
                            'key': {'type': 'string', 'default': None},
                            'value': {'type': 'undefined', 'default': '""'},
                        },
                        'param_order': ['key', 'value'],
                        'body': None
                    },
                    'get': {
                         'name': 'get',
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

    def testTranslatingCallToFunctionInsideANamespace(self):
        src = '''namespace Foo {
            function void foo(x);
            function void bar();
        };
        Foo.foo(x="y");
        Foo.bar();
        '''
        translator = compiler.translator.Translator().take(src).translate()
        desired = [{'call': 'Foo.foo', 'params': {'x': '"y"'}},
                   {'call': 'Foo.bar', 'params': {}}
                   ]
        self.assertEqual(desired, translator.getcalls())

    def testTranslatingFunctionCallWhenReferenceIsNotCallable(self):
        src = '''namespace Foo {
            namespace Bar {};
            function void bar();
        };
        Foo.bar();
        Foo.Bar();
        '''
        translator = compiler.translator.Translator().take(src)
        self.assertRaises(compiler.errors.InvalidCallError, translator.translate)

    def testTranslatingFunctionCallFailsWhenRequiredParameterIsNotGiven(self):
        src = 'function void foo(x); foo();'
        translator = compiler.translator.Translator().take(src)
        self.assertRaises(compiler.errors.InvalidCallError, translator.translate)

    def testTranslatingFunctionCallFailsWhenMultipleValuesForAnArgumentAreGiven(self):
        src0 = 'function void foo(x); foo(0, x=0);'
        src1 = 'function void foo(x); foo(x=0, x=0);'
        for src in [src0, src1]:
            translator = compiler.translator.Translator().take(src)
            self.assertRaises(compiler.errors.InvalidCallError, translator.translate)

    def testTranslatingFunctionCallFailsWhenGivenTooManyArguments(self):
        src = 'function void foo(x); foo(0, 1, 2);'
        translator = compiler.translator.Translator().take(src)
        self.assertRaises(compiler.errors.InvalidCallError, translator.translate)

    def testTranslatingFunctionCallFailsWhenUnnamedArgumentAppearsAfterNamedArgument(self):
        src = 'function void foo(x, y); foo(x=0, 1);'
        translator = compiler.translator.Translator().take(src)
        self.assertRaises(compiler.errors.InvalidCallError, translator.translate)


class RunnerTests(unittest.TestCase):
    def testFunctionCalling(self):
        src = 'function void foo(); foo();'
        translator = compiler.translator.Translator().take(src).translate()
        exe = runner.Runner(root='.', requests=translator.getcalls())
        self.assertRaises(pakeerrors.UnknownRequestError, exe.run, fatalwarns=True)

    def testCallingFunctionLocatedInsideANamespace(self):
        src = '''namespace Foo {
            function void foo();
        };
        Foo.foo();
        '''
        translator = compiler.translator.Translator().take(src).translate()
        exe = runner.Runner(root='.', requests=translator.getcalls())
        self.assertRaises(pakeerrors.UnknownRequestError, exe.run, fatalwarns=True)


if __name__ == '__main__':
    unittest.main()
