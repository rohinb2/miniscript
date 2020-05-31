import miniscript as ms

from typing import Optional, Callable, List, Tuple, Sequence
import argparse


class Challenge:
    def __init__(self,
                 name,
                 challenge: Sequence[Tuple[str, str, Callable[[], ms.Type]]],
                 monitor: ms.BaseMonitor,
                 restrictions: Optional[Callable[[ms.Ast], bool]] = None,
                 setup: Optional[Callable[[ms.Scope], None]] = None,
                 check: Optional[Callable[[ms.Scope], bool]] = None,
                 nruns: int = 1):
        """Create the challenge to extract the sepcified variable values.
        :param name: Challenge name
        :param challenge: List of challenge tuples. Each tuple consist of the high and low variable
            names and a generator for the high value. The generator should also set the security label.
        :param monitor: flow control rules
        :param restrictions: Optional restrictions on the ast. Should return false 
            or raise an exception if the ast uses restricted elements
        :param setup: function that is called to initialize the global scope
        :param check: optional custom validator function that can be used instead 
            of the standard result validation. Should return true or false to indicate
            whether the challenge should pass.
        :param nruns: number of times to run the challenge before passing 
        """
        self.name = name
        self._setup = setup
        self.challenge = challenge
        self.monitor = monitor
        self.restrictions = restrictions
        if check:
            self.check = check
        self.nruns = nruns

    def setup(self) -> ms.Scope:
        s = ms.Scope()
        if self._setup:
            self._setup(s)
        return s

    def run(self, source):
        passed = True
        try:
            for i in range(self.nruns):
                ast = ms.parse(source)
                if not self.restrictions or self.restrictions(ast):
                    code = ms.compile(ast)
                    s = self.setup()
                    for h, l, g in self.challenge:
                        s.declare(l, ms.TUndefined())
                        s.declare(h, g())
                    interpreter = ms.Interpreter(code, s, self.monitor)
                    interpreter.run()
                    if not self.check(s):
                        passed = False
                else:
                    print('you used forbidden syntax elements')
                    passed = False
        except ms.InterpreterError as e:
            print(e)
            passed = False
        if passed:
            print('congratulations, you passed')
            return True
        else:
            print('not quite. try again')
            return False

    def check(self, s: ms.Scope):
        passed = True
        for h, l, _ in self.challenge:
            print(l, s[l], s[l].label)
            print(h, s[h], s[h].label)
            if type(s[l]) != type(s[h]) or s[l].value != s[h].value or s[l].label:
                passed = False
                break
        return passed

def default_main(challenge):
    parser = argparse.ArgumentParser(description=f'run {challenge.name}')
    parser.add_argument('code', help='attacker code')
    args = parser.parse_args()
    with open(args.code) as f:
        source = f.read()
    challenge.run(source)
