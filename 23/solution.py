import math
import re

from copy import deepcopy

from collections import namedtuple, deque

LINE_PATT = re.compile('pos=<(?P<x>-?\d+),(?P<y>-?\d+),(?P<z>-?\d+)>, r=(?P<r>\d+)')

Bot = namedtuple('Bot', ('x', 'y', 'z', 'r'))


def read_input(filename):
    with open(filename) as f:
        contents = f.read()
        return _parse_contents(contents)


def _parse_contents(contents):
        result = []
        for line in contents.splitlines():
            m = re.match(LINE_PATT, line)
            result.append(
                Bot(
                    int(m.group('x')),
                    int(m.group('y')),
                    int(m.group('z')),
                    int(m.group('r'))
                )
            )
        return result


def solution1(nanobots):
    largest_radius_nanobot = max(nanobots, key=lambda bot: bot.r)
    largest_radius = largest_radius_nanobot.r
    return sum(
        1
        for bot in nanobots
        if _manhattan_distance(bot, largest_radius_nanobot) <= largest_radius
    )


def solution2(nanobots):
    """
    Solution outline: compute the region where most bots intersect directly.
    However due to the size of the grid it is not practical to do this on
    original coordinates. Instead we refine the search area by changing the
    granularity of the search space. The zoom factors are powers of 2.
    """

    bounds = _get_search_bounds(nanobots)
    print('Search for point in bounds: %s' % bounds)
    most_common_coordinate = _solve(bounds, nanobots)
    print(most_common_coordinate)
    return sum(abs(c) for c in most_common_coordinate)


def _manhattan_distance(bot1, bot2):
    return abs(bot1.x - bot2.x) + abs(bot1.y - bot2.y) + abs(bot1.z - bot2.z)


def _get_search_bounds(nanobots):
    bounds = _radius_bounds(nanobots[0])
    for bot in nanobots[1:]:
        for i, dimension_bounds in enumerate(_radius_bounds(bot)):
            bounds[i] = (
                min(bounds[i][0], dimension_bounds[0]),
                max(bounds[i][1], dimension_bounds[1])
            )
    return bounds


def _radius_bounds(bot):
    return [
        (bot.x - bot.r, bot.x + bot.r),
        (bot.y - bot.r, bot.y + bot.r),
        (bot.z - bot.r, bot.z + bot.r)
    ]


def _solve(bounds, bots):
    SCALE_INCREMENT_FACTOR = 2
    scale_factor = _find_starting_scale_factor(SCALE_INCREMENT_FACTOR, bounds)
    scaled_bounds = deepcopy(bounds)
    most_common_point = None
    while scale_factor >= 1:
        new_bounds = [(int(sb[0] / scale_factor), int(sb[1] / scale_factor) + 1) for sb in scaled_bounds]
        most_common_point = _find_coordinate(
            new_bounds,
            [
                Bot(round(bot.x / scale_factor), round(bot.y / scale_factor), round(bot.z / scale_factor), round(bot.r / scale_factor)) for bot in bots
            ]
        )
        scaled_bounds = [
            (
                math.floor(c - SCALE_INCREMENT_FACTOR) * scale_factor,
                math.floor(c + SCALE_INCREMENT_FACTOR) * scale_factor
            ) for c in most_common_point
        ]
        print('Search space narrowed to [%d]: %s' % (scale_factor, scaled_bounds))
        scale_factor /= SCALE_INCREMENT_FACTOR
    return most_common_point


def _find_starting_scale_factor(scale_factor_increment, bounds):
    b = min(abs(b[0]) for b in bounds)
    scale_factor = 1
    while b >= scale_factor_increment:
        scale_factor *= scale_factor_increment
        b /= scale_factor_increment
    return scale_factor


def _find_coordinate(bounds, bots):
    queue = deque([tuple(c[0] for c in bounds)])
    max_intersect = None
    n_bots = len(bots)
    results = []
    seen = set()
    while queue:
        point = queue.popleft()
        if point[0] > bounds[0][1] or point[1] > bounds[1][1] or point[2] > bounds[2][1]:
            continue
        if point in seen:
            continue
        else:
            seen.add(point)
        n_intersect = 0
        for b in bots:
            if _in_range(point, b):
                n_intersect += 1
        if n_intersect == n_bots:
            return [point]
        elif max_intersect is None or n_intersect >= max_intersect:
            if n_intersect == max_intersect:
                results.append(point)
            else:
                max_intersect = n_intersect
                results = [point]
        queue.append((point[0] + 1, point[1], point[2]))
        queue.append((point[0], point[1] + 1, point[2]))
        queue.append((point[0], point[1], point[2] + 1))
        queue.append((point[0] + 1, point[1] + 1, point[2]))
        queue.append((point[0] + 1, point[1], point[2] + 1))
        queue.append((point[0], point[1] + 1, point[2] + 1))
        queue.append((point[0] + 1, point[1] + 1, point[2] + 1))
    return results[0]


def _in_range(point, bot):
    return sum(abs(p - b) for p, b in zip(point, bot)) <= bot.r


def test():
    input = """pos=<0,0,0>, r=4
pos=<1,0,0>, r=1
pos=<4,0,0>, r=3
pos=<0,2,0>, r=1
pos=<0,5,0>, r=3
pos=<0,0,3>, r=1
pos=<1,1,1>, r=1
pos=<1,1,2>, r=1
pos=<1,3,1>, r=1"""
    nanobots = _parse_contents(input)
    result = solution1(nanobots)
    assert 7 == result, result


def test2():
    _test__get_search_bounds()
    _test_find_starting_scale_factor()

    result = solution2(
        [
            Bot(10, 12, 12, 2),
            Bot(12, 14, 12, 2),
            Bot(16, 12, 12, 4),
            Bot(14, 14, 14, 6),
            Bot(50, 50, 50, 200),
            Bot(10, 10, 10, 5),
        ]
    )
    assert 36 == result, result  # point 12,12,12


def _test__get_search_bounds():
    bot1 = Bot(1, 1, 1, 1,)  # x=( 0,  2), y=( 0,  2), z=( 0,  2)
    bot2 = Bot(1, 2, 3, 4)  # x=(-3,  5), y=(-2,  6), z=(-1,  7)
    bot3 = Bot(3, 3, 3, 2)  # x=( 1,  5), y=( 1,  5), z=( 1,  5)
    group = [bot1, bot2, bot3]
    result = _get_search_bounds(group)
    assert [(-3, 5), (-2, 6), (-1, 7)] == result, result


def _test_find_starting_scale_factor():
    bounds = [(-3, 5), (-2, 6), (-1, 7)]
    result = _find_starting_scale_factor(2, bounds)
    assert 1 == result

    bounds = [(-30, 50), (-20, 60), (-10, 70)]
    result = _find_starting_scale_factor(2, bounds)
    assert 8 == result

    bounds = [(-300, 500), (-200, 600), (-100, 700)]
    result = _find_starting_scale_factor(2, bounds)
    assert 64 == result
