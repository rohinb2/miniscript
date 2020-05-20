from .miniscript_ast import *
from .parser import parse

import math
from typing import Optional, Mapping, Sequence, TypeVar

T = TypeVar('T')


class InterpreterError(Exception):
    pass


class IllegalStateError(InterpreterError):
    pass


class UnsupportedOperationError(InterpreterError):
    pass


class NotYetImplementedError(Exception):
    pass


class RefError(InterpreterError):
    pass


class MaximumStepsReached(InterpreterError):
    pass


class Type:
    def string(self) -> 'TString':
        raise UnsupportedOperationError('cannot convert to string')

    def number(self) -> 'TNumber':
        return TNumber(float('nan'))

    def call(self, args: Sequence['Type']) -> 'Type':
        raise UnsupportedOperationError('not a function')

    def __eq__(self, other):
        return self is other

    def __repr__(self):
        return f'{type(self).__name__}()'

    def __str__(self):
        return self.string().value


class TUndefined(Type):
    def string(self):
        return TString('undefined')

    def __eq__(self, other):
        return type(self) == type(other)


class TNull(Type):
    def string(self) -> 'TString':
        return 'null'

    def number(self):
        return Number(0)

    def __eq__(self, other):
        return type(self) == type(other)


class TFunction(Type):
    def __init__(self, name: str, code: Sequence[Code]):
        self.name = name
        self.code = code

    def string(self):
        return self.name or '<anonymous>'

    def call(self, args: Sequence[Type]):
        raise NotYetImplementedError()

    def __repr__(self):
        return f'{type(self).__name__}({self.name}, {self.code})'


class TNumber(Type):
    def __init__(self, value: float):
        self.value = value

    def number(self):
        return self

    def string(self):
        if math.isnan(self.value):
            return TString('NaN')
        elif math.isinf(self.value):
            return TString('Infinity' if self.value > 0 else '-Infinity')
        return TString(str(self.value))

    def __eq__(self, other):
        if type(self) != type(other): return False
        return self.value == other.value

    def __repr__(self):
        return f'{type(self).__name__}({self.value})'


class TBoolean(TNumber):
    def __init__(self, value: bool):
        self.value = value

    def string(self):
        if self.value: return TString('true')
        else: return TString('false')

    def __repr__(self):
        return f'{type(self).__name__}({self.value})'


class TString(Type):
    def __init__(self, value):
        self.value = value

    def number(self):
        try:
            return Number(int(self.value))
        except ValueError as e:
            return super(self).number()

    def string(self):
        return self

    def __eq__(self, other):
        if type(self) != type(other): return False
        return self.value == other.value


class TArray(Type):
    def __init__(self, values: Sequence[Type]):
        self.values = values

    def number(self):
        if len(self.values) == 1:
            return self.values[0].number()
        else:
            return super().number()

    def string(self):
        if not self.values: return TString('')
        elif len(self.values == 1): return self.values[0].string()
        else:
            return f'[{", ".join(map(lambda x: x.string(), self.values))}]'

    def __eq__(self, other):
        return self.values == other.values


class Scope:
    """Scope for name resolution.
    If a name is not boud within a scope the lookup is delegated to the parent scope.
    """
    def __init__(self, parent: Optional['Scope'] = None):
        self.parent = parent
        self.names: Mapping[str, Type] = dict()
        self._vars = 0

    def __getitem__(self, key: str):
        if key in self.names: return self.names[key]
        elif self.parent: return self.parent[key]
        raise ReferenceError(f'name {key} is not defined')

    def __setitem__(self, key: str, val: Type, local: bool = False):
        if local or key in self.names or not self.parent:
            self.names[key] = val
        else:
            self.parent[key] = val

    def __contains__(self, key):
        return key in self.names

    def declare(self, name: str, value: Optional[Type] = Undefined):
        self.names[name] = value

    def fresh_var(self):
        if not self.parent:
            self._vars += 1
            return self._vars
        else:
            return self.parent.fresh_var()


class GlobalScope(Scope):
    def __init__(self):
        super().__init__(None)

    pass


class _LocalVarCollector(NodeVisitor):
    def __init__(self):
        self.locals = []

    def visit_FunctionDef(self, f: FunctionDef):
        visitor = type(self)()
        f.localvars = visitor.visit(f.body)

    def visit_VarDecl(self, declaration: VarDecl):
        self.locals.append(declaration.name.name)

    def visit(self, tree: Ast):
        super().visit(tree)
        return self.locals


def is_falsy(e: Expr):
    # yes, that's what this is called in javascript...
    return e in [
        TBoolean(False),
        TNumber(0),
        TNull(),
        TUndefined(),
        TNumber(float('nan')),
        TString('')
    ]


