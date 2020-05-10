from sly import Lexer, Parser

from miniscript_ast import *


class MiniScriptLexer(Lexer):
    tokens = {
        NULL,
        NUMBER,
        STRING,
        BOOLEAN,
        PLUS,
        MINUS,
        TIMES,
        DIV,
        AND,
        OR,
        EQ,
        NEQ,
        LT,
        LE,
        GT,
        GE,
        ID,
        IF,
        ELSE,
        WHILE,
        FOR,
        FUNCTION,
        VAR,
        ASSIGN,
    }
    literals = {'(', ')', '{', '}', '[', ']', ';', '!', ','}

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

    @_('stmt_list')
    def prog(self, p):
        return p[0]

    @_('stmt_list stmt')
    def stmt_list(self, p):
        if p.stmt is not None:
            p.stmt_list.append(p.stmt)
        return p.stmt_list  # [p.stmt] + p.stmt_list

    @_('empty')
    def stmt_list(self, p):
        return StmtList()

    @_('func')
    def stmt(self, p):
        return p[0]

    @_('FUNCTION ID "(" args ")" block')
    def func(self, p):
        return FunctionDef(p.ID, p.args, p.block)

    @_('args2 ID')
    def args(self, p):
        p.args2.append(p.ID)
        return p.args2

    @_('empty')
    def args(self, p):
        return []

    @_('args2 ID ","')
    def args2(self, p):
        p.args2.append(p.ID)
        return p.args2

    @_('empty')
    def args2(self, p):
        return []

    @_('expr ";"')
    def stmt(self, p):
        return p.expr

    @_('empty ";"')
    def stmt(self, p):
        return
    
    @_('name "=" expr ";"')
    def stmt(self, p):
        return Assign(p.name, p.expr)

    @_('block')
    def stmt(self, p):
        return [p.stmt]

    @_('ifthenelse')
    def stmt(self, p):
        return p[0]

    @_('whileloop')
    def stmt(self, p):
        return p[0]

    @_('IF "(" expr ")" stmt ELSE stmt')
    def ifthenelse(self, p):
        return If(p.expr, p.stmt0, p.stmt1)

    @_('IF "(" expr ")" stmt')
    def ifthenelse(self, p):
        return If(p.expr, p.stmt)

    @_('"{" stmt_list "}"')
    def block(self, p):
        return p.stmt_list

    @_('WHILE "(" expr ")" stmt')
    def whileloop(self, p):
        return While(p.expr, p.stmt)

    @_(*(f'expr {op} expr'
         for op in [PLUS, MINUS, TIMES, DIV, AND, OR, EQ, NEQ, LT, LE, GT, GE])
       )
    def expr(self, p):
        return BinOp(p[1], p.expr0, p.expr1)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('"!" expr')
    def expr(self, p):
        return Not(p.expr)

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
    
    @_('name "." ID')
    def name(self, p):
        pass

    @_('ID')
    def name(self, p):
        pass

    @_('')
    def empty(self, p):
        return []

    def _error(self, p):
        print(f'syntax error at {p}')
        next(self.tokens, None)
        self.restart()
        return p


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
    print(list(map(lambda x: (x.type, x.value), lexer.tokenize(code))))
    tree = parser.parse(lexer.tokenize(code))
    print(tree)
    print(repr(tree))
