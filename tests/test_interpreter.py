import pytest
import context
from miniscript.interpreter import *

class TestCompiler:
    def test_compile(self):
        ast = [If(Boolean(True), [Assign(Name('x'), Number(5))], Assign(Name('y'), String('foo')))]
        assert compile(ast) == [ConditionalJump(Boolean(True), 3), Assign(Name('y'), String('foo')), Jump(2), Assign(Name('x'), Number(5))]

        ast2 = [Call(Name('print'), [Number(7)]), Assign(Name('x'), String('foo'))]
        assert compile(ast2) == ast2

        ast3 = [While(Boolean(True), Assign(Name('x'), String('foo')))]
        assert compile(ast3) == [Jump(2), Assign(Name('x'), String('foo')), ConditionalJump(Boolean(True), -1)]

class TestExpressions:
    def test_expression(self):
        e = ExpressionEvaluator(Scope())
        ast = BinOp('+', Number(1), Number(1))
        assert e.visit(ast) == TNumber(2)
        ast2 = BinOp('+', Number(1), String('1'))
        assert e.visit(ast2) == TString('11')
        ast3 = BinOp('-', Number(1), String('2'))
        assert e.visit(ast3) == TNumber(-1)
        ast4 = UnaryOp('!', Boolean(True))
        assert e.visit(ast4) == TBoolean(False)
        ast5 = UnaryOp('-', Number(1))
        assert e.visit(ast5) == TNumber(-1)

class TestInterpreter:
    def test_simple(self):
        s = Scope()
        s.declare('x')
        s['x'] = TNumber(5)
        ast = If(BinOp('<', Name('x'), Number(5)), Assign(Name('x'), Number(42)), Assign(Name('x'), Number(17)))
        interpreter = Interpreter(compile(ast), s)
        interpreter.run(100)
        assert s['x'] == TNumber(17)