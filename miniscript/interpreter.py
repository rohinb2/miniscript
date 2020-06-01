from .miniscript_ast import *
from .parser import parse

import math
import copy
from typing import Optional, MutableMapping as Mapping, Sequence, TypeVar, List, Callable

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


class ReturnStatement(InterpreterError):
    def __init__(self, value: 'Type', r: Return):
        super().__init__(f'unexpected return {r}')
        self.value = value


class Type:
    def __init__(self, label=set()):
        self.label = label

    def string(self) -> 'TString':
        raise UnsupportedOperationError('cannot convert to string')

    def number(self) -> 'TNumber':
        return TNumber(float('nan'))

    def call(self, args: List['Type']) -> 'Type':
        raise UnsupportedOperationError('not a function')

    @property
    def label(self):
        return getattr(self, '_label', set())

    @label.setter
    def label(self, l):
        self._label = l

    def __eq__(self, other):

        return self is other

    def __repr__(self):
        return f'{type(self).__name__}({self.label})'

    def __str__(self):
        return f'{self.string().value}'

    def lbl_str(self):
        return f'{str(self)}:{{{ ", ".join(self.label)}}}'


class TUndefined(Type):
    def string(self):
        return TString('undefined')

    def __eq__(self, other):
        return type(self) == type(other)


class TNull(Type):
    def string(self, label=set()) -> 'TString':
        return TString('null')

    def number(self):
        return Number(0)

    def __eq__(self, other):
        return type(self) == type(other)


class TFunction(Type):
    def __init__(self, name: str = '', label=set()):
        self.name = name

    def string(self):
        return TString(self.name or '<anonymous>')

    def call(self, args: List[Type]):
        raise NotYetImplementedError()

    def __repr__(self):
        return f'{type(self).__name__}({self.label})'


class TNumber(Type):
    def __init__(self, value: float, label=set()):
        self.value = value
        self.label = label

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
        return f'{type(self).__name__}({self.value}, {self.label})'


class TBoolean(TNumber):
    def __init__(self, value: bool, label=set()):
        self.value = value
        self.label = label

    def string(self):
        if self.value: return TString('true')
        else: return TString('false')

    def __repr__(self):
        return f'{type(self).__name__}({self.value}, {self.label})'


class TString(Type):
    def __init__(self, value: str, label=set()):
        self.value = value
        self.label = label

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

    def __repr__(self):
        return f'{type(self).__name__}({self.value}, {self.label})'


class TArray(Type):
    def __init__(self, values: Sequence[Type], label=set()):
        self.values = values
        self.label = label

    def number(self) -> TNumber:
        if len(self.values) == 1:
            return self.values[0].number()
        else:
            return super().number()

    def string(self) -> TString:
        if not self.values: return TString('')
        elif len(self.values) == 1: return self.values[0].string()
        else:
            return TString(f'[{", ".join(map(str, self.values))}]')

    def __eq__(self, other):
        return self.values == other.values

    def __repr__(self):
        return f'{type(self).__name__}({repr(self.values)}, {self.label})'


class BaseMonitor:
    def __init__(self):
        self.pc_levels = [set()]  # type: List[Set(String)]
        self.return_address = []

    @property
    def current_pc_level(self):
        return self.pc_levels[-1]

    def handle_BinOp(self, left_res: Type, right_res: Type):
        return set()

    def handle_UnaryOp(self, res: Type):
        return set()

    def handle_literal(self, res: Type):
        return res

    def handle_end_block(self):
        pass

    def handle_enter_block(self, res):
        pass

    def handle_secure_assign(self, a: Assign, scope, evaluator):
        return evaluator.visit(a.value)

    def handle_call(self, func: TFunction, args: List[Type]):
        self.return_address.append(len(self.pc_levels))

    def handle_return(self, val: Type):
        a = self.return_address.pop()
        while len(self.pc_levels) > a:
            self.pc_levels.pop()


class FlowControlError(InterpreterError):
    pass


class BlockRule:
    def handle_enter_block(self, res: Type):
        self.pc_levels.append(self.current_pc_level.union(res.label))

    def handle_end_block(self):
        self.pc_levels.pop()


class LiteralRule:
    def handle_literal(self, res: Type):
        res.label = self.current_pc_level
        return res


