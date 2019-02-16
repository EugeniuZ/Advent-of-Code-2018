import numpy as np

SIZE = 300


def read_input(filename):
    with open(filename) as f:
        serial_number = int(f.read())
        grid = _power_grid(SIZE, serial_number)
        sat_grid = _compute_summed_area_table(grid)
        return sat_grid


def solution1(sat_grid):
    x, y, total_power = _solve(sat_grid, 3)
    return '(d=3): X=%d, Y=%d, power=%d' % (x, y, total_power)


def solution2(sat_grid):
    m_power = None
    m_x = m_y = m_d = None
    for k in range(1, SIZE + 1):
        x, y, total_power = _solve(sat_grid, k)
        if m_power is None or total_power > m_power:
            m_power = total_power
            m_x = x
            m_y = y
            m_d = k
        print('(d=%d): X=%d, Y=%d, power=%d' % (k, x, y, total_power))

    return '(d=%d): X=%d, Y=%d, power=%d' % (m_d, m_x, m_y, m_power)


def _power_grid(size, serial):
    grid = np.full((size, size), 0)
    for i in range(size):
        for j in range(size):
            grid[i][j] = _cell_power(i + 1, j + 1, serial)
    return grid


def _cell_power(x, y, serial):
    rack_id = x + 10
    pl = rack_id * y + serial
    pl *= rack_id
    pl //= 100
    pl %= 10
    pl -= 5
    return pl


def _compute_summed_area_table(grid):
    sat = np.full(grid.shape, 0)
    r, c = grid.shape

    for j in range(c):
        sat[0][j] = grid[0][j]

    for i in range(1, r):
        for j in range(c):
            sat[i][j] = sat[i-1][j] + grid[i][j]

    for i in range(0, r):
        for j in range(1, c):
            sat[i][j] += sat[i][j-1]

    return sat


def _solve(sat, d):
    assert d > 0
    r, c = sat.shape
    pmax = sat[d-1][d-1]
    pi = pj = 0

    for i in range(r - d + 1):
        for j in range(c - d + 1):
            ri = i + d - 1
            rj = j + d - 1
            D = sat[ri][rj]
            B = sat[ri - d][rj] if ri >= d else 0
            C = sat[ri][rj - d] if rj >= d else 0
            A = sat[ri - d][rj - d] if ri >= d and rj >= d else 0
            p = D - B - C + A
            if p > pmax:
                pi = i
                pj = j
                pmax = p
    return pi + 1, pj + 1, pmax


def test_solution1():
    assert 4 == _cell_power(3, 5, 8)
    assert -5 == _cell_power(122, 79, 57)
    assert 0 == _cell_power(217, 196, 39)
    assert 4 == _cell_power(101, 153, 71)

    a = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ])
    a_sat = _compute_summed_area_table(a)
    assert (np.array([
        [1,  3,  6],
        [5,  12, 21],
        [12, 27, 45]
    ]) == a_sat).all(), a_sat

    r = _solve(a_sat, 2)
    assert (2, 2, 28) == r, r
