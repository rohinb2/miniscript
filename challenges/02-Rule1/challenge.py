import context
import miniscript as ms
import argparse
import random

class Level2Monitor:
    """Monitor that only enforces rule 1 from our report.
    """
    def __init__(self):
        self.pc_levels = [set()]  # type: List[Set(String)]

    @property
    def current_pc_level(self):
        return self.pc_levels[-1]

    def handle_BinOp(self, left_res, right_res):
        return self.pc_levels[-1].union(left_res.label.union(right_res.label))

    def handle_UnaryOp(self, res):
        return set()

    def handle_end_block(self):
        pass

    def handle_enter_block(self, res):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run the challenge')
    parser.add_argument('code', help='attacker code')
    args = parser.parse_args()
    with open(args.code) as f:
        source = f.read()
    r = random.randrange(1000000000)
    l = ms.Undefined()
    s = ms.Scope()
    s.declare('h', ms.TNumber(r, {'high'}))
    s.declare('l', ms.TUndefined())
    code = ms.compile(ms.parse(source))
    i = ms.Interpreter(code, s, monitor = Level2Monitor())
    i.run()
    result = s['l']
    if isinstance(result, ms.TNumber) and result.value == r and result.label == set():
        print('challenge passed')
    else:
        print('not quite. try again')
    pass