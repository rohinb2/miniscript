
class NodeVisitor:
    def visit_Operator(self, o: 'Operator'): pass
    def visit_Null(self, n: 'Null'): pass
    def visit_Number(self, n: 'Number'): pass
    def visit_Boolean(self, b: 'Boolean'): pass
    def visit_String(self, s: 'String'): pass
    def visit_Symbol(self, s: 'Symbol'): pass

class AST:
    def __init__(self):
        pass

    def visit(self, visitor: NodeVisitor):
        pass

    def __str__(self):
        self._str_prec(0)

class Expr(AST):
    pass

class Operator(Expr):
    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op
    
    def visit(self, v: NodeVisitor):
        v.visit_operator(self)
    
    _prec = {'+':17, '-': 17, '*': 16, '/': 16, '&&': 6, '||': 5}
    @classmethod
    def precedence(cls.op):
        return cls._prec.get(cls, op, 0)

    def _str_prec(self, prec):
        pass

class Literal(Expr):
    def __init__(self, value):
        self.value = value
    
class String(Literal):
    def visit(self, v: NodeVisitor):
        v.visit_String(self)

class Boolean(Literal):
    def visit(self, v: NodeVisitor):
        v.visit_Boolean(self)

class Number(Literal):
    def visit(self, v: NodeVisitor):
        v.visit_Number(self)

class Null(Literal):
    def __init__(self):
        Literal.__init__(self, None)
    
    def visit(self, v: NodeVisitor): v.visit_Null(self)

class Symbol(Expr):
    def __init__(self, name):
        self.name = name

    def visit(self, v: NodeVisitor): v.visit_String(self)