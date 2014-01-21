#!/usr/bin/env python3

"""Part of Akemetal responsible for translating tokens into
executable form.
"""


# Flags
DEBUG = False


from . import tokenizer, joiner, shared, errors


types = ['int', 'float', 'string', 'undefined', 'void']


def _functioncallparams(tokens, src):
    """Compile function call parameter list -> (...).
    """
    params = {}
    param = {'name': None,
             'value': None,
             }
    step = 0
    i = 0
    while i < len(tokens):
        l, tok = tokens[i]
        if shared.isvalidname(tok) and step == 0:
            param['name'] = tok
            step = 1
        elif tok == '=' and step == 1:
            step = 2
        elif (tok == ',' or tok == ')') and (step == 0 or step == 3):
            if tok == ')':
                i += 1
                break
            step = 0
            params[param['name']] = param['value']
            param = {'name': None, 'value': None}
        elif step == 2:
            param['value'] = tok
            step = 3
        else:
            raise errors.CompilationError('line {0}: "{1}": neighbouring tokens: {2}'.format(l+1, tokenizer.rebuild(l, src),
                                                                                             ' '.join([tokens[i-1][1], tok, tokens[i+1][1]])))
        i += 1
    if param != {'name': None, 'value': None}:
        params[param['name']] = param['value']
    return params


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
            raise errors.CompilationError('line {0}: "{1}": token: {2}'.format(l+1, tokenizer.rebuild(l, src), tok))
        i += 1
    if param != {'name': None, 'type': 'undefined', 'default': None}:
        params.append(param)
        param_order.append(param['name'])
    return (params, param_order)


def functiondeclaration(tokens, n, src):
    ex = {'name': None,
          'params': {},
          'param_order': [],
          'body': None,
          'return': None
          }
    ex['return'] = tokens[n][1]
    ex['name'] = tokens[n+1][1]
    param_list_start, param_list_end = 0, 0
    i = 2
    for l, tok in tokens[n+2:]:
        if tok == '(':
            param_list_start = i+1
        if tok == ')':
            param_list_end = i+1
            break
        i += 1
    leap = i
    leap += 1
    if param_list_start != 3 or tokens[n+leap][1] != ';':
        l = tokens[n+leap][0]
        if not src: src = tokens
        raise errors.CompilationError('line {0}: "{1}"'.format(l+1, tokenizer.rebuild(l, src)))
    param_tokens = tokens[param_list_start:param_list_end+1]
    params, ex['param_order'] = _functiondeclarationparams(param_tokens[1:-1], src)
    for p in params:
        ex['params'][p['name']] = {}
        for k in ['default', 'type']:
            ex['params'][p['name']][k] = p[k]
    leap += 1
    return (ex, leap)


class Translator():
    """Translator for Metal.

    NOTICE: Currently there is no way to store the executable form.
            The language is not designed to be a full-feature creation.
    """
    def __init__(self):
        self._src = []
        self._tokens = []
        self._ns = None

    def __getitem__(self, access):
        return self._ns[access]

    def take(self, source):
        """Takes :source as string.
        """
        tokens = tokenizer.tokenize(source)
        self._src = tokens
        self._tokens = tokenizer.strip(tokenizer.decomment(joiner.join(tokens)))
        return self

    def translate(self):
        self._ns = NamespaceTranslator(self._tokens, self._src).translate()
        return self

    def constants(self):
        return self._ns.constants()

    def getfunctions(self):
        return self._ns._function
    
    def getcalls(self):
        return self._ns._calls


