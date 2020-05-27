#!/usr/bin/env python
import context
import miniscript as ms
from miniscript.miniscript_ast import *
#from miniscript.interpreter import *
import argparse
import random
import copy

class Level4Monitor(ms.ArithmeticOpRule, ms.UnaryOperatorRule, ms.LiteralRule, ms.AssignRule, ms.BaseMonitor):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run the challenge')
    parser.add_argument('code', help='attacker code')
    args = parser.parse_args()
    with open(args.code) as f:
        source = f.read()
    r = random.randint(1, 1000000007)
    l = ms.Undefined()
    s = ms.GlobalScope()
    s.declare('h', ms.TNumber(r, {'high'}))
    s.declare('l', ms.TUndefined())
    ast = ms.parse(source)
    result = None
    try:
        #NoIfNodeVisitor().visit(ast)
        code = ms.compile(ast)
        i = ms.Interpreter(code, s, monitor = Level4Monitor())
        i.run()
        result = s['l']
        print(f'got l={str(result)} with label {result.label}')
        print(f'expected {r}')
    except ms.InterpreterError as e:
        print(e)
    if isinstance(result, ms.TNumber) and result.value == r and result.label == set():
        print('challenge passed')
    else:
        print('not quite. try again')
    pass
