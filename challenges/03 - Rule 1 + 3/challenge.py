#!/usr/bin/env python
import context
import miniscript as ms
import random
from common import Challenge, default_main

class Level3Monitor(ms.ArithmeticOpRule, ms.UnaryOperatorRule, ms.BaseMonitor):
    pass

if __name__ == '__main__':
    default_main(
        Challenge(name='extract boolean',
                  challenge=[('h', 'l', lambda: ms.TBoolean(random.choice((True, False)), label={'high'}))],
                  monitor=Level3Monitor(),
                  nruns=8))
