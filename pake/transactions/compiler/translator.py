#!/usr/bin/env python3

"""Part of Akemetal responsible for translating tokens into
executable form.
"""


# Flags
DEBUG = False


from . import tokenizer, joiner, shared, errors


types = ['int', 'float', 'string', 'bool', 'undefined', 'void']


def _functiondeclarationparams(tokens, src):
    """Compile function declaration parameter list -> (...).
    """
    params, param_order = [], []
    param = {'name': None,
             'type': 'undefined',
             'default': None,
             }
    step = 0
    i = 0
    while i < len(tokens):
        l, tok = tokens[i]
        if tok in types and step == 0:
            param['type'] = tok
            step = 1
        elif shared.isvalidname(tok) and (step == 0 or step == 1):
            param['name'] = tok
            step = 2
        elif tok == ',' and (step == 2 or step == 3):
            step = 0
            params.append(param)
            param_order.append(param['name'])
            param = {'name': None, 'type': 'undefined', 'default': None}
        elif tok == '=' and step == 2:
            step = 3
        elif step == 3:
            param['default'] = tok
        elif tok == ')' and (step == 2 or step == 3):
            i += 1
            break
        else:
            raise errors.CompilationError('line {0}: "{1}": in function declaration: {2}'.format(l+1, tokenizer.rebuild(l, src), tok))
        i += 1
    if param != {'name': None, 'type': 'undefined', 'default': None}:
        params.append(param)
        param_order.append(param['name'])
    return (params, param_order)


