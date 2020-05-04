from sly import Lexer, Parser

from miniscript_ast import *


class MiniScriptLexer(Lexer):
    tokens = {
        NULL,
        NUMBER,
        STRING,
        BOOLEAN,
        PLUS, MINUS, TIMES, DIV, AND, OR, EQ, NEQ, LT, LE, GT, GE,
        ID,
        IF,
        ELSE,
        WHILE,
        FOR,
        FUNCTION,
        VAR,
        ASSIGN,
    }
    literals = {'(', ')', '{', '}', '[', ']', ';', '!'}

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
    ID = r'[_$\w][_$\w\d]*'
    ID['function'] = FUNCTION
    ID['if'] = IF
    ID['else'] = ELSE
    ID['while'] = WHILE
    ID['for'] = FOR
    ID['var'] = VAR
    PLUS, MINUS, TIMES, DIV = r'\+', '-', r'\*', '/'
    AND, OR = '&&', r'\|\|'
    EQ, NEQ, LT, LE, GT, GE = '==', '!=', '<', '<=', '>', '>='
    ASSIGN = '='

    def error(self, t):
        print(
            f'{t.lineno}:{self.find_column(t.value, t)}: Illegal character: "{t.value[0]}". Ignoring...'
        )
        self.index += 1

    @staticmethod
    def find_column(text, token):
        last_cr = text.rfind('\n', 0, token.index)
        if last_cr < 0:
            last_cr = 0
        column = (token.index - last_cr) + 1
        return column


class MiniScriptParser(Parser):
    """Parser for the miniscript language.
    miniscript has the following grammar:

    prog : stmt prog | fun_decl prog | empty

    fun_decl : "function" ID ( [arg [, arg]*] ) { stmt_list }

    stmt_list : stmt stmt_list | empty

    stmt : expr ;
        | if ( expr ) stmt [else stmt]
        | while ( expr ) stmt
        | { stmt_list }
    
    expr : expr op expr | ! expr | ( expr ) 
        | ID | NUM | STRING | true | false | null

    op : + | - | * | / | && | || | == | <= | => | < | > 
    """
    debugfile = 'parser.out'
    tokens = MiniScriptLexer.tokens
    precedence = (
        ('right', AND),
        ('right', OR),
        ('left', EQ, NEQ),
        ('left', GT, LT, GE, LE),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIV),
    )

    @_('stmt prog')
    def prog(self, p):
        return  # TODO

    @_('func prog')
    def prog(self, p):
        return # TODO
    
    @_('empty')
    def prog(self, p):
        pass # TODO

    @_('stmt stmt_list')
    def stmt_list(self, p):
        return [p.stmt] + p.stmt_list
    
    @_('empty')
    def stmt_list(self, p):
        return []
    
    # TODO
    @_('FUNCTION ID "(" args ")" "{" stmt_list "}"')
    def func(self, p):
        pass # TODO

    @_('ID args2')
    def args(self, p):
        return [p.ID] + p.args2

    @_('empty')
    def args(self, p):
        return []
    
    @_(', ID args2')
    def args2(self, p):
        return [p.ID] + p.args2
    
    @_('empty')
    def args2(self, p):
        return []

    @_('expr ";"')
    def stmt(self, p):
        return
    
    @_('empty ";"')
    def stmt(self, p):
        return
    
    @_('block')
    def stmt(self, p):
        return [p.stmt]

    @_('ifthenelse')
    def stmt(self, p):
        pass # TODO

    @_('whileloop')
    def stmt(self, p):
        pass # TODO

    @_('IF "(" expr ")" stmt ELSE stmt')
    def ifthenelse(self, p):
        pass # TODO

    @_('IF "(" expr ")" stmt')
    def ifthenelse(self, p):
        pass # TODO
    
    @_('"{" stmt_list "}"')
    def block(self, p):
        return p.stmt_list
    
    @_('WHILE "(" expr ")" block')
    def whileloop(self, p);
        pass # TODO

    @_(*(f'expr {op} expr' for op in [PLUS, MINUS, TIMES, DIV, AND, OR, EQ, NEQ, LT, LE, GT, GE]))
    def expr(self, p):
        return BinOp(p[1], p.expr0, p.expr1)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr
    
    @_('"!" expr')
    def expr(self, p):
        pass # TODO

    @_('NULL')
    def expr(self, p):
        return Null

    @_('NUMBER')
    def expr(self, p):
        return Number(p.NUMBER)

    @_('STRING')
    def expr(self, p):
        return String()

    @_('ID')
    def expr(self, p):
        return Symbol(p[0])

    @_('BOOLEAN')
    def expr(self, p):
        return Boolean(p.BOOLEAN)

    @_('')
    def empty(self, p):
        return []


if __name__ == '__main__':
    lexer = MiniScriptLexer()
    parser = MiniScriptParser()
    code = ''
    while True:
        try:
            code += input() + '\n'
            print(repr(code))
        except EOFError:
            break
    print(list(lexer.tokenize(code)))
    tree = parser.parse(lexer.tokenize(code))
    print(tree)
    print(repr(tree))
