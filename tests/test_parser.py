import pytest
import context
from miniscript import *


class TestExpressions:
    def test_literals(self):
        assert parse('1') == [Number(1)]
        assert parse('2') != [Number(1)]
        assert parse('"";') == [String("")]
        assert parse('"31415";') == [String('31415')]
        assert parse('false;') == [Boolean(False)]
        assert parse('true;') == [Boolean(True)]
        assert parse('undefined;') == [Undefined()]
        assert parse('null;') == [Null()]
        assert parse('x;') == [Name('x')]

    def test_operator_simple(self):
        assert parse('1 + 1;') == [BinOp('+', Number(1), Number(1))]
        assert parse('"" + 3;') == [BinOp('+', String(''), Number(3))]
        assert parse('3 * 7;') == [BinOp('*', Number(3), Number(7))]
        assert parse('7 / 9;') == [BinOp('/', Number(7), Number(9))]
        assert parse('8 - 9;') == [BinOp('-', Number(8), Number(9))]
        assert parse('-9;') == [UnaryOp('-', Number(9))]
        assert parse('!false;') == [UnaryOp('!', Boolean(False))]
        assert parse('7 <= 13') == [BinOp('<=', Number(7), Number(13))]
        assert parse('a >= b;') == [BinOp('>=', Name('a'), Name('b'))]

    def test_operator_precedence(self):
        assert parse('1 + 2 + 3;') == [BinOp('+', BinOp('+', Number(1), Number(2)), Number(3))]
        assert parse('1 - 2 - 3;') == [BinOp('-', BinOp('-', Number(1), Number(2)), Number(3))]
        assert parse('1 + 2 * 3 - 4;') == [
            BinOp('-', BinOp('+', Number(1), BinOp('*', Number(2), Number(3))), Number(4))
        ]
        assert parse('1 - - 2;'), [BinOp('-', Number(1), UnaryOp('-', Number(2)))]
        assert parse('(1 + 2) / 3 * 7;') == [
            BinOp('*', BinOp('/', BinOp('+', Number(1), Number(2)), Number(3)), Number(7))
        ]
        assert parse('!foo(1, b)[42];') == [
            UnaryOp('!', Index(Call(Name('foo'), [Number(1), Name('b')]), Number(42)))
        ]

    def test_array(self):
        assert parse('[1,2,"asd", []];') == [Array([Number(1), Number(2), String('asd'), Array()])]
        assert parse('[1,2,3][65];') == [
            Index(Array([Number(1), Number(2), Number(3)]), Number(65))
        ]
        assert parse('(1+1)["affe" - 4];') == [
            Index(BinOp('+', Number(1), Number(1)), BinOp('-', String('affe'), Number(4)))
        ]

    def test_sequence(self):
        assert parse('1;2;3;') == [Number(1), Number(2), Number(3)]
        assert parse('1; 2; {31; 32;}') == [Number(1), Number(2), [Number(31), Number(32)]]
        assert parse(';{;;;};{};;;') == [[], []]

    def test_function(self):
        assert parse('function foo() {}') == [FunctionDef(Name('foo'), [], [])]
        assert parse('function foo(a, b) { return b; }') == [
            FunctionDef(Name('foo'), [Name('a'), Name('b')], [Return(Name('b'))])
        ]
        assert parse('function abc123(a) { a }') == [
            FunctionDef(Name('abc123'), [Name('a')], [Name('a')])
        ]

    def test_control(self):
        assert parse('if (1 + 1 == 2) 1; else 2;') == [
            If(BinOp('==', BinOp('+', Number(1), Number(1)), Number(2)), Number(1), Number(2))
        ]
        assert parse('if (true) { print("true"); }') == [
            If(Boolean(True), [Call(Name('print'), [String('true')])])
        ]
        assert parse('while (false) { return true; }') == [
            While(Boolean(False), [Return(Boolean(True))])
        ]

    def test_declaration(self):
        #assert parse('var x = 5;') == [VarDecl(Name('x'), Number(5))]
        assert parse('var x ;') == [VarDecl(Name('x'))]
