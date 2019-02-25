from collections import namedtuple

Instruction = namedtuple('Instruction', ['name', 'in1', 'in2', 'out'])


class Program:
    def __init__(self, ip, instructions, n=6):
        self.regs = [0] * n
        self.ip = ip
        self.instructions = instructions
        self.size = len(instructions)

    def init(self, reg0=0):
        self.regs = [0] * len(self.regs)
        self.regs[0] = reg0

    def run(self):
        while self.regs[self.ip] < self.size:
            instruction = self.instructions[self.regs[self.ip]]
            instruction.name(self.regs, instruction)
            self.regs[self.ip] += 1


def read_input(filename):
    with open(filename) as f:
        ip, instructions = _parse_instructions(f.read())
        return Program(ip, instructions)


def solution1(program):
    program.run()
    return program.regs[0]


def solution2(program):
    """Naive solution is too slow
    # --------------------------
    # program.init(reg0=1)
    # program.run()
    # return program.regs[0]
    # --------------------------
    Had to disassemble the program to understand what it does

    Initial state:

    A = 0
    B = 3
    C = 1
    D = 10551408
    E = 1
    F = 10550400

    E = 1           seti 1 4 4
    C = 1           seti 1 1 2
    F = E * C       mulr 4 2 5
    F = F == D      eqrr 5 3 5
    if F: goto 7    addr 5 1 1
    goto 8          addi 1 1 1
    A += E          addr 4 0 0
    C += 1          addi 2 1 2
    F = C > D       gtrr 2 3 5
    if F: goto 12   addr 1 5 1
    goto 3          seti 2 4 1
    E += 1          addi 4 1 4
    F = E > D       gtrr 4 3 5
    if F: goto 16   addr 5 1 1
    goto 2          seti 1 1 1
    exit            mulr 1 1 1

    Then converted to an equivalent python program

    A = 0
    B = 3
    C = 1
    D = 10551408
    E = 1
    F = 10550400

    E = 1
    while True:
        C = 1
        while True:
            if E * C == D:
                A += E
                print('A=%d %s' % (A, [A, B, C, D, E, F]))
            C += 1
            if C > D:
                E += 1
                if E > D:
                    print('Answer 2: reg0=%d' % A)
                    return A
                break

    Finally after analyzing the output I understood the meaning of the program
    """
    D = 10551408
    return sum(i for i in range(1, D + 1) if D % i == 0)


def _parse_instructions(contents):
    lines = contents.splitlines()
    ipline, instruction_lines = lines[0], lines[1:]
    ip = int(ipline[3:])
    instructions = []
    for line in instruction_lines:
        name, in1, in2, out = line.split()
        in1, in2, out = int(in1), int(in2), int(out)
        instructions.append(Instruction(globals()[name], in1, in2, out))
    return ip, instructions


def addr(r, bi):
    r[bi.out] = r[bi.in1] + r[bi.in2]


def addi(r, bi):
    r[bi.out] = r[bi.in1] + bi.in2


def mulr(r, bi):
    r[bi.out] = r[bi.in1] * r[bi.in2]


def muli(r, bi):
    r[bi.out] = r[bi.in1] * bi.in2


def banr(r, bi):
    r[bi.out] = r[bi.in1] & r[bi.in2]


def bani(r, bi):
    r[bi.out] = r[bi.in1] & bi.in2


def borr(r, bi):
    r[bi.out] = r[bi.in1] | r[bi.in2]


def bori(r, bi):
    r[bi.out] = r[bi.in1] | bi.in2


def setr(r, bi):
    r[bi.out] = r[bi.in1]


def seti(r, bi):
    r[bi.out] = bi.in1


def gtir(r, bi):
    r[bi.out] = int(bi.in1 > r[bi.in2])


def gtri(r, bi):
    r[bi.out] = int(r[bi.in1] > bi.in2)


def gtrr(r, bi):
    r[bi.out] = int(r[bi.in1] > r[bi.in2])


def eqir(r, bi):
    r[bi.out] = int(bi.in1 == r[bi.in2])


def eqri(r, bi):
    r[bi.out] = int(r[bi.in1] == bi.in2)


def eqrr(r, bi):
    r[bi.out] = int(r[bi.in1] == r[bi.in2])


def test_solution1():
    text = """#ip 0
seti 5 0 1
seti 6 0 2
addi 0 1 0
addr 1 2 3
setr 1 0 0
seti 8 0 4
seti 9 0 5"""

    ip, instructions = _parse_instructions(text)
    program = Program(ip, instructions)
    program.run()
    assert [7, 5, 6, 0, 0, 9] == program.regs, program.regs
