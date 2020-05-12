from typing import Optional, Sequence, Callable, TypeVar
T = TypeVar('T')


class NodeVisitor:
    """Visitor class for ast nodes.
    Subclasses should implement visit_<Name> for any ast nodes they are interested in.
    The fallback `generic_visit` traverses the whole tree and recursively 
    """
    def visit(self, tree: 'AST'):
        """Calls the appropriate `visit_<Name>` method for `tree`.
        If no suitable visitor method is found this calls `generic_visit`
        """
        # inspired by cpython ast.py
        method = 'visit_' + type(tree).__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(tree)

    def generic_visit(self, tree: 'AST'):
        """Generic visitor method.
        """
        for field, value in tree._locals:
            if isinstance(tree, AST):
                self.visit(getattr(self, field))

    @staticmethod
    def iter_fields(tree):
        for name in dir(tree):
            field = getattr(tree, name)
            if isinstance(field, list):
                for f in field:
                    self.visit(f)
            elif isinstance(field, AST):
                self.visit(field)


# only defined for type checking
def node(f: Callable[..., T]) -> Callable[..., T]:
    pass


class AstMeta(type):
    def node(cls):
        def decorate(f):
            f.arg_locals = f.__code__.co_varnames[1:f.__code__.co_argcount]
            return f

        return decorate

    @classmethod
    def __prepare__(meta, cls, *args, **kwargs):
        return {'node': meta.node(cls)}

    def __new__(meta, classname, bases, attributes):
        cls = super().__new__(meta, classname, bases, attributes)
        if hasattr(cls.__init__, 'arg_locals'):
            setattr(cls, '_locals', cls.__init__.arg_locals)
        return cls


class AST(metaclass=AstMeta):
    _locals: Sequence[str]

    @node
    def __init__(self):
        pass

    def __repr__(self):
        return f'{type(self).__name__}({ ", ".join(repr(getattr(self, l)) for l in self._locals) })'


class Stmt(AST):
    pass


class Expr(Stmt):
    def __str__(self) -> str:
        return self.str_prec(0) + ';'

    def str_prec(self, precedence: int) -> str:
        return "Expr"


class If(Stmt):
    #_locals = ['cond', 'then', 'els']

    @node
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
    @node
    def __init__(self, cond: Expr, body: Stmt):
        self.cond = cond
        self.body = body


class BinOp(Expr):
    @node
    def __init__(self, op: str, left: AST, right: AST):
        self.left: AST = left
        self.right: AST = right
        self.op: str = op

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
    def precedence_of(cls, op: str, side: Optional[str] = None) -> int:
        return cls._prec.get(op, 0)

    def inner_precedence(self, side: Optional[str] = None) -> int:
        if side is not None and side != self._assoc.get(self.op, 'left'):
            return max(self.precedence_of(self.op) + 1, 0)
        return self.precedence_of(self.op, side)

    @property
    def precedence(self) -> int:
        return self.precedence_of(self.op)

    #def str_prec(self, prec: int) -> str:
    #    left = self.left.str_prec(self.inner_precedence('left'))
    #    right = self.right.str_prec(self.inner_precedence('right'))
    #    s = f'{left} {self.op} {right}'
    #    if self.precedence < prec:
    #        return f"({s})"
    #    else:
    #        return s

    #def __repr__(self):
    #    return f"{type(self).__name__}({repr(self.op)}, {repr(self.left)}, {repr(self.right)})"


class Not(Expr):
    @node
    def __init__(self, expr: Expr):
        self.expr = expr

    #def __repr__(self):
    #    return r'{type(self).__name__}({self.expr})'

    def str_prec(self, prec: int):
        return f'!{self.expr.str_prec(BinOp.precedence_of("!"))}'


class Assign(Stmt):
    @node
    def __init__(self, var: Expr, value: Expr):
        self.var = var
        self.value = value

    #def __repr__(self):
    #    return f'{type(self).__name__}({repr(self.var)}, {repr(self.value)})'


class VarDecl(Stmt):
    @node
    def __init__(self, name: str, initial_value: Optional[Expr] = None):
        self.name = name
        self.value = initial_value

    #def __repr__(self):
    #    return f'{type(self).__name__}({repr(self.var)}, {repr(self.value)})'


class Literal(Expr):
    @node
    def __init__(self, value):
        self.value = value

    def str_prec(self, prec: int) -> str:
        return str(self.value)

    #def __repr__(self):
    #    return f"{type(self).__name__}({repr(self.value)})"


class String(Literal):
    pass

    def str_prec(self, prec):
        return f'"{self.value}""'


class Boolean(Literal):
    pass


class Number(Literal):
    pass


class Singleton(Literal):
    @node
    def __init__(self):
        Literal.__init__(self, None)

    # def __repr__(self):
    #     return f'{type(self).__name__}()'


class Null(Singleton):
    pass


class Undefined(Singleton):
    pass


class Name(Expr):
    @node
    def __init__(self, name):
        self.name = name


class Attribute(Expr):
    @node
    def __init__(self, value: Expr, attr: str):
        self.value = value
        self.attr = attr

    # def __repr__(self):
    #     return f'{type(self).__name__}({repr(self.value)}, {repr(self.attr)})'


class Call(Expr):
    @node
    def __init__(self, func: Expr, args: Sequence[Expr]):
        self.func = func
        self.args = args

    # def __repr__(self):
    #     return f'{type(self).__name__}({repr(self.func)}, {repr(self.args)})'


class FunctionDef(Stmt):
    @node
    def __init__(self, name: str, args: Sequence[str], body: Sequence[Stmt]):
        self.name = name
        self.args = args
        self.body = body

    #def __repr__(self):
    #    return f'{type(self).__name__}({repr(self.name)}, {repr(self.args)}, {repr(self.body)})'
