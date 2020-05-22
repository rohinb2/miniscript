from typing import Optional, Sequence, Callable, TypeVar
T = TypeVar('T')

__all__ = [
    'NodeVisitor', 'Ast', 'Attribute', 'BinOp', 'Boolean', 'Call', 'Expr', 'FunctionDef', 'If',
    'Literal', 'Name', 'Array', 'Index', 'NodeVisitor', 'UnaryOp', 'Null', 'Number', 'Sequence',
    'Singleton', 'Stmt', 'String', 'Undefined', 'VarDecl', 'While', 'Return', 'Assign', 'Jump',
    'ConditionalJump', 'Code'
]


class NodeVisitor:
    """Visitor class for ast nodes.
    Subclasses should implement visit_<Name> for any ast nodes they are interested in.
    The fallback `generic_visit` traverses the whole tree and recursively 
    """
    def visit(self, tree: 'Ast'):
        """Calls the appropriate `visit_<Name>` method for `tree`.
        If no suitable visitor method is found this calls `generic_visit`
        """
        # inspired by cpython ast.py
        method = 'visit_' + type(tree).__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(tree)

    def generic_visit(self, tree: 'Ast'):
        """Generic visitor method.
        """
        for field, value in tree._locals:
            if isinstance(tree, Ast):
                self.visit(getattr(self, field))
        return tree

    @staticmethod
    def iter_fields(tree):
        for name in dir(tree):
            field = getattr(tree, name)
            if isinstance(field, list):
                for f in field:
                    self.visit(f)
            elif isinstance(field, Ast):
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


class Ast(metaclass=AstMeta):
    _locals: Sequence[str]

    @node
    def __init__(self):
        pass

    def __repr__(self):
        return f'{type(self).__name__}({ ", ".join(repr(getattr(self, l)) for l in self._locals) })'

    def __eq__(self, other):
        if (type(self) != type(other)): return False
        if (self._locals != other._locals): return False
        for s, o in zip(self._locals, other._locals):
            if getattr(self, s) != getattr(other, o): return False
        return True


class Code(metaclass=AstMeta):
    @node
    def __init__(self):
        pass

    def __eq__(self, other):
        if type(self) != type(other): return False
        for l in self._locals:
            if getattr(self, l) != getattr(other, l): return False
        return True


class Stmt(Ast):
    pass


class Expr(Stmt, Code):
    pass


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

    # def __str__(self):
    #     ifstring = r'if ({self.cond}) {\nself.then}'
    #     if self.els is not None:
    #         ifstring += r' else {self.els}'


class While(Stmt):
    @node
    def __init__(self, cond: Expr, body: Stmt):
        self.cond = cond
        self.body = body


class BinOp(Expr):
    @node
    def __init__(self, op: str, left: Ast, right: Ast):
        self.left: Ast = left
        self.right: Ast = right
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


class UnaryOp(Expr):
    @node
    def __init__(self, op: str, expr: Expr):
        self.op = op
        self.expr = expr


class Assign(Stmt, Code):
    @node
    def __init__(self, target: Expr, value: Expr):
        self.target = target
        self.value = value


class Literal(Expr, Code):
    @node
    def __init__(self, value):
        self.value = value


class Singleton(Literal):
    @node
    def __init__(self):
        Literal.__init__(self, None)

    # def __repr__(self):
    #     return f'{type(self).__name__}()'


class String(Literal):
    pass


class Boolean(Literal):
    pass


class Number(Literal):
    pass


class Null(Singleton):
    pass


class Undefined(Singleton):
    pass


class Name(Expr):
    @node
    def __init__(self, name):
        self.name = name


class Array(Expr):
    @node
    def __init__(self, values: Sequence[Expr] = []):
        self.values = values


class Index(Expr):
    @node
    def __init__(self, target: Expr, index: Expr):
        self.target = target
        self.index = index


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


class Return(Expr, Code):
    @node
    def __init__(self, expr: Expr = Undefined()):
        self.expr = expr


class VarDecl(Stmt):
    @node
    def __init__(self, name: Name, value: Optional[Expr] = None):
        self.name = name
        self.value = value


class FunctionDef(Stmt):
    @node
    def __init__(self,
                 name: Optional[Name] = None,
                 args: Sequence[Name] = [],
                 body: Sequence[Stmt] = []):
        self.name = name
        self.args = args
        self.body = body


# some internal code classes:
class Jump(Code):
    """Represents a relative jump by a specified offset.
    """
    @node
    def __init__(self, offset: int):
        self.offset = offset

    def __repr__(self):
        return f'{type(self).__name__}({self.offset})'


class ConditionalJump(Code):
    @node
    def __init__(self, expr: Expr, offset: int):
        self.offset = offset
        self.expr = expr

    def __repr__(self):
        return f'{type(self).__name__}({self.expr}, {self.offset})'