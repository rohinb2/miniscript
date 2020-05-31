#!/usr/bin/env python
import context
import miniscript as ms
import random
import copy
from common import Challenge, default_main


class Level4Monitor(ms.ArithmeticOpRule, ms.UnaryOperatorRule, ms.LiteralRule, ms.AssignRule, ms.BaseMonitor):
    pass


def setup(s: ms.Scope):
    g = ms.GlobalScope()
    s['print'] = g['print']


if __name__ == '__main__':
    default_main(
        Challenge(name='extract boolean without using if',
                  challenge=[('h', 'l', lambda: ms.TNumber(random.randint(1, 1000000007), label={'high'}))],
                  monitor=Level4Monitor(),
                  setup=setup,
                  nruns=8))
