#!/usr/bin/env python
import context
import miniscript as ms
import random
from common import Challenge, default_main

class NoIfNodeVisitor(ms.NodeVisitor):
    def visit_If(self, tree: ms.If):
        raise ms.IllegalStateError('If statements not allowed')

class Level4Monitor(ms.ArithmeticOpRule, ms.UnaryOperatorRule, ms.LiteralRule, ms.AssignRule, ms.BaseMonitor):
    pass

if __name__ == '__main__':
    default_main(
        Challenge(name='extract boolean without using if',
                  challenge=[('h', 'l', lambda: ms.TBoolean(random.choice((True, False)), label={'high'}))],
                  monitor=Level4Monitor,
                  restrictions=NoIfNodeVisitor().visit,
                  nruns=8))