class NamespaceTranslator2():
    def __init__(self, tokens, source, name='', parenttypes=[], parentnames=[]):
        self._tokens = tokens
        self._source = source
        self._name = name
        self._parenttypes = parenttypes
        self._parentnames = parentnames
        self._function = {}
        self._var = {}
        self._const = {}
        self._class = {}
        self._namespace = {}
        self._calls = []
        self._imported = {}

    def __getitem__(self, access):
        item = None
        parts = access.split('.')
        if len(parts) == 1:
            if access in self._function: item = self._function[access]
            elif access in self._var: item = self._var[access]
            elif access in self._const: item = self._const[access]
            elif access in self._class: item = self._class[access]
            elif access in self._namespace: item = self._namespace[access]
        else:
            ns = parts[0]
            if ns in self._namespace: item = self._namespace[ns]['.'.join(parts[1:])]
        return item

    def __contains__(self, item):
        return (self.__getitem__(item) is not None)

    def _throw(self, err, line, message=''):
        report = 'line {0}: {1}'.format(line+1, tokenizer.rebuild(line, self._source))
        if message: report = '{0}: {1}'.format(message, report)
        raise err(report)

    def _warn(self, line, message=''):
        report = 'line {0}: {1}'.format(line+1, tokenizer.rebuild(line, self._source))
        if message: report = '{0}: {1}'.format(message, report)
        print('warning: {0}'.format(report))

    def _matchbracket(self, start, bracket):
        match = {'{': '}',
                 '(': ')',
                 '[': ']',
                 '<': '>',
                 }
        left = 1
        n = (start + 1)
        while n < len(self._tokens):
            if left == 0: break
            if self._tokens[n][1] == match[bracket]: left -= 1
            if self._tokens[n][1] == bracket: left += 1
            n += 1
        if not (left == 0):
            line = self._tokens[start][0]
            msg = 'did not found matching pair for opening bracket: {0}'.format(bracket)
            self._throw(errors.CompilationError, line, msg)
        return (n-start)

    def _matchlogicalend(self, start):
        n = (start+1)
        while n < len(self._tokens):
            if self._tokens[n][1] == ';': break
            n += 1
        return (n-start)

    def _getreferencetokens(self, start, use=[]):
        n, tokens = (0, [])
        if not use: use = self._tokens
        l, tok = use[start]
        while shared.isvalidname(tok) or tok == '.':
            if (n % 2 == 1) and tok != '.':
                break
            if (n % 2 == 0) and tok == '.':
                self._throw(errors.CompilationError, use[start][0], 'invalid reference')
            tokens.append((l, tok))
            n += 1
            if (start+n) >= len(use): break
            l, tok = use[start+n]
        return (n, tokens)

    def _extractfunction(self, index):
        n = index+1
        extracted = {'type': None,
                     'name': None,
                     'params': None,
                     'body': None,
                     }
        extracted['type'] = self._tokens[n][1]
        if DEBUG: print(n, self._tokens[n], extracted['type'])
        n += 1
        extracted['name'] = self._tokens[n][1]
        if DEBUG: print(n, self._tokens[n], extracted['name'])
        n += 1
        if self._tokens[n][1] == '(':
            forward = self._matchbracket(start=n, bracket='(')
            if DEBUG: print(forward)
            extracted['params'] = self._tokens[n:n+forward]
            n += forward
        else:
            self._throw(errors.CompilationError, self._tokens[n][0])
        if self._tokens[n][1] == '{':
            forward = self._matchbracket(start=n, bracket='{')
            if DEBUG: print(forward)
            extracted['body'] = self._tokens[n:n+forward]
            n += forward
        if self._tokens[n][1] != ';':
            msg = 'missing semicolon after function '
            if extracted['body'] is None: msg += 'declaration'
            else: msg += 'definition'
            msg += ' starting on line {0}'.format(self._tokens[index+1][0]+1)
            self._throw(errors.CompilationError, self._tokens[n-1][0], msg)
        n += 1
        leap = (n-index)
        return (leap, extracted)

    def _extractimport(self, index):
        n = index+1
        forward = self._matchlogicalend(start=n)
        extracted = self._tokens[n:n+forward]
        n += forward
        n += 1
        leap = (n-index)
        return (leap, extracted)

    def _extractnamespace(self, index):
        n = index+1
        extracted = {'name': None,
                     'body': None,
                     }
        extracted['name'] = self._tokens[n][1]
        if DEBUG: print(n, self._tokens[n], extracted['name'])
        n += 1
        if self._tokens[n][1] == '{':
            forward = self._matchbracket(start=n, bracket='{')
            if DEBUG: print(forward)
            extracted['body'] = self._tokens[n:n+forward]
            n += forward
        if self._tokens[n][1] != ';': self._throw(errors.CompilationError, self._tokens[n][0])
        n += 1
        leap = (n-index)
        return (leap, extracted)

    def _typeof(self, what, reference=True):
        if reference: what = self[what]
        type = 'undefined'
        if tokenizer.candequote(what): type = 'string'
        return type

    def _compilekw_const(self, index):
        leap, piece = self._compiledatapiece(index, allow_declarations=False)
        name = piece['name']
        del piece['name']
        self._const[name] = piece
        return leap

    def _compiledatapiece(self, index, allow_declarations=True):
        leap = self._matchlogicalend(start=index)
        tokens = self._tokens[index+1:index+leap]
        words = [tok for l, tok in tokens]
        piece = {'type': 'undefined',
                 'value': None,
                 'name': None
                 }
        is_declaration = not ('=' in words)
        if is_declaration and not allow_declarations: self._throw(errors.CompilationError, tokens[0][0], 'declarations are not allowed')
        if is_declaration:
            declaration = words
            definition = []
        else:
            eq = words.index('=')
            declaration = words[:eq]
            definition = words[eq+1:]
        if len(declaration) == 1 and shared.isvalidname(declaration[0]) and declaration[0] not in self.hastypes():
            piece['name'] = declaration[0]
        elif len(declaration) > 1:
            n, piecetypetokens = self._getreferencetokens(index+1)
            if n == len(declaration)-1:
                piecetype = '.'.join(declaration[:-1])
                piecename = declaration[-1]
            if piecetype in self.hastypes() and shared.isvalidname(piecename):
                piece['type'] = piecetype
                piece['name'] = piecename
        if piece['name'] is None: self._throw(errors.CompilationError, tokens[0][0], 'invalid declaration/definition')
        piecevalue = '.'.join(definition)
        if piecevalue: piece['value'] = piecevalue
        if not is_declaration and piece['value'] is None: self._throw(errors.CompilationError, tokens[0][0], 'invalid declaration/definition')
        return (leap, piece)

    def _compilekw_var(self, index):
        leap, piece = self._compiledatapiece(index)
        name = piece['name']
        del piece['name']
        self._var[name] = piece
        return leap

    def _compilekwFunction(self, code):
        function = {'name': None,
                    'type': 'undefined',
                    'params': {},
                    'param_order': [],
                    'body': None,
                    }
        for key in ['name', 'type']: function[key] = code[key]
        function['params'], function['param_order'] = _functiondeclarationparams(code['params'][1:-1], self._source)
        function['body'] = code['body']
        if function['body'] is not None: function['body'] = function['body'][1:-1]
        return function

    def _compilekwImport(self, code):
        srcpath = tokenizer.dequote(code[0][1])
        if srcpath in self._imported:
            if DEBUG: print('reusing previously compiled import file: {0}'.format(srcpath))
            imported = self._imported[srcpath]
        else:
            if DEBUG: print('importing file: {0}'.format(srcpath))
            ifstream = open(srcpath)
            source = ifstream.read()
            ifstream.close()
            source = tokenizer.tokenize(source)
            tokens = tokenizer.strip(tokenizer.decomment(joiner.join(source)))
            if DEBUG: print('  * compiling...')
            imported = NamespaceTranslator2(tokens=tokens, source=source).translate()
            if DEBUG: print('  * saving for later reuse...')
            self._imported[srcpath] = imported
        if len(code) == 1:
            for ns in imported.getnamspaces():
                self._namespace[ns] = imported[ns]
            for f in imported.getfunctions():
                self._function[f] = imported[f]
        else:
            where = code[1][1]
            path = code[2][1]
            what = imported[path]
            path = path.split('.')[-1]
            if where == 'namespace':
                self._namespace[path] = what
            elif where == 'function':
                self._function[path] = what
            else:
                self._throw(errors.CompilationError, code[0][0], 'bad import')

    def _functioncallparams(self, tokens):
        params = []
        if tokens and tokens[-1][1] != ',':
            # this if block can be removed after var/const reference resolving is implemented
            # for now it's here to make translator think that everything that looks like valid name
            # is a parameter name
            l = tokens[-1][0]
            tokens.append((l, ','))
        step = 0
        i = 0
        name, value = '', None
        while i < len(tokens):
            l, tok = tokens[i]
            if shared.isvalidname(tok) and step == 0:
                name = tok
                step = 1
            elif tok == '=' and step == 0:
                self._throw(errors.CompilationError, l, 'expected parameter name before = operator')
            elif tok == '=' and step == 1:
                step = 2
            elif tok == ',' and (step == 0 or step == 3):
                step = 0
                params.append((name, value))
                name, value = '', None
            elif tok == ',' and step == 2:
                self._throw(errors.CompilationError, l, 'expected value after = operator')
            elif step == 0 or step == 2:
                value = tok
                step = 3
            else:
                msg = 'error during step {0} of function call parameters compilation: ({1}, `{2}`)'.format(step, name, value)
                if step == 1: msg = 'expected = operator after parameter name'
                self._throw(errors.CompilationError, l, msg)
            i += 1
        if name and value is None and step != 2:
            value = name
            name = ''
        if name and value is None and step == 2:
            self._throw(errors.CompilationError, l, 'expected value after = operator')
        if value is not None: params.append((name, value))
        return params

    def _verifycall(self, index, reference, rawparams):
        function = self[reference]
        required = [k['name'] for k in function['params'] if (k['default'] is None)]
        params = {}
        wasnamed = False
        for name, v in rawparams:
            if name != '': wasnamed = True
            if name == '' and wasnamed:
                line = self._tokens[index][0]
                raise self._throw(errors.InvalidCallError, line, 'unnamed argument appeared after named argument'.format(name))
        for i, param in enumerate(rawparams):
            name, value = param
            if name == '':
                maximum = len(function['param_order'])
                if i >= maximum:
                    line = self._tokens[index][0]
                    raise self._throw(errors.InvalidCallError, line, 'got too many arguments, expected at most {0} but got {1}'.format(maximum, len(rawparams)))
                name = function['param_order'][i]
            if name in params:
                line = self._tokens[index][0]
                raise self._throw(errors.InvalidCallError, line, 'got multiple values for argument `{0}`'.format(name))
            params[name] = value
        for param in required:
            if param not in params:
                line = self._tokens[index][0]
                msg = 'missing required parameter "{1}" for function "{0}"'.format(reference, param)
                raise self._throw(errors.InvalidCallError, line, msg)
        for key in params:
            value = params[key]
            typeof = self._typeof(value, reference=False)
            expected = [k for k in function['params'] if (k['name'] == key)][0]['type']
            if typeof != expected and expected != 'undefined':
                self._throw(errors.InvalidCallError, self._tokens[index][0], 'invalid type of argument given to parameter "{0}", expected "{1}" but got "{2}"'.format(key, expected, typeof))
        return params

    def _translate(self, index):
        line, token = self._tokens[index]
        if token == 'namespace':
            leap, code = self._extractnamespace(index)
            ns = NamespaceTranslator2(tokens=code['body'][1:-1],
                                      source=self._source,
                                      name=code['name'],
                                      )
            self._namespace[code['name']] = ns.translate()
        elif token == 'function':
            leap, code = self._extractfunction(index)
            self._function[code['name']] = self._compilekwFunction(code)
        elif token == 'import':
            leap, code = self._extractimport(index)
            self._compilekwImport(code)
        elif token == ';':
            leap = 1
        elif shared.isvalidreference(token) and ((token in self) or (token in self._parentnames)):
            leap = 1
            if self._tokens[index+leap][1] == '(':
                forward = self._matchbracket(start=(index+leap), bracket='(')
                look = (index+leap+forward)
                if self._tokens[look][1] != ';': self._warn(self._tokens[look-1][0], 'missing semicolon after function call')
                params = self._tokens[index+leap:index+leap+forward]
                params = self._functioncallparams(params[1:-1])
                params = self._verifycall(index=index, reference=token, rawparams=params)
                self._calls.append({'call': token, 'params': params})
                leap += forward
        elif token in shared.getkeywords():
            self._throw(errors.CompilationError, line, 'keyword not implemented: {0}'.format(token))
        elif shared.isvalidreference(token):
            self._throw(errors.CompilationError, line, 'undeclared reference: {0}'.format(token))
        else:
            self._throw(errors.CompilationError, line, 'unexpected token found: {0}'.format(token))
        return leap

    def _joinreferencetokens(self):
        joined = []
        i = 0
        while i < len(self._tokens):
            line, token = self._tokens[i]
            if shared.isvalidname(token):
                forward, refs = self._getreferencetokens(start=i)
                token = ''.join([tok for l, tok in refs])
                i += forward
            else:
                i += 1
            joined.append((line, token))
        self._tokens = joined

    def finalize(self):
        self._joinreferencetokens()
        return self

    def translate(self):
        i = 0
        while i < len(self._tokens): i += self._translate(i)
        return self

    def getnamspaces(self):
        return self._namespace

    def getfunctions(self):
        return self._function

    def getcalls(self):
        return self._calls
