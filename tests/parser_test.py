import unittest
from parser import *
from miniscript_ast import *


class TestExpressions(unittest.TestCase):
    def test_literals(self):
        self.assertEqual(parse('1'), [Number(1)])
        self.assertNotEqual(parse('2'), [Number(1)])
        self.assertEqual(parse('"";'), [String("")])
        self.assertEqual(parse('"31415";'), [String('31415')])
        self.assertEqual(parse('false;'), [Boolean(False)])
        self.assertEqual(parse('true;'), [Boolean(True)])
        self.assertEqual(parse('undefined;'), [Undefined()])
        self.assertEqual(parse('null;'), [Null()])
        self.assertEqual(parse('x;'), [Name('x')])

    def test_operator_simple(self):
        self.assertEqual(parse('1 + 1;'), [BinOp('+', Number(1), Number(1))])
        self.assertEqual(parse('"" + 3;'), [BinOp('+', String(''), Number(3))])
        self.assertEqual(parse('3 * 7;'), [BinOp('*', Number(3), Number(7))])
        self.assertEqual(parse('7 / 9;'), [BinOp('/', Number(7), Number(9))])
        self.assertEqual(parse('8 - 9;'), [BinOp('-', Number(8), Number(9))])
        self.assertEqual(parse('-9;'), [UnaryOp('-', Number(9))])
        self.assertEqual(parse('!false;'), [UnaryOp('!', Boolean(False))])

    def test_operator_precedence(self):
        self.assertEqual(parse('1 + 2 + 3;'),
                         [BinOp('+', BinOp('+', Number(1), Number(2)), Number(3))])
        self.assertEqual(parse('1 - 2 - 3;'),
                         [BinOp('-', BinOp('-', Number(1), Number(2)), Number(3))])
        self.assertEqual(
            parse('1 + 2 * 3 - 4;'),
            [BinOp('-', BinOp('+', Number(1), BinOp('*', Number(2), Number(3))), Number(4))])
        self.assertEqual(parse('1 - - 2;'), [BinOp('-', Number(1), UnaryOp('-', Number(2)))])
        self.assertEqual(
            parse('(1 + 2) / 3 * 7;'),
            [BinOp('*', BinOp('/', BinOp('+', Number(1), Number(2)), Number(3)), Number(7))])
        self.assertEqual(
            parse('!foo(1, b)[42];'),
            [UnaryOp('!', Index(Call(Name('foo'), [Number(1), Name('b')]), Number(42)))])

    def test_array(self):
        self.assertEqual(parse('[1,2,"asd", []];'),
                         [Array([Number(1), Number(2), String('asd'),
                                 Array()])])
        self.assertEqual(parse('[1,2,3][65];'),
                         [Index(Array([Number(1), Number(2), Number(3)]), Number(65))])
        self.assertEqual(
            parse('(1+1)["affe" - 4];'),
            [Index(BinOp('+', Number(1), Number(1)), BinOp('-', String('affe'), Number(4)))])

    def test_sequence(self):
        self.assertEqual(parse('1;2;3;'), [Number(1), Number(2), Number(3)])
        self.assertEqual(parse('1; 2; {31; 32;}'), [Number(1), Number(2), [Number(31), Number(32)]])
        self.assertEqual(parse(';{;;;};{};;;'), [[], []])

    def test_function(self):
        self.assertEqual(parse('function foo() {}'), [FunctionDef(Name('foo'), [], [])])
        self.assertEqual(parse('function foo(a, b) { return b; }'),
                         [FunctionDef(Name('foo'), [Name('a'), Name('b')], [Return(Name('b'))])])
        self.assertEqual(parse('function abc123(a) { a }'),
                         [FunctionDef(Name('abc123'), [Name('a')], [Name('a')])])

    def test_control(self):
        self.assertEqual(
            parse('if (1 + 1 == 2) 1; else 2;'),
            [If(BinOp('==', BinOp('+', Number(1), Number(1)), Number(2)), Number(1), Number(2))])
        self.assertEqual(parse('if (true) { print("true"); }'),
                         [If(Boolean(True), [Call(Name('print'), [String('true')])])])
        self.assertEqual(parse('while (false) { return true; }'),
                         [While(Boolean(False), [Return(Boolean(True))])])


    def test_declaration(self):
        self.assertEqual(parse('var x = 5;'), [VarDecl(Name('x'), Number(5))])

if __name__ == '__main__':
    unittest.main()