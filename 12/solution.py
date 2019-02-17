import copy
import re

garden_pattern = '(\.|#)+'


def read_input(filename):
    rules = {}
    with open(filename) as f:
        n_left, garden, n_right = _read_garden_state(f.readline())
        f.readline()
        for rule in f.readlines():
            left, right = _to_rule(rule)
            if right == '#':
                rules[left] = right
    return {'rules': rules, 'n_left': n_left, 'garden': garden, 'n_right': n_right}


def solution1(data):
    (
        rules,
        n_left,
        garden,
        n_right
    ) = data['rules'], data['n_left'], data['garden'], data['n_right']
    return _solve(n_left, garden, n_right, rules, 1000)


def solution2(data):
    (
        rules,
        n_left,
        garden,
        n_right
    ) = data['rules'], data['n_left'], data['garden'], data['n_right']
    return _solve(n_left, garden, n_right, rules, 50000000000)


def _solve(n_left, garden, n_right, rules, generations):
    prev_s = None
    prev_diff = None
    for i in range(generations):
        s = _sum_pot_ids_with_plants(garden, n_left)
        diff = s - prev_s if prev_s is not None else None
        # print('generation=%d: %d, diff=%s' % (i, s, diff))
        if diff is not None and prev_diff == diff:
            print('Found repeating pattern at generation %d !' % i)
            result = (generations - i) * diff + s  # speed-up result computation for remaining generations
            return 'generations=(%d): %d' % (generations, result)
        prev_s = s
        prev_diff = diff
        n_left, garden, n_right = _grow_garden(n_left, garden, n_right, rules)

    return 'generations=(%d): %d' % (generations, _sum_pot_ids_with_plants(garden, n_left))


def _read_garden_state(line):
    m = re.search(garden_pattern, line)
    return 5, ['.'] * 5 + [c for c in m.group()] + ['.'] * 5, 5


def _to_rule(line):
    tokens = line.split('=>')
    left = tokens[0].strip()
    right = tokens[1].strip()
    return tuple(c for c in left), right


def _sum_pot_ids_with_plants(garden, n_left):
    ids = [pot_id for pot_id, pot in enumerate(garden, start=-n_left) if pot == '#']
    return sum(ids)


def _grow_garden(n_left, garden, n_right, rules):
    garden = _apply_rules(garden, rules)
    return _adjust_extremes(n_left, garden, n_right)


def _apply_rules(garden, rules):
    n = len(garden) - 4
    new_garden = copy.deepcopy(garden)
    for i in range(n):
        pot_5 = tuple(garden[i:i+5])
        if pot_5 in rules:
            new_garden[i+2] = rules[pot_5]
        else:
            new_garden[i+2] = '.'
    return new_garden


def _adjust_extremes(n_left, garden, n_right):
    while garden[0:5] != ['.', '.', '.', '.', '.']:
        garden.insert(0, '.')
        n_left += 1

    while garden[-5:] != ['.', '.', '.', '.', '.']:
        garden.append('.')
        n_right += 1

    return n_left, garden, n_right


def test_read_input():
    l, g, r = _read_garden_state('##..##')
    assert (5, '.....##..##.....', 5) == (l, ''.join(g), r)

    assert (('.', '#', '#', '.', '.'), '.') == _to_rule('.##.. => .')
    assert (('.', '#', '#', '.', '.'), '#') == _to_rule('.##.. => #')
    assert (('.', '#', '.', '.', '.'), '#') == _to_rule('.#... => #')
    assert (('.', '#', '.', '.', '.'), '.') == _to_rule('.#... => .')


def test_solution1():
    input_garden = [c for c in '.....#.#.....']
    expected_garden = [c for c in '......##.....']
    rules = {
        ('.', '#', '.', '#', '.'): '#',
        ('#', '.', '#', '.', '.'): '#'
    }

    assert expected_garden == _apply_rules(input_garden, rules)

    # test from problem description
    garden = '...#..#.#..##......###...###...........'
    line_rules = '''...## => #
..#.. => #
.#... => #
.#.#. => #
.#.## => #
.##.. => #
.#### => #
#.#.# => #
#.### => #
##.#. => #
##.## => #
###.. => #
###.# => #
####. => #'''
    rules = {}
    for line in line_rules.splitlines():
        left, right = _to_rule(line)
        rules[left] = right
    garden = [c for c in garden]
    new_garden = _apply_rules(garden, rules)
    expected_garden = '...#...#....#.....#..#..#..#...........'
    assert expected_garden == ''.join(new_garden)
