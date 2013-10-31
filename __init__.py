from tokenize import tokenize_file
from tokenfeed import TokenFeed
from ast import AST
from etc import SyntaxError

term_types = ('identifier', 'lparen', 'number', 'string')
def parse_term(feed):
    if feed.match('keyword', 'def'):
        token = feed.advance()
        argv = AST('argv', [])
        while feed.match('identifier'):
            identifier = feed.advance()
            argv.append(AST('identifier', (), identifier.string, identifier.source))
        return AST('def', [argv], source=token.source)
    token = feed.advance(term_types)
    if token.type in ('identifier', 'number', 'string'):
        return AST(token.type, (), token.string, token.source)
    if token.type == 'lparen':
        stmt = parse_expr(feed)
        feed.advance('rparen')
        return stmt
    raise Exception("FAIL")

def match_term(feed):
    if feed.match('keyword', 'def'):
        return True
    return feed.match(term_types)

def parse_expr100(feed):
    expr = parse_term(feed)
    while feed.match(('dot', 'member')):
        token = feed.advance()
        if token.type == 'dot':
            expr = AST('call', [expr], source=token.source)
        elif token.type == 'member':
            expr = AST('member', [expr], token.string, token.source)
    return expr

def parse_expr50(feed):
    expr = parse_expr100(feed)
    while feed.match('symbol', ('+', '-')):
        token = feed.advance()
        expr = AST('op', [expr, parse_expr100(feed)], token.string)
    return expr

def parse_expr10(feed):
    expr = parse_expr50(feed)
    while feed.match('symbol', ('==', '!=')):
        token = feed.advance()
        expr = AST('op', [expr, parse_expr10(feed)], token.string)
    return expr

def parse_expr(feed):
    stmt = parse_expr10(feed)
    if match_term(feed):
        stmt = AST('call', [stmt])
        while match_term(feed):
            stmt.append(parse_expr10(feed))
    if feed.match('symbol', ('=', ':=')):
        token = feed.advance('symbol', ('=', ':='))
        return AST('op', [stmt, parse_expr(feed)], token.string)
    return stmt

def parse_stmt(feed):
    if feed.ignore('keyword', 'import'):
        token = feed.advance('identifier')
        return AST('import', (), token.string, token.source)
    elif feed.ignore('keyword', 'if'):
        stmt = AST('if', [parse_expr(feed)])
        stmt.extend(parse_block(feed))
        return stmt
    elif feed.ignore('keyword', 'elif'):
        stmt = AST('elif', [parse_expr(feed)])
        stmt.extend(parse_block(feed))
        return stmt
    elif feed.ignore('keyword', 'else'):
        stmt = AST('else', [])
        stmt.extend(parse_block(feed))
        return stmt
    else:
        expr = parse_expr(feed)
        if feed.match('indent'):
            blocks = expr.find(('def',))
            if len(blocks) > 0:
                blocks[0].extend(parse_block(feed))
            elif expr.type != 'call':
                expr = AST('call', [expr])
                expr.extend(parse_block(feed))
            else:
                expr.extend(parse_block(feed))
        return expr

def parse_block(feed):
    feed.advance('indent')
    if not feed.ignore('keyword', 'pass'):
        yield parse_stmt(feed)
        while feed.ignore('newline'):
            if not feed.ignore('keyword', 'pass'):
                yield parse_stmt(feed)
    feed.advance('dedent')

def parse_program(feed):
    program = AST('program', [])
    while feed.ignore('newline'):
        if not feed.ignore('keyword', 'pass'):
            program.append(parse_stmt(feed))
    return program


keywords = set(('def', 'if', 'elif', 'else', 'pass', 'import'))
symbols = set(('=', ':=', ':', '+', '-', '==', '!=', '!'))

def parse_file(path):
    feed = TokenFeed(tokenize_file(path, keywords, symbols))
    program = parse_program(feed)
    if feed.current != None:
        raise SyntaxError(feed.current.source, "parsing terminated")
    return program

if __name__=='__main__':
    program = parse_file('input')
    print program.repr()
