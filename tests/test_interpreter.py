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
            Jump(3),
            Assign(Name('x'), String('foo')),
            EndBlock(True),
            ConditionalJump(Boolean(True), -2, True),
            EndBlock()
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
        ast6 = BinOp('/', Number(4), Number(2))
        assert e.visit(ast6) == TNumber(2)

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

    def test_declarations(self):
        code = 'var x;\nx=3;function foo() {var x; x = 4; }\nfoo();'
        i = make_interpreter(code)
        i.run()
        assert i.scope['x'] == TNumber(3)

    def test_functions(self):
        s = Scope()
        code = compile(parse("function f(x) { y = 2 * x; x = x + 1; return x; };\nz = f(42);"))
        print(code)
        interpreter = Interpreter(code, s)
        interpreter.run(100)
        assert 'x' not in s
        assert s['y'] == TNumber(84)
        assert s['z'] == TNumber(43)

        code2 = compile(parse("function f(x) { y = 2 * x; x = x + 1; return x; };\nz = f(f(42));"))
        interpreter2 = Interpreter(code2, Scope())
        interpreter2.run(100)
        s = interpreter2.scope
        assert 'x' not in s
        assert s['y'] == TNumber(86)
        assert s['z'] == TNumber(44)

    def test_label(self):
        s = GlobalScope()
        code = compile(parse("x = label(5, 42); y = label(5, 43);"))
        interpreter = Interpreter(code, s)
        interpreter.run(100)
        assert s['x'] == s['y']

        s2 = GlobalScope()
        code2 = compile(parse("x = label(5, 42); y = label(6, 43); z = x + y;"))
        interpreter2 = Interpreter(code2, s2)
        interpreter2.run(100)
        assert s2['z'] == TNumber(11)

        s3 = GlobalScope()
        code3 = compile(parse("x = label(3, 100); y = 0; if(x < 5) {y = 100;}"))
        interpreter3 = Interpreter(code3, s3)
        try:
            interpreter3.run(100)
        except FlowControlError:
            print("Handled expected error")
        assert s3['y'] == TNumber(0)

        s4 = GlobalScope()
        code4 = compile(parse("x = label(1, 100); y = 0; while(x) {y = 1; x = 0;}"))
        interpreter4 = Interpreter(code4, s4)
        try:
            interpreter4.run(100)
        except FlowControlError:
            print("Handled expected error")
        assert s4['y'] == TNumber(0)
        assert s4['x'] == TNumber(1)
