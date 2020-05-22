import sys

from miniscript import *

if __name__ == '__main__':
    code = ''
    # todo: replace this with statement evaluator when its ready
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            lines = f.readlines()
    else:
        lines = []
        while True:
            try:
                lines.append(input())
            except EOFError:
                break
    source = '\n'.join(lines)
    ast = parse(source)
    code = compile(ast)
    #print(source)
    #print(ast)
    #print(code)
    interpreter = Interpreter(code, GlobalScope())
    try:
        interpreter.run(1000000)
    except InterpreterError as err:
        print(err)
    print(interpreter.scope)