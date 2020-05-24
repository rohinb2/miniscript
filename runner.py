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
        prev = None
        while True:
            try:
                l = input().strip()
                if prev == l.strip() == '':
                    break
                prev = l
                lines.append(l)
            except EOFError:
                break
    source = '\n'.join(lines)
    interpreter = make_interpreter(source)
    try:
        interpreter.run(1000000)
    except InterpreterError as err:
        print(err)
    print(interpreter.scope)