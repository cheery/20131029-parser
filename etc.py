class SourceLocation(object):
    def __init__(self, path, start, stop):
        self.path = path
        self.start = start
        self.stop  = stop

    def __repr__(self):
        return "%s[%i:%i]" % (self.path, self.start, self.stop)

class SyntaxError(Exception):
    def __init__(self, source, message):
        Exception.__init__(self, message)
        self.source = source