class ArithmeticOpRule:
    def handle_BinOp(self, left_res: Type, right_res: Type):
        return self.current_pc_level.union(left_res.label.union(right_res.label))


class UnaryOperatorRule:
    def handle_UnaryOp(self, res: Type):
        return self.current_pc_level.union(res.label)


class AssignRule:
    def handle_secure_assign(self, a: Assign, scope, evaluator):
        if self.current_pc_level != set():
            # Can't define a new variable in a secure block
            if a.target.name not in scope:
                raise FlowControlError(
                    f'cannot create variable within branch with security level {self.current_pc_level}')

            # Can't redefine a variable with too low security
            elif not self.current_pc_level.issubset(scope[a.target.name].label):
                raise FlowControlError(
                    f'cannot modify variable with label {scope[a.target.name].label} within branch with security level {self.current_pc_level}'
                )
        result = evaluator.visit(a.value)

        # When assigning a value raise it to at least the security level of the current scope
        # However, simply reading the value from another variable does not mean
        # that that variable's label needs to go up. So, make a copy.
        # We want these to be primitives copied, not references.
        result = copy.deepcopy(result)
        result.label = result.label.union(self.current_pc_level)
        return result


class ReturnRule:
    def handle_return(self, value: Type):
        a = self.return_address[-1]
        if not self.current_pc_level.issubset(self.pc_levels[a - 1]):
            raise FlowControlError('return statment in illegal context')
        BaseMonitor.handle_return(self, value)


class Monitor(BlockRule, LiteralRule, ArithmeticOpRule, UnaryOperatorRule, AssignRule, ReturnRule, BaseMonitor):
    pass


class BuiltinFunction(TFunction):
    def __init__(self, f: Callable[[List[Type]], Type], name: str = '', pass_monitor: bool = False):
        super().__init__()
        self.f = f
        self.pass_monitor = pass_monitor

    def string(self):
        return TString('[native code]')

    def call(self, args: List[Type], monitor: Monitor):
        if not self.pass_monitor:
            r = self.f(*args)
        else:
            r = self.f(monitor, *args)
        return r if r is not None else Undefined()


import traceback, sys


class UserFunction(TFunction):
    def __init__(self, code: List[Code], localvars: List[str], argnames: List[str],
                 parent_scope: 'Scope'):
        self.code = code
        self.localvars = localvars
        self.argnames = argnames
        self.parent_scope = parent_scope

    def call(self, args, monitor: Monitor):
        scope = Scope(self.parent_scope)
        for l in self.localvars:
            scope.declare(l, label = monitor.current_pc_level)
        for name, val in zip(self.argnames, args):
            scope.declare(name, val, label = monitor.current_pc_level)
        for name in self.argnames[len(args):]:
            scope.declare(name, label = monitor.current_pc_level)
        try:
            interpreter = Interpreter(self.code, scope, monitor)
            interpreter.run()
        except ReturnStatement as r:
            return r.value
        return interpreter.run()

    def string(self):
        return TString('function () { /* code */ }')


class Scope:
    """Scope for name resolution.
    If a name is not boud within a scope the lookup is delegated to the parent scope.
    """
    def __init__(self, parent: Optional['Scope'] = None, names: Optional[Mapping[str, Type]] = None):
        self.parent = parent
        self.names: Mapping[str, Type] = names or dict()
        self._vars = 0

    def __getitem__(self, key: str):
        if key in self.names: return self.names[key]
        elif self.parent: return self.parent[key]
        raise RefError(f'name {key} is not defined')

    def __setitem__(self, key: str, val: Type, local: bool = False):
        if local or key in self.names or not self.parent:
            self.names[key] = val
        else:
            self.parent[key] = val

    def __contains__(self, key):
        return key in self.names or (self.parent and key in self.parent)

    def declare(self, name: str, value: Type = TUndefined(), label = set()):
        value.label = value.label.union(label)
        self.names[name] = value

    def fresh_var(self):
        if not self.parent:
            self._vars += 1
            return self._vars
        else:
            return self.parent.fresh_var()

    def __repr__(self):
        return f'{type(self).__name__}({repr(self.parent)}, {self.names})'


