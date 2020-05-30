#!/usr/bin/env python
import context
import miniscript as ms
import random
from common import Challenge, default_main


class LightMonitor(ms.BaseMonitor):
    pass


class AstRestrictor(ms.NodeVisitor):
    def __init__(self, message='You are only allowed to use number literals, variables and arithmetic operators'):
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

    def visit_UnaryOp(self, tree: ms.UnaryOp):
        return self.visit(tree.expr)

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
            return True
        else:
            raise self.error(tree)


if __name__ == '__main__':
    default_main(
        Challenge(name='very basic challenge',
                  challenge=[('h', 'l', lambda: ms.TNumber(random.randrange(1000000000), label={'high'}))],
                  monitor=LightMonitor(),
                  restrictions=AstRestrictor().visit))
