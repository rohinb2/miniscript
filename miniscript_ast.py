from typing import Optional, Sequence


class NodeVisitor:
    def visit(self, tree: 'Ast'):
        # inspired by cpython ast.py
        method = 'visit_' + type(tree).__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(tree)

    def generic_visit(self, tree: 'Ast'):
        for field, value in dic(tree):
            if isinstance(tree, Ast):
                self.visit(field)

    @staticmethod
    def iter_fields(tree):
        for name in dir(tree):
            field = getattr(tree, name)
            if isinstance(field, list):
                for f in field:
                    self.visit(f)
            elif isinstance(field, AST):
                self.visit(field)


class AST:
    def __init__(self):
        pass

    def visit(self, visitor: NodeVisitor):
        pass


class Stmt(AST):
    pass


class StmtList(list):
    def __str__(self):
        return '\n'.join(map(str, self))

    def __repr__(self):
        return f'{type(self).__name__}({list.__repr__(self)})'


class Expr(Stmt):
    def __str__(self) -> str:
        return self.str_prec(0) + ';'

    def str_prec(self, precedence: int) -> str:
        return "Expr"


class If(Stmt):
    def __init__(self, cond: Expr, then: Stmt, els: Optional[Stmt] = None):
        self.cond = cond
        self.then = then
        self.els = els

    def __repr__(self):
        elstring = ''
        if self.els is not None:
            elstring = f', {repr(self.els)}'
        return f'{type(self).__name__}({repr(self.cond)}, {repr(self.then)}{elstring})'

    def __str__(self):
        ifstring = r'if ({self.cond}) {\nself.then}'
        if self.els is not None:
            ifstring += r' else {self.els}'


class While(Stmt):
    def __init__(self, cond: Expr, body: Stmt):
        self.cond = cond
        self.body = body


class BinOp(Expr):
    def __init__(self, op: str, left: AST, right: AST):
        self.left: AST = left
        self.right: AST = right
        print(type(self.left), type(self.right))
        self.op: AST = op

    def visit(self, v: NodeVisitor) -> None:
        v.visit_operator(self)

    _prec = {
        '&&': 6,
        '||': 5,
        '==': 11,
        '!=': 11,
        '>': 12,
        '<': 12,
        '>=': 12,
        '<=': 12,
        '+': 14,
        '-': 14,
        '*': 15,
        '/': 15,
        '%': 15,
        '!': 17,
    }
    # setting _assoc to None results in same str result of
    # (a && b) && c == a && b && c == a && (b && c)
    _assoc = {'!': 'left', '&&': None, '||': None, '+': None}

    @classmethod
    def precedence_of(cls,
                      op: Optional[str] = None,
                      side: Optional[str] = None) -> int:
        return cls._prec.get(op, 0)

    def inner_precedence(self, side: Optional[str] = None) -> int:
        if side is not None and side != self._assoc.get(self.op, 'left'):
            return max(self.precedence_of(self.op) + 1, 0)
        return self.precedence_of(self.op, side)

    @property
    def precedence(self) -> int:
        return self.precedence_of(self.op)

    def str_prec(self, prec: int) -> str:
        left = self.left.str_prec(self.inner_precedence('left'))
        right = self.right.str_prec(self.inner_precedence('right'))
        s = f'{left} {self.op} {right}'
        if self.precedence < prec:
            return f"({s})"
        else:
            return s

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.op)}, {repr(self.left)}, {repr(self.right)})"


class Not(Expr):
    def __init__(self, expr: Expr):
        self.expr = expr

    def __repr__(self):
        return r'{type(self).__name__}({self.expr})'

    def str_prec(self, prec: int):
        return f'!{self.expr.str_prec(BinOp.precedence_of("!"))}'


class FunctionCall(Expr):
    def __init__(self, func: Expr, args: Sequence[Expr]):
        pass


class Named(Expr):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f'{type(self).__name__}({repr(self.name)})'


class MemberAccess(Expr):
    def __init__(self, name: str, obj: Expr):
        self.name = name
        self.object = obj

    def __repr__(self):
        return f'{type(self).__name__}({repr(self.name)}, {repr(self.object)})'


class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def str_prec(self, prec: int) -> str:
        return str(self.value)

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.value)})"


class String(Literal):
    def visit(self, v: NodeVisitor):
        v.visit_String(self)

    def str_prec(self, prec):
        return f'"{self.value}""'


class Boolean(Literal):
    def visit(self, v: NodeVisitor):
        v.visit_Boolean(self)


class Number(Literal):
    def visit(self, v: NodeVisitor):
        v.visit_Number(self)


class Null(Literal):
    def __init__(self):
        Literal.__init__(self, None)

    def visit(self, v: NodeVisitor):
        v.visit_Null(self)

    def str_prec(self, prec):
        return "null"


class Symbol(Expr):
    def __init__(self, name):
        self.name = name

    def visit(self, v: NodeVisitor):
        v.visit_String(self)


class FunctionDef(Stmt):
    def __init__(self, name: str, args: Sequence[str], body: StmtList):
        self.name = name
        self.args = args
        self.body = body

    def __repr__(self):
        return f'{type(self).__name__}({repr(self.name)}, {repr(self.args)}, {repr(self.body)})'