class GlobalScope(Scope):
    def __init__(self):
        super().__init__(None)
        self.declare('print', BuiltinFunction(print))

        def label(val=Undefined(), *args: Sequence[Type]):
            val = copy.deepcopy(val)
            val.label = val.label.union(map(str, args))
            return val

        self.declare('label', BuiltinFunction(label))

        def print_label(m, *args):
            print(m.current_pc_level, *map(lambda v: v.lbl_str(), args))

        self.declare('labelPrint', BuiltinFunction(print_label, pass_monitor=True))


class _LocalVarCollector(NodeVisitor):
    def __init__(self):
        self.locals = []

    def visit_FunctionDef(self, f: FunctionDef):
        pass
        # visitor = type(self)()
        # f.localvars = visitor.visit(f.body)

    def visit_VarDecl(self, declaration: VarDecl):
        self.locals.append(declaration.name.name)

    def visit(self, tree: Ast):
        super().visit(tree)
        return self.locals


def collect_locals(ast: Ast) -> List[str]:
    collector = _LocalVarCollector()
    return collector.visit(ast)


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
    def __init__(self, scope: Scope, monitor: Optional[Monitor] = None):
        self.monitor = monitor or Monitor()
        self.scope = scope
        self.monitor = monitor

    def visit_BinOp(self, tree: BinOp) -> Type:
        op, left, right = tree.op, tree.left, tree.right
        left_val = self.visit(left)
        if op in ['&&', '||']:
            # short circuitevaluation
            if op == '&&':
                if is_falsy(left_val):
                    return left_val
                else:
                    self.monitor.handle_enter_block(left_val)
                    right_val = self.visit(right)
                    self.monitor.handle_end_block()
                    res_label = self.monitor.handle_BinOp(left_val, right_val)
                    right_val.label = res_label
                    return right_val
            elif op == '||':
                if is_falsy(left_val):
                    self.monitor.handle_enter_block(left_val)
                    right_val = self.visit(right)
                    self.monitor.handle_end_block()
                    res_label = self.monitor.handle_BinOp(left_val, right_val)
                    right_val.label = res_label
                    return right_val
                else:
                    return left_val
        right_val = self.visit(right)
        res_label = self.monitor.handle_BinOp(left_val, right_val)
        if op == '+':
            # both are number: addition
            if (isinstance(left_val, TNumber) or isinstance(left_val, TBoolean)) \
                and (isinstance(right_val, TNumber) or isinstance(right_val, TBoolean)):
                return TNumber(left_val.value + right_val.value, res_label)
            # otherwise: string concatenation
            else:
                return TString(left_val.string().value + right_val.string().value, res_label)
        elif op == '-':
            return TNumber(left_val.number().value - right_val.number().value, res_label)
        elif op == '*':
            return TNumber(left_val.number().value * right_val.number().value, res_label)
        elif op == '/':
            # division has a few special cases that work differently in python
            right_num = right_val.number()
            left_num = left_val.number()
            if right_num == 0:
                if left_num == 0:
                    return TNumber(float('nan'), res_label)
                elif left_num > 0:
                    return TNumber(float('inf'), res_label)
                elif left_num < 0:
                    return TNumber(-float('inf'), res_label)
                else:
                    return TNumber(float('nan'), res_label)
            return TNumber(left_val.number().value / right_val.number().value, res_label)
        elif op == '%':
            return TNumber(left_val.number().value % right_val.number().value, res_label)
        elif op == '==':
            return TBoolean(left_val == right_val, res_label)
        elif op == '!=':
            return TBoolean(left_val != right_val, res_label)
        elif op == '>=':
            return TBoolean(left_val.number().value >= right_val.number().value, res_label)
        elif op == '>':
            return TBoolean(left_val.number().value > right_val.number().value, res_label)
        elif op == '<':
            return TBoolean(left_val.number().value < right_val.number().value, res_label)
        elif op == '<=':
            return TBoolean(left_val.number().value <= right_val.number().value, res_label)
        raise UnsupportedOperationError(f'unknown operator "{op}"')

    def visit_UnaryOp(self, tree: UnaryOp) -> Type:
        op = tree.op
        res = self.visit(tree.expr)
        res_label = self.monitor.handle_UnaryOp(res)
        if op == '-':
            return TNumber(-res.number().value, res_label)
        elif op == '!':
            return TBoolean(is_falsy(res), res_label)
        else:
            raise UnsupportedOperationError(f'unknown operator "{op}')

    def visit_Undefined(self, tree: Undefined) -> Type:
        return self.monitor.handle_literal(TUndefined())

    def visit_Null(self, tree: Null) -> Type:
        return self.monitor.handle_literal(TNull())

    def visit_String(self, tree: String) -> Type:
        return self.monitor.handle_literal(TString(tree.value))

    def visit_Number(self, tree: Number) -> Type:
        return self.monitor.handle_literal(TNumber(tree.value))

    def visit_Boolean(self, tree: Boolean) -> Type:
        return self.monitor.handle_literal(TBoolean(tree.value))

    def visit_Array(self, tree: Array) -> Type:
        return self.monitor.handle_literal(TArray([self.visit(e) for e in tree.values]))

    def visit_Name(self, tree: Name) -> Type:
        return self.scope[tree.name]

    def visit_Call(self, tree: Call) -> Type:
        func = self.visit(tree.func)
        args = list(map(self.visit, tree.args))
        self.monitor.handle_call(func, args)
        return func.call(args, self.monitor)

    def visit_FunctionDef(self, tree: FunctionDef) -> Type:
        localvars = collect_locals(tree.body)
        code = compile(tree.body)
        f = UserFunction(code, localvars, list(tree.args), self.scope)
        if tree.name:
            f.name = tree.name
            self.scope[tree.name] = f
        return f

    def generic_visit(self, tree: Ast) -> Type:
        raise UnsupportedOperationError(f'unexpected {tree}')


