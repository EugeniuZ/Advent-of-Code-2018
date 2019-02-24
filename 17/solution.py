import sys

CLAY = '#'
SAND = '.'
SOURCE = '+'
WATER = '~'
WET_SAND = '|'

TILE_SUPPORT = {CLAY, WATER}


def read_input(filename):
    contents = _get_contents(filename)
    return _build_ground(contents)


def solution1(data):
    source = data['source']
    grid = data['grid']  # modify in place to reuse the result in second solution
    sys.setrecursionlimit(len(grid) + len(grid[0]))
    try:
        _pour_water(source[0] + 1, source[1], grid)
    finally:
        with open('solution17.txt', 'w') as f:
            f.write(_make_printable_grid(grid))
    return sum(1 for row in grid for tile in row if tile in (WET_SAND, WATER))


def solution2(data):
    return sum(1 for row in data['grid'] for tile in row if tile == WATER)


def _get_contents(filename):
    with open(filename) as f:
        return f.read()


def _build_ground(contents):
    clay_x = []
    clay_y = []
    for line in contents.splitlines():
        for x, y in _get_points(line):
            clay_x.append(x)
            clay_y.append(y)
    x_min = min(clay_x)
    x_max = max(clay_x)
    y_min = min(clay_y)
    y_max = max(clay_y)
    n_columns = y_max - y_min + 1 + 2  # extra sand columns for water overflow
    grid = [[SAND] * n_columns for _ in range(x_min - 1, x_max + 1)]  # extra row for source
    source_y = 500 - y_min + 1
    grid[0][source_y] = SOURCE
    for x, y in zip(clay_x, clay_y):
        grid[x - x_min + 1][y - y_min + 1] = CLAY
    return {'grid': grid, 'source': (0, source_y)}


def _get_points(line):
    xr, yr = line.split(', ')
    xr, yr = xr[2:], yr[2:]
    if line.startswith('x='):  # flip coordinates
        xr, yr = yr, xr
    if '..' in xr and '..' not in yr:
        x1, x2 = xr.split('..')
        return ((x, int(yr)) for x in range(int(x1), int(x2) + 1))
    elif '..' in yr and '..' not in xr:
        y1, y2 = yr.split('..')
        return ((int(xr), y) for y in range(int(y1), int(y2) + 1))
    else:
        raise Exception('Unexpected input: %s' % line)


def _pour_water(x, y, grid):
    if x == len(grid):
        return
    tile = grid[x][y]
    if tile in TILE_SUPPORT:
        return
    if tile == SAND:
        grid[x][y] = WET_SAND
        _pour_water(x + 1, y, grid)
        if x == len(grid) - 1 or grid[x + 1][y] not in TILE_SUPPORT:
            return
        # spread left
        ly = y - 1
        l_hit = False
        while grid[x + 1][ly] in TILE_SUPPORT:
            if grid[x][ly] == CLAY:
                l_hit = True
                break
            else:
                assert grid[x][ly] not in TILE_SUPPORT
                grid[x][ly] = WET_SAND
                ly -= 1
        # spread right
        ry = y + 1
        r_hit = False
        while grid[x + 1][ry] in TILE_SUPPORT:
            if grid[x][ry] == CLAY:
                r_hit = True
                break
            else:
                assert grid[x][ry] not in TILE_SUPPORT
                grid[x][ry] = WET_SAND
                ry += 1
        if l_hit and r_hit:  # inside a clay pot
            for yy in range(ly + 1, ry):
                grid[x][yy] = WATER
        if not l_hit:
            _pour_water(x, ly, grid)
        if not r_hit:
            _pour_water(x, ry, grid)


def test_read_input():
    contents = """x=495, y=2..7
y=7, x=495..501
x=501, y=3..7
x=498, y=2..4
x=506, y=1..2
x=498, y=10..13
x=504, y=10..13
y=13, x=498..504"""

    lines = contents.splitlines()
    [(x, 495) for x in range(2, 8)] == list(_get_points(lines[0]))
    [(7, y) for y in range(495, 502)] == list(_get_points(lines[1]))

    data = _build_ground(contents)
    assert (0, 6) == data['source']
    result_grid = '\n' + _make_printable_grid(data['grid'])
    assert """
......+.......
............#.
.#..#.......#.
.#..#..#......
.#..#..#......
.#.....#......
.#.....#......
.#######......
..............
..............
....#.....#...
....#.....#...
....#.....#...
....#######...""" == result_grid, result_grid


def test_solution1():
    expected_result = """......+.......
......|.....#.
.#..#||||...#.
.#..#~~#|.....
.#..#~~#|.....
.#~~~~~#|.....
.#~~~~~#|.....
.#######|.....
........|.....
...|||||||||..
...|#~~~~~#|..
...|#~~~~~#|..
...|#~~~~~#|..
...|#######|.."""

    initial_configuration = """x=495, y=2..7
y=7, x=495..501
x=501, y=3..7
x=498, y=2..4
x=506, y=1..2
x=498, y=10..13
x=504, y=10..13
y=13, x=498..504"""

    data = _build_ground(initial_configuration)
    result = solution1(data)
    assert 57 == result, result
    actual_result = _make_printable_grid(data['grid'])
    assert expected_result == actual_result, '\n' + actual_result


def _make_printable_grid(grid):
    return '\n'.join(''.join(row) for row in grid)
