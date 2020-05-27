import context
import miniscript as ms
from miniscript.miniscript_ast import *
#from miniscript.interpreter import *
import argparse
import random
import copy

class NoIfNodeVisitor(NodeVisitor):
    def visit_If(self, tree: If):
        raise IllegalStateError('If statements not allowed')

class Level4Monitor:
    """Monitor that enforces rule 1,3 and 4 from our report.
    """
    def __init__(self):
        self.pc_levels = [set()]  # type: List[Set(String)]

    @property
    def current_pc_level(self):
        return self.pc_levels[-1]

    def handle_BinOp(self, left_res, right_res):
        return self.pc_levels[-1].union(left_res.label.union(right_res.label))

    def handle_UnaryOp(self, res):
        return self.pc_levels[-1].union(res.label)

    def handle_literal(self, res):
        res.label = self.current_pc_level
        return res

    def handle_secure_assign(self, a: Assign, scope, evaluator):
        if self.current_pc_level != set():
            # Can't define a new variable in a secure block
            if a.target.name not in scope:
                raise IllegalStateError(f'cannot create variable within branch with security level {self.current_pc_level}')

            # Can't redefine a variable with too low security
            elif not self.current_pc_level.issubset(scope[a.target.name].label):
                raise IllegalStateError(f'cannot modify variable with label {scope[a.target.name].label} within branch with security level {self.current_pc_level}')
        result = evaluator.visit(a.value)

        # When assigning a value raise it to at least the security level of the current scope
        # However, simply reading the value from another variable does not mean that that variable's label needs to go up. So, make a copy. We want these to be primitives copied, not references.
        result = copy.deepcopy(result)
        result.label = result.label.union(self.current_pc_level)

        # todo: proper target lookup for assign (e.g. array indeices, etc)
        if isinstance(a.target, Name):
            scope[a.target.name] = result
        else:
            raise NotYetImplementedError(f'currently only assignment to name is supported')

    def handle_end_block(self):
        pass

    def handle_enter_block(self, res):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run the challenge')
    parser.add_argument('code', help='attacker code')
    args = parser.parse_args()
    with open(args.code) as f:
        source = f.read()
    r = random.choice([True, False])
    l = ms.Undefined()
    s = ms.Scope()
    s.declare('h', ms.TBoolean(r, {'high'}))
    s.declare('l', ms.TUndefined())
    code = ms.compile(ms.parse(source))
    i = ms.Interpreter(code, s, monitor = Level4Monitor())
    #try:
    i.run()
    #except:
    #    print('If statements not allowed')
    result = s['l']
    if isinstance(result, ms.TBoolean) and result.value == r and result.label == set():
        print('challenge passed')
    else:
        print('not quite. try again')
    pass
