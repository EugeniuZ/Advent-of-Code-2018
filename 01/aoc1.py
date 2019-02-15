from itertools import cycle


def main():
    with open('aoc1.txt') as f:
        values = [int(line) for line in f]

    print('Answer 1: %d' % _solution1(values))
    print('Answer 1: %d' % _solution2(values))


def _solution1(values):
    return sum(values)


def _solution2(values):
    known_sums = set()
    s = 0
    for v in cycle(values):
        s += v
        if s in known_sums:
            return s
        else:
            known_sums.add(s)


if __name__ == '__main__':
    main()
