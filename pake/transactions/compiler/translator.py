#!/usr/bin/env python3

"""Part of Akemetal responsible for translating tokens into
executable form.
"""


from . import tokenizer, shared, errors


types = ['int', 'float', 'string', 'undefined', 'void']


def _functioncallparams(tokens, src):
    """Compile function call parameter list -> (...).
    Steps:
        0*  define param name,
        1.  define param value,
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
            raise errors.CompilationError('line {0}: "{1}": token: {2}'.format(l+1, tokenizer.rebuild(l, src), tok))
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
    i = 0
    while i < len(tokens):
        l, tok = tokens[i]
        if tok == '(':
            param_list_start = i
            break
        i += 1
        leap += 1
    leap += 2
    ex['call'] = tokens[n][1]
    ex['params'], i = _functioncallparams(tokens[n+param_list_start-1:], src)
    leap += i
    return (ex, leap)


def _functiondeclarationparams(tokens):
    """Compile function declaration parameter list -> (...).
    Steps:

        0.  define parm type (default: undefined),
        1.  define param name,
        2*  define param default value (default: unspecified),
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
        else:
            raise errors.CompilationError('line {0}: "{1}": token: {2}'.format(l+1, tokenizer.rebuild(l, tokens), tok))
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
    leap += 2
    if param_list_start != 3 or tokens[leap][1] != ';':
        l = tokens[n+leap][0]
        if not src: src = tokens
        raise errors.CompilationError('line {0}: "{1}"'.format(l+1, tokenizer.rebuild(l, src)))
    param_tokens = tokens[param_list_start:param_list_end+1]
    params, ex['param_order'] = _functiondeclarationparams(param_tokens[1:-1])
    for p in params:
        ex['params'][p['name']] = {}
        for k in ['default', 'type']:
            ex['params'][p['name']][k] = p[k]
    return (ex, leap)


class Translator():
    """Translator for Metal.

    NOTICE: Currently there is no way to store the executable form.
            The language is not designed to be a full-feature creation.
    """
    def __init__(self):
        self._src = []
        self._tokens = []
        self._calls = []
        self._functions = {}

    def take(self, source):
        """Takes :source as string.
        """
        tokens = tokenizer.tokenize(source)
        self._src = tokens
        self._tokens = tokenizer.strip(tokens)
        return self

    def _compile(self, index):
        l, tok = self._tokens[index]
        if tok == 'function':
            func, leap = functiondeclaration(self._tokens, (index+1), self._src)
            self._functions[func['name']] = func
        elif tok in self._functions:
            call, leap = functioncall(self._tokens, index, self._src)
            self._calls.append(call)
        elif tok == ';':
            leap = 1
        elif shared.isvalidname(tok):
            raise errors.UndeclaredReferenceError('line {0}: "{1}": undeclared reference: "{2}"'.format(l+1, tokenizer.rebuild(l, self._src), tok))
        else:
            raise errors.CompilationError('line {0}: "{1}": token: "{2}"'.format(l+1, tokenizer.rebuild(l, self._src), tok))
        return leap

    def translate(self):
        i = 0
        while i < len(self._tokens):
            l, tok = self._tokens[i]
            i += self._compile(i)
        return self

    def getfunctions(self):
        return self._functions
    
    def getcalls(self):
        return self._calls