class ExpressionEvaluator(NodeVisitor):
    def __init__(self, scope: Scope):
        self.scope = scope

    def visit_BinOp(self, tree: BinOp):
        op, left, right = tree.op, tree.left, tree.right
        left_val = self.visit(left)
        if op in ['&&', '||']:
            # short circuitevaluation
            if op == '&&':
                if is_falsy(left_val):
                    return left_val
                else:
                    return self.visit(right)
            elif op == '||':
                if is_falsy(left_val):
                    return self.visit(right)
                else:
                    return left_val
        right_val = self.visit(right)
        if op == '+':
            # both are number: addition
            if (isinstance(left_val, TNumber) or isinstance(left_val, TBoolean)) \
                and (isinstance(right_val, TNumber) or isinstance(right_val, TBoolean)):
                return TNumber(left_val.value + right_val.value)
            # otherwise: string concatenation
            else:
                return TString(left_val.string().value + right_val.string().value)
        elif op == '-':
            return TNumber(left_val.number().value - right_val.number().value)
        elif op == '*':
            return TNumber(left_val.number().value * right_val.number().value)
        elif op == '/':
            # division has a few special cases that work differently in python
            right_num = right_val.number()
            left_num = left_val.number()
            if right_num == 0:
                if left_num == 0:
                    return TNumber(float('nan'))
                elif left_num > 0:
                    return TNumber(float('inf'))
                elif left_num < 0:
                    return TNumber(float(- 'inf'))
                else:
                    return TNumber(float('nan'))
        elif op == '==':
            return TBoolean(left_val == right_val)
        elif op == '!=':
            return TBoolean(left_val != right_val)
        elif op == '>=':
            return TBoolean(left_val.number().value >= right_val.number().value)
        elif op == '>':
            return TBoolean(left_val.number().value > right_val.number().value)
        elif op == '<':
            return TBoolean(left_val.number().value < right_val.number().value)
        elif op == '<=':
            return TBoolean(left_val.number().value <= right_val.number().value)
        else:
            raise UnsupportedOperationError(f'unknown operator "{op}"')

    def visit_UnaryOp(self, tree: UnaryOp):
        op = tree.op
        if op == '-':
            return TNumber(-self.visit(tree.expr).number().value)
        elif op == '!':
            return TBoolean(is_falsy(self.visit(tree.expr)))
        else:
            raise UnsupportedOperationError(f'unknown operator "{op}')

    def visit_Undefined(self, tree: Undefined):
        return TUndefined()

    def visit_Null(self, tree: Null):
        return TNull()

    def visit_String(self, tree: String):
        return TString(tree.value)

    def visit_Number(self, tree: Number):
        return TNumber(tree.value)

    def visit_Boolean(self, tree: Boolean):
        return TBoolean(tree.value)

    def visit_Array(self, tree: Array):
        return TArray([self.visit(e) for e in tree.values])

    def visit_Name(self, tree: Name):
        return self.scope[tree.name]

    def generic_visit(self, tree: Ast):
        raise UnsupportedOperationError(f'unexpected {tree}')


def flatten(l: Sequence[T]):
    l = l.copy()
    i = 0
    while i < len(l):
        while isinstance(l[i], list):
            if not l[i]:
                del l[i]
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return l


def compile(code: Ast):
    compiler = _CodeCompiler()
    return flatten(compiler.visit(code))


class _CodeCompiler(NodeVisitor):
    def visit_If(self, tree: If):
        then = self.visit(tree.then)
        els = self.visit(tree.els)
        print(then)
        print(els)
        # jump when condition is true -> else block comes first
        els_offset = len(els) + 2
        els.append(Jump(len(then) + 1))
        code = [ConditionalJump(tree.cond, els_offset)] + els + then
        return code

    def visit_While(self, tree: While):
        body_code = self.visit(tree.body)
        # jump to conditional in the end
        body_len = len(body_code) + 1
        # jump back all the way
        while_offset = -len(body_code)
        while_code = [Jump(body_len)] + body_code + [ConditionalJump(tree.cond, while_offset)]
        return while_code

    #TODO collect locals, etc.
    #def visit_FunctionDef

    def generic_visit(self, tree: Ast):
        if isinstance(tree, list):
            return list(map(self.visit, tree))
        elif isinstance(tree, Code):
            return [tree]
        else:
            raise UnsupportedOperationError(f'{type(tree).__name__} is not supported')


class Interpreter:
    def __init__(self, code: Sequence[Code], scope: Scope):
        self.code = code
        self.scope = scope
        self.pc = 0
        self.evaluator = ExpressionEvaluator(self.scope)

    def step(self):
        if 0 <= self.pc < len(self.code):
            instruction = self.code[self.pc]
            method = getattr(self, 'run_' + type(instruction).__name__, self.generic_run)
            self.pc += method(self.code[self.pc]) or 1
        else:
            raise IllegalStateError(f'illegal pc {self.pc}')

    def run(self, steps=None):
        if steps is None:
            while (self.pc < len(self.code)):
                self.step()
        else:
            for i in range(steps):
                if self.pc >= len(self.code):
                    break
                self.step()
            else:
                raise MaximumStepsReached(f'reached maximum of {steps} steps')

    def evaluate(self, expr):
        return self.evaluator.visit(expr)

    def run_Jump(self, g: Jump):
        return g.offset

    def run_ConditionalJump(self, j: ConditionalJump):
        result = self.evaluate(j.expr)
        if is_falsy(result):
            return 1
        else:
            return j.offset

    def run_Assign(self, a: Assign):
        result = self.evaluate(a.value)
        # todo: proper target lookup for assign (e.g. array indeices, etc)
        if isinstance(a.target, Name):
            self.scope[a.target.name] = result
        else:
            raise NotYetImplementedError(f'currently only assignment to name is supported')

    def generic_run(self, instruction):
        if isinstance(instruction, Expr):
            self.evaluate(instruction)
        else:
            raise UnsupportedOperationError(f'{instruction} not supported')
