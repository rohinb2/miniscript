import pytest
import context
from miniscript.interpreter import *


class TestCompiler:
    def test_compile(self):
        ast = [If(Boolean(True), [Assign(Name('x'), Number(5))], Assign(Name('y'), String('foo')))]
        assert compile(ast) == [
            ConditionalJump(Boolean(True), 3),
            Assign(Name('y'), String('foo')),
            Jump(2),
            Assign(Name('x'), Number(5)),
            EndBlock()
        ]

        ast2 = [Call(Name('print'), [Number(7)]), Assign(Name('x'), String('foo'))]
        assert compile(ast2) == ast2

        ast3 = [While(Boolean(True), Assign(Name('x'), String('foo')))]
        assert compile(ast3) == [
            Jump(3), Assign(Name('x'), String('foo')),EndBlock(),
            ConditionalJump(Boolean(True), -2), EndBlock()
        ]


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
        assert e.visit(parse('7 * 13')[0]) == TNumber(91)

    def test_comparison(self):
        e = ExpressionEvaluator(Scope())
        ast = BinOp('<', Number(5), Number(5))
        assert e.visit(ast) == TBoolean(False)
        assert e.visit(BinOp('<', Number(4), Number(5))) == TBoolean(True)

        assert e.visit(parse('7 < 13')[0]) == TBoolean(True)
        assert e.visit(parse('13 < 13')[0]) == TBoolean(False)

        assert e.visit(parse('7 <= 13')[0]) == TBoolean(True)
        assert e.visit(parse('13 <= 13')[0]) == TBoolean(True)

        assert e.visit(parse('7 > 13')[0]) == TBoolean(False)
        assert e.visit(parse('13 > 13')[0]) == TBoolean(False)

        assert e.visit(parse('7 >= 13')[0]) == TBoolean(False)
        assert e.visit(parse('13 >= 13')[0]) == TBoolean(True)

        assert e.visit(parse('13 == 13')[0]) == TBoolean(True)
        assert e.visit(parse('14 == 13')[0]) == TBoolean(False)
        assert e.visit(parse('"13" == "13"')[0]) == TBoolean(True)
        assert e.visit(parse('"abd" == "13"')[0]) == TBoolean(False)
        assert e.visit(parse('[1,2,3] == [1,2,3]')[0]) == TBoolean(True)
        assert e.visit(parse('"13" != 31')[0]) == TBoolean(True)

    def test_logical(self):
        e = ExpressionEvaluator(Scope())

        assert e.visit(parse('false || 0')[0]) == TNumber(0)
        assert e.visit(parse('14 || 7')[0]) == TNumber(14)
        assert e.visit(parse('14 && 7')[0]) == TNumber(7)
        assert e.visit(parse('"" || 3')[0]) == TNumber(3)

    def test_lookup(self):
        s = Scope()
        s.declare('x', TNumber(5))
        e = ExpressionEvaluator(s)
        assert e.visit(Name('x')) == s['x']


class TestInterpreter:
    def test_simple(self):
        s = Scope()
        s.declare('x', TNumber(5))
        ast = If(BinOp('<', Name('x'), Number(5)), Assign(Name('x'), Number(42)),
                 Assign(Name('x'), Number(17)))
        code = compile(ast)
        interpreter = Interpreter(code, s)
        interpreter.run(100)
        assert s['x'] == TNumber(17)

    def test_loop(self):
        s = Scope()
        s.declare('x', TNumber(10))
        code = compile(parse("""while (x) { x = x - 1 }"""))
        interpreter = Interpreter(code, s)
        interpreter.run(100)
        assert s['x'] == TNumber(0)