def flatten(l):
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
        flatten(then)
        els = self.visit(tree.els) if tree.els else []
        flatten(els)
        # jump when condition is true -> else block comes first
        els_offset = len(els) + 2
        els.append(Jump(len(then) + 1))
        code: List[Code] = [ConditionalJump(tree.cond, els_offset)]
        code.append(els)
        code.append(then)
        code.append(EndBlock())
        return code

    def visit_While(self, tree: While):
        body_code = self.visit(tree.body)
        body_code.append(EndBlock())
        flatten(body_code)
        # jump to conditional in the end
        body_len = len(body_code) + 1
        # jump back all the way
        while_offset = -len(body_code)
        while_code = [Jump(body_len)] + body_code + [ConditionalJump(tree.cond, while_offset), EndBlock()]
        return while_code

    #TODO: collect locals, etc.
    #def visit_FunctionDef

    def generic_visit(self, tree: Ast):
        if isinstance(tree, list):
            return list(map(self.visit, tree))
        elif isinstance(tree, Code):
            return [tree]
        else:
            raise UnsupportedOperationError(f'{type(tree).__name__} is not supported')


class Interpreter:
    def __init__(self, code: Sequence[Code], scope: Scope, monitor: Optional[Monitor] = None):
        self.code = code
        self.scope = scope
        self.pc = 0
        self.monitor = monitor or Monitor()
        self.evaluator = ExpressionEvaluator(self.scope, self.monitor)
        self.return_value = None

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
        self.monitor.handle_enter_block(result)
        if is_falsy(result):
            return 1
        else:
            return j.offset

    def run_Assign(self, a: Assign):
        result = self.monitor.handle_secure_assign(a, self.scope, self.evaluator)
        # todo: proper target lookup for assign (e.g. array indeices, etc)
        if isinstance(a.target, Name):
            self.scope[a.target.name] = result
        else:
            raise NotYetImplementedError(f'currently only assignment to name is supported')

    def run_Return(self, r: Return):
        value = self.evaluate(r.expr)
        self.monitor.handle_return(value)
        raise ReturnStatement(value, r)

    def run_EndBlock(self, eb: EndBlock):
        self.monitor.handle_end_block()

    def run_VarDecl(self, v: VarDecl):
        if v.value:
            self.run_Assign(Assign(v.name, v.value))

    def generic_run(self, instruction):
        if isinstance(instruction, Expr):
            self.evaluate(instruction)
        else:
            raise UnsupportedOperationError(f'{instruction} not supported')


def make_interpreter(source: str):
    ast = parse(source)
    globalvars = collect_locals(ast)
    code = compile(ast)
    scope = GlobalScope()
    monitor = Monitor()
    for var in globalvars:
        scope.declare(var)
    return Interpreter(code, scope, monitor)
