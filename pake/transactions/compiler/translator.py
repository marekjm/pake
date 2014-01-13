#!/usr/bin/env python3

"""Part of Akemetal responsible for translating tokens into
executable form.
"""


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
    return (params, i)


def functioncall(tokens, n, src):
    """Translates tokens into function call.
    """
    ex = {'call': '', 'params': {}}
    param_list_start, param_list_end = 0, 0
    leap = 0
    i = n
    while i < len(tokens):
        l, tok = tokens[i]
        if tok == '(':
            param_list_start = i+1
            break
        i += 1
        leap += 1
    leap += 2
    ex['call'] = tokens[n][1]
    ex['params'], i = _functioncallparams(tokens[param_list_start:], src)
    leap += i
    return (ex, leap)


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

    def getfunctions(self):
        return self._ns._function
    
    def getcalls(self):
        return self._ns._calls


class NamespaceTranslator():
    def __init__(self, tokens, source):
        self._tokens = tokens
        self._source = source
        self._function = {}
        self._var = {}
        self._const = {}
        self._class = {}
        self._namespace = {}
        self._calls = []

    def __getitem__(self, access):
        item = None
        if access in self._function: item = self._function[access]
        elif access in self._var: item = self._var[access]
        elif access in self._const: item = self._const[access]
        elif access in self._class: item = self._class[access]
        elif access in self._namespace: item = self._namespace[access]
        return item

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

    def _compilekw_include(self, index):
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
            msg = ('line {0}: "{1}": token: {2}\ncaused by error in included file "{3}":\n{4}: {5}'
                   .format(line+1, tokenizer.rebuild(line, self._source), tok, path, type(error), error))
            raise errors.CompilationError(msg)
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
        ns = NamespaceTranslator(nstokens[3:-1], self._source).translate()
        self._namespace[name] = ns
        return leap

    def _compilekeyword(self, index):
        line, tok = self._tokens[index]
        if tok == 'include':
            leap = self._compilekw_include(index)
        elif tok == 'namespace':
            leap = self._compilekw_namespace(index)
        else:
            msg = 'line {0}: "{1}": keyword not yet implemented: {2}'.format(line+1, tokenizer.rebuild(line, self._source), tok)
            raise errors.CompilationError(msg)
        return leap

    def _compile(self, index):
        l, tok = self._tokens[index]
        if tok == 'function':
            func, leap = functiondeclaration(self._tokens, (index+1), self._source)
            self._function[func['name']] = func
        elif tok in self._function:
            call, leap = functioncall(self._tokens, index, self._source)
            self._calls.append(call)
        elif tok == ';':
            leap = 1
        elif tok in shared.getkeywords():
            leap = self._compilekeyword(index)
        elif shared.isvalidname(tok):
            raise errors.UndeclaredReferenceError('line {0}: "{1}": undeclared reference: "{2}"'.format(l+1, tokenizer.rebuild(l, self._source), tok))
        else:
            raise errors.CompilationError('line {0}: "{1}": token: {2}'.format(l+1, tokenizer.rebuild(l, self._source), tok))
        return leap

    def translate(self):
        i = 0
        while i < len(self._tokens):
            l, tok = self._tokens[i]
            i += self._compile(i)
        return self

    def functions(self):
        return self._function

    def vars(self):
        return self._var

    def constants(self):
        return self._const

    def classes(self):
        return self._class

    def namespaces(self):
        return self._namespace
