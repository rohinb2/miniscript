import context
import miniscript as ms
import argparse
import random

class LightMonitor:
    """Monitor that doesn't enforce any security policies.
    """
    def __init__(self):
        pass

    @property
    def current_pc_level(self):
        return set()

    def handle_BinOp(self, left_res, right_res):
        return set()

    def handle_UnaryOp(self, res):
        return set()

    def handle_end_block(self):
        pass

    def handle_enter_block(self, res):
        pass

class AstRestrictor(ms.NodeVisitor):
    def __init__(self, message = 'You are only allowed to use number literals, variables and arithmetic operators'):
        self.message = message
    
    def error(self, tree):
        return ms.InterpreterError(self.message)

    def visit_BinOp(self, tree: ms.BinOp):
        left = tree.left
        right = tree.right
        op = tree.op
        if op not in '+-*/%':
            raise self.error(tree)
        self.visit(left)
        self.visit(right)
        return True
    
    def visit_Name(self, tree):
        return True
    
    def visit_Number(self, tree: ms.Number):
        return True
    
    def visit_Assign(self, tree: ms.Assign):
        self.visit(tree.target)
        self.visit(tree.value)
        return True
    
    def generic_visit(self, tree):
        if isinstance(tree, list):
            for t in tree:
                self.visit(t)
        else:
            raise self.error(tree)

class Challenge:
    pass
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run the challenge')
    parser.add_argument('code', help='attacker code')
    args = parser.parse_args()
    with open(args.code) as f:
        source = f.read()
    r = random.randrange(1000000000)
    l = ms.Undefined()
    s = ms.Scope()
    s.declare('h', ms.TNumber(r, {'high'}))
    s.declare('l', ms.TUndefined())
    ast = ms.parse(source)
    AstRestrictor().visit(ast)
    code = ms.compile(ast)
    i = ms.Interpreter(code, s, monitor = LightMonitor())
    i.run()
    result = s['l']
    if isinstance(result, ms.TNumber) and result.value == r and result.label == set():
        print('challenge passed')
    else:
        print('not quite. try again')
    pass