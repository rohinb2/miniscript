from sly import Lexer, Parser

from miniscript_ast import *


class MiniScriptLexer(Lexer):
    tokens = { NULL, NUMBER, STRING, BOOLEAN, 
        OPERATOR,
        #PLUS, MINUS, TIMES, DIVIDE, 
        #SEMICOLON,
        IDENTIFIER,
        IF, ELSE, WHILE, FOR, FUNCTION, VAR,
        EQ, NE, GT, LT, GEQ, LEQ, ASSIGN
    }
    literals = {'(', ')', '{', '}', '[', ']', ';'}

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    ignore_whitespace = r'\s'
    ignore_comments = r'//.*'
    ignore_multicomment = r'\/\*([^*]|\*[^/])*\*\/'

    NULL = r'null'
    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t
    
    @_(r'"(\\.|[^"\\])*"')
    def STRING(self, t):
        # TODO process escape sequences
        t.value = t.value[1:-1]
        return t
    BOOLEAN = r'(true|false)'
    IDENTIFIER = r'[_$\w][_$\w\d]*'
    OPERATOR = r'\+|\-|\*|\/'
    IF = 'if'
    ELSE = 'else'
    WHILE = 'while'
    FOR = 'for'
    FUNCTION = 'function'
    VAR = 'var'

    EQ, NE, GT, LT, GEQ, LEQ, ASSIGN = '==', '!=', '>', '<', '>=', '<=', '='

    def error(self, t):
        print(f'{t.lineno}:{self.find_column(t.value, t)}: Illegal character: "{t.value[0]}". Ignoring...')
        self.index += 1


    @staticmethod
    def find_column(text, token):
        last_cr = text.rfind('\n', 0, token.index)
        if last_cr < 0:
            last_cr = 0
        column = (token.index - last_cr) + 1
        return column

class MiniScriptParser(Parser):
    tokens = MiniScriptLexer.tokens

    @_('expr OPERATOR expr')
    def expr(self, p):
        return Operator(p.expr0, p.expr1, p.OPERATOR)
    
    @_('"(" expr ")"')
    def expr(self, p): return p.expr

    @_('NULL')
    def expr(self, p): return Null

    @_('NUMBER')
    def expr(self, p): return Number(p.NUMBER)

    @_('STRING')
    def expr(self, p): return String()

    @_('IDENTIFIER')
    def expr(self, p): return Symbol(p[0])

if __name__ == "__main__":
    lexer = MiniScriptLexer()
    parser = MiniScriptParser()
    code = ''
    while True:
        try: 
            code += input() + '\n'
            print(repr(code))
        except EOFError:
            break
    print(parser.parse(lexer.tokenize(code)))