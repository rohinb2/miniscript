
from miniscript import *

if __name__ == '__main__':
    code = ''
    # todo: replace this with statement evaluator when its ready
    evaluator = ExpressionEvaluator(GlobalScope())
    while True:
        try:
            code = parse(input() + ';')
            if code:
                print(evaluator.visit(code[0]).string().value)
        except EOFError:
            break