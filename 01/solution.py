from itertools import cycle


def read_input(filename):
    with open(filename) as f:
        return [int(line) for line in f]


def solution1(values):
    return sum(values)


def solution2(values):
    known_sums = set()
    s = 0
    for v in cycle(values):
        s += v
        if s in known_sums:
            return s
        else:
            known_sums.add(s)
