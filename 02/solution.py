from collections import Counter
from functools import reduce


def read_input(filename):
    with open(filename) as f:
        return [line.strip() for line in f]


def solution1(box_ids):
    twos = 0
    threes = 0
    for box_id in box_ids:
        c = Counter(box_id)
        p = reduce(lambda x, y: x*y, c.values(), 1)
        twos += p % 2 == 0
        threes += p % 3 == 0
    return twos * threes


def solution2(box_ids):
    for i in range(0, len(box_ids) - 1):
        box_i = box_ids[i]
        for j in range(i + 1, len(box_ids)):
            box_j = box_ids[j]
            if diff_1(box_i, box_j):
                common = ''.join(ci for ci, cj in zip(box_i, box_j) if ci == cj)
                return 'common string: %s (box %d: %s and box %d: %s)' % (common, i, box_i, j, box_j)


def diff_1(bi, bj):
    c = 0
    for i, j in zip(bi, bj):
        if i != j:
            c += 1
        if c > 1:
            return False
    return c == 1
