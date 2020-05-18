from .miniscript_ast import *
from typing import Optional, Mapping, Sequence
import math


class InterpreterError(Exception):
    pass


class UnsupportedOperationError(InterpreterError):
    pass


class NotYetImplementedError(Exception):
    pass


class RefError(InterpreterError):
    pass


class Type:
    def string(self) -> str:
        raise UnsupportedOperationError('cannot convert to string')

    def number(self) -> 'Number':
        return Number(float('nan'))

    def call(self, args: Sequence['Type']) -> 'Type':
        raise UnsupportedOperationError('not a function')


class TUndefined(Type):
    def string(self):
        return 'undefined'


class TNull(Type):
    def string(self):
        return 'null'

    def number(self):
        return Number(0)


Code = Ast


class TFunction(Type):
    def __init__(self, name: str, code: Code):
        self.name = name
        self.code = code

    def string(self):
        return self.name or '<anonymous>'

    def call(self, args: Sequence[Type]):
        raise NotYetImplementedError()


class TNumber(Type):
    def __init__(self, value: float):
        self.value = value

    def number(self):
        return self

    def string(self):
        if math.isnan(self.value):
            return String('NaN')
        elif math.isinf(self.value):
            return String('Infinity' if self.value > 0 else '-Infinity')
        return String(str(self.value))


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


class Scope:
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

    def declare(name: str, value: Optional[Type] = Undefined):
        self.names

    def fresh_var(self):
        if not self.parent:
            self._vars += 1
            return self._vars
        else:
            return self.parent.fresh_var()


class GlobalScope(Scope):
    def __init__(self):
        super(GlobalScope).__init__(self, None)

    pass