class NamespaceTranslator():
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

    def _throw(self, err, line, message):
        raise err('line {0}: {1}: {2}'.format(line+1, tokenizer.rebuild(line, self._source), message))

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
            msg = 'line {0}: "{1}": did not found matching pair for opening bracket: {2}'.format(line, tokenizer.rebuild(line, self._source), bracket)
            raise errors.CompilationError(msg)
        return (n-start)

    def _matchlogicalend(self, start):
        n = (start+1)
        while n < len(self._tokens):
            if self._tokens[n][1] == ';': break
            n += 1
        return (n-start)

    def _getreferencetokens(self, start):
        n, tokens = (0, [])
        l, tok = self._tokens[start]
        while shared.isvalidname(tok) or tok == '.':
            if (n % 2 == 1) and tok != '.':
                break
            if (n % 2 == 0) and tok == '.':
                raise errors.CompilationError('line {0}: "{1}": invalid reference starting on line {2}: "{3}"'
                                              .format(l+1, tokenizer.rebuild(l, self._source),
                                                      (self._tokens[start][0]+1), tokenizer.rebuild(self._tokens[start][0], self._source)))
            tokens.append((l, tok))
            n += 1
            l, tok = self._tokens[start+n]
        return (n, tokens)

    def _functioncallparams(self, tokens):
        params = []
        step = 0
        i = 0
        name, value = '', None
        while i < len(tokens):
            l, tok = tokens[i]
            if shared.isvalidname(tok) and step == 0:
                name = tok
                step = 1
            elif tok == '=' and step == 1:
                step = 2
            elif tok == ',' and (step == 0 or step == 3):
                step = 0
                params.append((name, value))
                name, value = '', None
            elif step == 0:
                value = tok
            elif step == 2:
                value = tok
                step = 3
            else:
                raise errors.CompilationError('line {0}: "{1}"'.format(l+1, tokenizer.rebuild(l, self._source)))
            i += 1
        if value is not None: params.append((name, value))
        return params

    def _verifycall(self, index, tokens, reference):
        function = self[reference]
        required = [k for k in function['params'] if (function['params'][k] is not None)]
        rawparams = self._functioncallparams(tokens)
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
                    raise self._throw(errors.InvalidCallError, line, 'got too many arguments, expected at most {0}: {1}'.format(maximum, len(rawparams)))
                name = function['param_order'][i]
            if name in params:
                line = self._tokens[index][0]
                raise self._throw(errors.InvalidCallError, line, 'got multiple values for argument: {0}'.format(name))
            params[name] = value
        for param in required:
            if param not in params:
                line = self._tokens[index][0]
                msg = 'missing required parameter for function "{0}": {1}'.format(reference, param)
                raise self._throw(errors.InvalidCallError, line, msg)

    def _compilekw_import(self, index):
        try:
            path = tokenizer.dequote(self._tokens[index+1][1])
            ifstream = open(path)
            source = ifstream.read()
            ifstream.close()
            trans = Translator().take(source).translate()
            funcs = trans.getfunctions()
            for f in funcs:
                if f not in self._functions:
                    self._functions[f] = funcs[f]
            error = None
        except (Exception) as e:
            error = e
        finally:
            pass
        if error is not None:
            line = self._tokens[index][0]
            msg = 'caused by error in imported file "{0}":\n{1}: {2}'.format(path, type(error), error)
            raise self._throw(errors.CompilationError, line, msg)
        else:
            leap = 2
        return leap

    def _compilekw_namespace(self, index):
        name = self._tokens[index+1][1]
        nstokens = []
        nstokens.append(self._tokens[index])
        nstokens.append(self._tokens[index+1])
        leap = 2
        if self._tokens[index+leap][1] == ';':
            nstokens.append(self._tokens[index+leap])
        elif self._tokens[index+leap][1] == '{':
            jump = self._matchbracket(bracket='{', start=index+leap)
            nstokens.extend(self._tokens[index+leap:index+leap+jump])
            leap += jump
        else:
            line = self._tokens[index][0]
            tok = self._tokens[index][1]
            raise errors.CompilationError('line {0}: "{1}": token: {2}'.format(line, tokenizer.rebuild(line, self._source), tok))
        ns = NamespaceTranslator(tokens=nstokens[3:-1], source=self._source, name=name,
                                 parenttypes=self.hastypes(), parentnames=self.names())
        self._namespace[name] = ns.translate()
        return leap

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

    def _compilekeyword(self, index):
        line, tok = self._tokens[index]
        if tok == 'import':
            leap = self._compilekw_import(index)
        elif tok == 'namespace':
            leap = self._compilekw_namespace(index)
        elif tok == 'function':
            func, leap = functiondeclaration(self._tokens, (index+1), self._source)
            self._function[func['name']] = func
        elif tok == 'const':
            leap = self._compilekw_const(index)
        elif tok == 'var':
            leap = self._compilekw_var(index)
        else:
            msg = 'line {0}: "{1}": keyword not yet implemented: {2}'.format(line+1, tokenizer.rebuild(line, self._source), tok)
            raise errors.CompilationError(msg)
        return leap

    def _compilefunctioncall(self, index, reference):
        call = {'call': reference, 'params': {}}
        leap = self._matchbracket(start=index, bracket='(')
        param_tokens = self._tokens[index:index+leap][1:-1]
        params = dict(self._functioncallparams(param_tokens))
        call['params'] = params
        function = self[reference]
        function = ('return' in function and 'body' in function and 'params' in function and 'param_order' in function)
        if not function:
            line = self._tokens[index][0]
            raise errors.InvalidCallError('line {0}: "{1}": {2} is not callable'.format(line, tokenizer.rebuild(line, self._source), reference))
        self._verifycall(index=index, tokens=param_tokens, reference=reference)
        return (call, leap)

    def _compile(self, index):
        l, tok = self._tokens[index]
        if tok == ';':
            leap = 1
        elif tok in shared.getkeywords():
            leap = self._compilekeyword(index)
        elif shared.isvalidname(tok) and ((tok in self) or (tok in self._parentnames)):
            leap, access = self._getreferencetokens(index)
            reference = ''.join([tok for l, tok in access])
            if reference not in self and reference not in self._parentnames:
                raise errors.UndeclaredReferenceError('line {0}: "{1}": undeclared reference: "{2}"'.format(l+1, tokenizer.rebuild(l, self._source), reference))
            if self._tokens[index+leap][1] == '(':
                call, call_leap = self._compilefunctioncall(index+leap, reference)
                self._calls.append(call)
                leap += call_leap
        elif shared.isvalidname(tok):
            raise errors.UndeclaredReferenceError('line {0}: "{1}": undeclared reference: "{2}"'.format(l+1, tokenizer.rebuild(l, self._source), tok))
        else:
            raise errors.CompilationError('line {0}: "{1}": token: {2}'.format(l+1, tokenizer.rebuild(l, self._source), tok))
        return leap

    def translate(self):
        if DEBUG: print('parent names:', self._parentnames)
        if DEBUG: print('local names:', self.names())
        i = 0
        while i < len(self._tokens):
            l, tok = self._tokens[i]
            i += self._compile(i)
        return self

    def functions(self):
        return self._function

    def hastypes(self):
        hastypes = types
        hastypes.extend(self._parenttypes)
        hasclasses = [k for k in self.classes()]
        if self._name: hasclasses = ['.'.join(self._name, c) for c in hasclasses]
        hastypes.extend(hasclasses)
        return hastypes

    def names(self):
        names = []
        for i in [self._var, self._const, self._function]:
            names.extend(list(i.keys()))
        for pref in self._class:
            names.append(pref)
            c = self._class[pref]
            for name in c: names.append('.'.join([pref, name]))
        for pref in self._namespace:
            names.append(pref)
            c = self._namespace[pref]
            names.extend(['.'.join([pref, name]) for name in c.names()])
        return names

    def classes(self):
        return self._class

    def namespaces(self):
        return self._namespace

    def vars(self):
        return self._var

    def constants(self):
        return self._const
