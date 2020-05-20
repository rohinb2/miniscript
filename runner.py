
from miniscript import *

if __name__ == '__main__':
    code = ''
    # todo: replace this with statement evaluator when its ready
    lines = []
    while True:
        try:
            lines.append(input())
        except EOFError:
            break
    source = '\n'.join(lines)
    ast = parse(source)
    code = compile(ast)
    print(source)
    print(ast)
    print(code)
    interpreter = Interpreter(code, GlobalScope())
    interpreter.run(1000000)
    print(interpreter.scope)