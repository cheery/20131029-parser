from etc import SyntaxError

def match(pattern, obj):
    if pattern == None:
        return True
    elif isinstance(pattern, tuple):
        return obj in pattern
    else:
        return obj == pattern

class TokenFeed(object):
    def __init__(self, it):
        self.it = it
        try:
            self.current = self.it.next()
        except StopIteration:
            self.current = None

    def advance(self, type=None, string=None):
        current = self.current
        if current == None:
            raise Exception("End of stream breached.")
        if not match(type, current.type):
            raise SyntaxError(current.source, "expected %r, got %s" % (type, current.type))
        if not match(string, current.string):
            raise SyntaxError(current.source, "expected string %r, got %r" % (string, current.string))
        try:
            self.current = self.it.next()
        except StopIteration:
            self.current = None
        return current

    def match(self, type=None, string=None):
        current = self.current
        if current == None:
            return False
        if not match(type, current.type):
            return False
        if not match(string, current.string):
            return False
        return True

    def ignore(self, type=None, string=None):
        if self.match(type, string):
            self.advance()
            return True
        else:
            return False
