import copy

from collections import defaultdict


OPEN = '.'
TREE = '|'
LUMBER = '#'


def read_input(filename):
    with open(filename) as f:
        return [
            [c for c in line]
            for line in f.read().splitlines()
        ]


def solution1(area):
    n = 10
    area = copy.deepcopy(area)
    for minute in range(1, n+1):
        _transform(area)
    return _compute(area)


def solution2(area):
    n = 1000000000
    area = copy.deepcopy(area)
    cache = defaultdict(list)
    REPEAT_FACTOR = 10
    last_n = []
    for minute in range(1, n+1):
        _transform(area)
        number = _compute(area)
        print('Minute: %d, %d, %s' % (minute, number, cache[number]))
        if cache[number]:
            last_n.append(number)
        else:
            last_n.clear()
        if len(last_n) == REPEAT_FACTOR:
            first_number_in_stable_sequence = last_n[0]
            minutes = cache[first_number_in_stable_sequence]
            print('Found first repeating iteration at minute %d' % minutes[0])
            cycle_size = minutes[1] - minutes[0]
            print('Cycle size %d' % cycle_size)
            result_minute = (n - minutes[0]) % cycle_size + minutes[0]
            print('Expected result to be found at minute: %d' % result_minute)
            for number, minutes in cache.items():
                if minutes[0] == result_minute:
                    return number
        else:
            cache[number].append(minute)
    return _compute(area)


def _transform(area):
    orig = copy.deepcopy(area)
    for x, line in enumerate(area):
        for y, c in enumerate(line):
            n_open, n_tree, n_lumber = _count(x, y, orig)
            if c == OPEN and n_tree >= 3:
                area[x][y] = TREE
            elif c == TREE and n_lumber >= 3:
                area[x][y] = LUMBER
            elif c == LUMBER and not (n_lumber and n_tree):
                area[x][y] = OPEN


def _count(x, y, orig):
    n_open = n_tree = n_lumber = 0
    for i in range(max(0, x - 1), min(x + 2, len(orig))):
        for j in range(max(0, y - 1), min(y + 2, len(orig[x]))):
            if i != x or j != y:
                n_open += int(orig[i][j] == OPEN)
                n_tree += int(orig[i][j] == TREE)
                n_lumber += int(orig[i][j] == LUMBER)
    return n_open, n_tree, n_lumber


def _compute(area):
    tree = 0
    lumber = 0
    for line in area:
        for c in line:
            tree += int(c == TREE)
            lumber += int(c == LUMBER)
    result = tree * lumber
    return result


def test_solution1():
    area = [
        ['.', '#', '|'],
        ['#', '|', '.'],
        ['|', '.', '#'],
    ]

    assert (0, 1, 2) == _count(0, 0, area)
    assert (2, 2, 1) == _count(0, 1, area)
    assert (1, 1, 1) == _count(0, 2, area)
    assert (2, 2, 1) == _count(1, 0, area)
    assert (3, 2, 3) == _count(1, 1, area)
    assert (1, 2, 2) == _count(1, 2, area)
    assert (1, 1, 1) == _count(2, 0, area)
    assert (1, 2, 2) == _count(2, 1, area)
    assert (2, 1, 0) == _count(2, 2, area)
