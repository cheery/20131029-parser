class AST(object):
    def __init__(self, type, children=(), string='', source=None):
        self.type = type
        self.children = children
        self.string = string
        self.source = source

    def append(self, child):
        self.children.append(child)

    def insert(self, index, child):
        self.children.insert(index, child)

    def extend(self, children):
        self.children.extend(children)

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def repr(self):
        reprs = [child.repr() for child in self.children]
        return '\n'.join(
            ["%s: %r @%r" % (self.type, self.string, self.source)] + reprs
        ).replace('\n', '\n  ')

    def find(self, types):
        if self.type in types:
            return (self,)
        ret = ()
        for child in self:
            ret += child.find(types)
        return ret
