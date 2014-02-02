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


class JoinerTests(unittest.TestCase):
    def testJoiningInlineCommentTokens(self):
        src = '// comment\n;'
        desired = [(0, '//'), (0, ' '), (0, 'comment'), (0, '\n'), (1, ';')]
        got = compiler.joiner.join(compiler.tokenizer.tokenize(src))
        self.assertEqual(got, desired)

    def testJoiningBlockCommentTokens(self):
        src = '/* comment\n */\n;'
        desired = [(0, '/*'), (0, ' '), (0, 'comment'), (0, '\n'),
                   (1, ' '), (1, '*/'), (1, '\n'),
                   (2, ';')
                   ]
        got = compiler.joiner.join(compiler.tokenizer.tokenize(src))
        self.assertEqual(got, desired)


class TranslatorMatchersTests(unittest.TestCase):
    def testMatchingClosingBrackets(self):
        src = '((({})[(((((<>)))<[()](())>)())])\n)'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize()
        n = transltr._matchbracket(start=0, bracket='(')
        self.assertEqual((1, ')'), transltr._tokens[n])

    def testLogicalEndMatching(self):
        src = 'function void foo() {;;;;}\n;'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize()
        n = transltr._matchlogicalend(start=0)
        self.assertEqual((1, ';'), transltr._tokens[n])


class VariableSupportTests(unittest.TestCase):
    def testSimpleDeclaration(self):
        src = 'var foo;'
        desired = {'value': None, 'type': 'undefined', 'modifiers': []}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['foo'])

    def testTypedDeclaration(self):
        src = 'var bool foo;'
        desired = {'value': None, 'type': 'bool', 'modifiers': []}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['foo'])

    def testRedeclarationChangesType(self):
        src = 'var bool foo; var string foo;'
        desired = {'value': None, 'type': 'string', 'modifiers': []}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['foo'])

    def testRedeclarationDropsValue(self):
        src = 'var bool foo = true; var bool foo;'
        desired = {'value': None, 'type': 'bool', 'modifiers': []}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['foo'])

    def testRedeclarationDropsModifiers(self):
        src = 'var infer bool foo; var string foo;'
        desired = {'value': None, 'type': 'string', 'modifiers': []}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['foo'])

    def testDefinition(self):
        src = 'var bool foo; foo = true;'
        desired = {'value': 'true', 'type': 'bool', 'modifiers': []}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['foo'])

    def testDefinitionFailsBecauseOfMismatchedTypes(self):
        src = 'var bool foo; foo = "true";'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize()
        self.assertRaises(compiler.errors.CompilationError, transltr.translate)

    def testInstantDefinition(self):
        src = 'var bool foo = true;'
        desired = {'value': 'true', 'type': 'bool', 'modifiers': []}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['foo'])

    def testInstantDefinitionSupplyingValueViaReference(self):
        src = 'var bool foo = true; var bool bar = foo;'
        desired = {'value': 'true', 'type': 'bool', 'modifiers': []}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['bar'])

    def testInstantDefinitionSupplyingValueViaReferenceFailsWhenReferenceHasNoDefinedValue(self):
        src = 'var bool foo; var bool bar = foo;'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize()
        self.assertRaises(compiler.errors.CompilationError, transltr.translate)

    def testInstantDefinitionFailsBecauseOfMismatchedTypes(self):
        src = 'var string foo = true;'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize()
        self.assertRaises(compiler.errors.CompilationError, transltr.translate)

    def testVariableWithUndefinedTypeAccetpsValueOfAnyType(self):
        src = '''var foo = true;
        var bar = "true";
        '''
        desired = {'foo': {'value': 'true', 'type': 'undefined', 'modifiers': []},
                   'bar': {'value': '"true"', 'type': 'undefined', 'modifiers': []},
                   }
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr._var)

    def testVariableWithUndefinedTypeAccetpsValueOfAnyTypeEvenAfterDeclaration(self):
        src = '''var foo = true;
        var bar = "true";

        foo = "true";
        bar = true;
        '''
        desired = {'foo': {'value': '"true"', 'type': 'undefined', 'modifiers': []},
                   'bar': {'value': 'true', 'type': 'undefined', 'modifiers': []},
                   }
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr._var)

    def testModifierHardPreventsRedeclaration(self):
        src = 'var hard bool foo; var bool foo;'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize()
        self.assertRaises(compiler.errors.CompilationError, transltr.translate)

    def testModifierInferWorksWithInstantDefinitions(self):
        src = 'var infer undefined foo = "spam";'
        desired = {'value': '"spam"', 'type': 'string', 'modifiers': ['infer']}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['foo'])

    def testModifierInferAdjustsTypeOfTheVariableToTypeOfAssignedValue(self):
        src = '''var infer undefined foo;
        foo = true;
        foo = "true";
        '''
        desired = {'value': '"true"', 'type': 'string', 'modifiers': ['infer']}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['foo'])

    def testGettingWhatIs(self):
        src = 'var foo;'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual('var', transltr._whatis('foo'))

    def testTypeofOfVariableWithUndefinedTypeAlwaysReturnsUndefined(self):
        src = 'var undefined foo = true;'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual('undefined', transltr._typeof('foo'))


class ConstantsSupportTests(unittest.TestCase):
    def testConstantDeclaration(self):
        src = 'const bool foo = true;'
        desired = {'value': 'true', 'type': 'bool', 'modifiers': []}
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()
        self.assertEqual(desired, transltr['foo'])

    def testConstantDeclarationFailsWhenNoValueGiven(self):
        src = 'const bool foo;'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize()
        self.assertRaises(compiler.errors.CompilationError, transltr.translate)

    def testConstantRedefinitionFails(self):
        src = 'const bool foo = true; foo = true;'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize()
        self.assertRaises(compiler.errors.CompilationError, transltr.translate)

    def testConstantRedeclarationFails(self):
        src = 'const bool foo = true; const string foo = "true";'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize()
        self.assertRaises(compiler.errors.CompilationError, transltr.translate)

    def testConstantDeclarationFailsBecauseOfMismatchedTypes(self):
        src = 'const bool foo = "true";'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize()
        self.assertRaises(compiler.errors.CompilationError, transltr.translate)


class FunctionSupportTest(unittest.TestCase):
    @unittest.skip('')
    def testSimpleDeclaration(self):
        src = 'function void;'
        transltr = compiler.translator.NamespaceTranslator(*compiler.translator.sourced(source=src, read=False)).finalize().translate()


if __name__ == '__main__':
    unittest.main()
