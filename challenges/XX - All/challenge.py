#!/usr/bin/env python
import context
import miniscript as ms
import random
from common import Challenge, default_main


def setup(s: ms.Scope):
    g = ms.GlobalScope()
    s['print'] = g['print']
    s['labelPrint'] = g['labelPrint']

#, ms.ReturnRule
class ChallengeMonitor(ms.BlockLoopReturnRule, ms.LiteralRule, ms.ArithmeticOpRule, ms.UnaryOperatorRule, ms.AssignRule, ms.BaseMonitor):
    pass

if __name__ == '__main__':
    default_main(
        Challenge(name='final challenge',
                  challenge=[('h', 'l', lambda: ms.TBoolean(random.randint(1, 1000000007), label={'high'}))],
                  monitor=ChallengeMonitor,
                  setup=setup))
