
from miniscript import *

if __name__ == '__main__':
    code = ''
    evaluator = ExpressionEvaluator(GlobalScope())
    while True:
        try:
            code = parse(input() + ';')
            if code:
                print(evaluator.visit(code[0]).string().value)
        except EOFError:
            break