from etc import SourceLocation, SyntaxError

class Token(object):
    def __init__(self, type, string='', source=None):
        self.type = type
        self.string = string
        self.source = source

    def __repr__(self):
        return "%r: %s %r" % (self.source, self.type, self.string)

class Newline(object):
    def __init__(self, ret, string=''):
        self.ret = ret
        self.count = 0
        self.string = string

    def character(self, ch):
        if ch == ' ':
            self.count += 1
            self.string += ch
            return self
        elif ch == '\n':
            self.count = 0
            self.string += ch
            return self
        elif ch == '#':
            self.string += ch
            return Comment(self.ret, self.string)
        else:
            return self.emit().character(ch)

    def eof(self):
        return self.emit(False).eof()

    def emit(self, emit_newline=True):
        indent = self.ret.indent
        current = indent[-1]
        if current < self.count:
            indent.append(self.count)
            return self.ret.add(Token('indent', self.string))
        else:
            while indent[-1] > self.count:
                indent.pop(-1)
                self.ret.add(Token('dedent', self.string))
            if indent[-1] != self.count:
                raise SyntaxError(self.ret.source, "broken dedent")
            if emit_newline:
                self.ret.add(Token('newline', self.string))
            return self.ret

class Comment(object):
    def __init__(self, ret, string):
        self.ret = ret
        self.string = string

    def character(self, ch):
        self.string += ch
        if ch == '\n':
            return Newline(self.ret, self.string)
        else:
            return self
    
    def eof(self):
        return self.ret.eof()

class Identifier(object):
    def __init__(self, ret, string):
        self.ret = ret
        self.string = string
    
    def character(self, ch):
        if ch.isalnum() or ch == '_':
            self.string += ch
            return self
        else:
            return self.emit().character(ch)

    def emit(self):
        which = 'identifier'
        if self.string in self.ret.keywords:
            which = 'keyword'
        return self.ret.add(Token(which, self.string))

    def eof(self):
        return self.emit().eof()

class Symbol(object):
    def __init__(self, ret, string):
        self.ret = ret
        self.string = string
    
    def character(self, ch):
        string = self.string + ch
        if string in self.ret.symbols:
            self.string = string
            return self
        else:
            return self.emit().character(ch)

    def emit(self):
        return self.ret.add(Token('symbol', self.string))

    def eof(self):
        return self.emit().eof()

class Dot(object):
    def __init__(self, ret, string):
        self.ret = ret
        self.string = string
    
    def character(self, ch):
        if ch.isalnum() or ch == '_':
            self.string += ch
            return self
        else:
            return self.emit().character(ch)

    def emit(self):
        which = 'member'
        if self.string == "":
            which = 'dot'
            self.string = "."
        return self.ret.add(Token(which, self.string))

    def eof(self):
        return self.emit().eof()

class String(object):
    def __init__(self, ret, term, string=''):
        self.ret = ret
        self.term = term
        self.string = string

    def character(self, ch):
        if ch == self.term:
            return self.ret.add(Token('string', self.string), +1)
        else:
            self.string += ch
            return self

    def eof(self):
        raise SyntaxError(self.ret.source, "missing string terminator %r" % self.term)

class Number(object):
    def __init__(self, ret, string):
        self.ret = ret
        self.string = string

    def character(self, ch):
        if ch.isalnum() or ch == '.':
            self.string += ch
            return self
        else:
            return self.emit().character(ch)

    def emit(self):
        return self.ret.add(Token('number', self.string))

    def eof(self):
        return self.emit().eof()

class Idle(object):
    def __init__(self, path, keywords, symbols):
        self.path = path
        self.keywords = keywords
        self.symbols = symbols
        self.tokens = []
        self.indent = [0]
        self.start = 0
        self.stop  = 0
    
    def character(self, ch):
        self.start = self.stop
        if ch.isalpha() or ch == '_':
            return Identifier(self, ch)
        if ch.isdigit():
            return Number(self, ch)
        if ch == '.':
            return Dot(self, "")
        if ch == '#':
            return Comment(self, ch)
        if ch == '\n':
            return Newline(self, ch)
        if ch == ' ':
            return self
        if ch in self.symbols:
            return Symbol(self, ch)
        if ch == '"' or ch == "'":
            return String(self, ch)
        if ch == '(':
            return self.add(Token('lparen', ch), +1)
        if ch == ')':
            return self.add(Token('rparen', ch), +1)
        raise SyntaxError(self.source, "bad character %r" % ch)

    def eof(self):
        return self.tokens

    @property
    def source(self):
        return SourceLocation(self.path, self.stop, self.stop+1)

    def add(self, token, offset=0):
        token.source = SourceLocation(self.path, self.start, self.stop + offset)
        self.tokens.append(token)
        return self

def tokenize_file(path, keywords, symbols):
    with open(path) as fd:
        source = fd.read()
    idle = Idle(path, keywords, symbols)
    mode = Newline(idle)
    index = 0
    for index, ch in enumerate(source):
        idle.stop = index
        mode = mode.character(ch)
    idle.stop = index+1
    return iter(mode.eof())

if __name__=='__main__':
    keywords = set(('def', 'if', 'elif', 'else'))
    symbols = set(('=', ':=', ':'))
    for token in tokenize_file('input', keywords, symbols):
        print token
