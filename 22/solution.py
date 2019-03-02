import heapq as h
import re
import sys

from functools import lru_cache

sys.setrecursionlimit(sys.getrecursionlimit() * 3)

C_EL = 20183
C_X = 48271
C_Y = 16807
TIME_ADVANCE = 1
TIME_TOOL_CHANGE = 7

REGION_ROCKY = 0
REGION_WET = 1
REGION_NARROW = 2

TOOL_NONE = 1
TOOL_TORCH = 2
TOOL_CLIMBING_GEAR = 4

OTHER_TOOLS = {
    TOOL_NONE: (TOOL_TORCH, TOOL_CLIMBING_GEAR),
    TOOL_TORCH: (TOOL_CLIMBING_GEAR, TOOL_NONE),
    TOOL_CLIMBING_GEAR: (TOOL_TORCH, TOOL_NONE)
}

FORBIDDEN_TOOLS = {
    REGION_ROCKY: TOOL_NONE,
    REGION_WET: TOOL_TORCH,
    REGION_NARROW: TOOL_CLIMBING_GEAR
}


def read_input(filename):
    with open(filename) as f:
        contents = f.read()
        depth, tx, ty = tuple(int(i) for i in re.findall('\d+', contents, flags=re.M))
    return {'depth': depth, 'tx': tx, 'ty': ty}


def solution1(data):
    depth, tx, ty = data['depth'], data['tx'], data['ty']
    risk_level = 0
    for i in range(tx + 1):
        for j in range(ty + 1):
            el = _erosion_level(i, j, tx, ty, depth) % 3
            risk_level += el
    return risk_level


def solution2(data):
    depth, tx, ty = data['depth'], data['tx'], data['ty']
    # compute a quick path moving only within the bounding box
    # optimal path should be at most equal to this
    min_path_time = _find_path_in_bounding_box(depth, tx, ty)
    # store traversal states, sorted by current path length
    pqueue = []
    # for traversed points and tools keep path len
    # Discard points with longer length that reach this point
    seen = {}
    h.heappush(pqueue, (0, 0, 0, TOOL_TORCH))
    while pqueue:
        path_time, x, y, tool = h.heappop(pqueue)
        if x == tx and y == ty:
            if tool != TOOL_TORCH:
                path_time += TIME_TOOL_CHANGE
                tool = TOOL_TORCH
            if path_time < min_path_time:
                min_path_time = path_time  # set min_path and continue search
                seen[x, y, tool] = path_time
                continue
        if path_time >= min_path_time or path_time + (abs(tx - x) + abs(ty - y)) * TIME_ADVANCE >= min_path_time:
            continue  # discard longer paths (also incomplete paths that theoretically can't be shorter)
        if (x, y, tool) in seen and seen[x, y, tool] <= path_time:
            continue  # discard longer or equal path to point with same tooling
        else:
            seen[x, y, tool] = path_time

        for dx, dy in ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)):
            if dx >= 0 and dy >= 0:
                d_zone_type = _erosion_level(dx, dy, tx, ty, depth) % 3
                forbidden_tool = FORBIDDEN_TOOLS[d_zone_type]
                currently_forbidden_tool = FORBIDDEN_TOOLS[_erosion_level(x, y, tx, ty, depth) % 3]
                if tool != forbidden_tool:
                    h.heappush(pqueue, (path_time + TIME_ADVANCE, dx, dy, tool))
                else:
                    for atool in OTHER_TOOLS[forbidden_tool]:
                        if atool == currently_forbidden_tool:
                            continue
                        dl = path_time + TIME_ADVANCE + TIME_TOOL_CHANGE
                        if (dx, dy, atool) not in seen or dl <= seen[dx, dy, atool]:
                            h.heappush(pqueue, (dl, dx, dy, atool))
    return min_path_time


def _find_path_in_bounding_box(depth, tx, ty):
    # longest path can't be longer than direct path
    # where we change tools after each move
    min_path_time = (tx + ty + 2) * (TIME_ADVANCE + TIME_TOOL_CHANGE)
    # store coordinate and cumulative path len
    pqueue = []
    # for traversed points and tools keep path time
    # Discard points with longer path time that reach this point
    seen = {}
    h.heappush(pqueue, (0, 0, 0, TOOL_TORCH))
    while pqueue:
        path_time, x, y, tool = h.heappop(pqueue)
        if x == tx and y == ty:
            if tool != TOOL_TORCH:
                path_time += TIME_TOOL_CHANGE
                tool = TOOL_TORCH
            if path_time < min_path_time:
                min_path_time = path_time  # set min_path and continue search
                seen[x, y, tool] = path_time
                continue
        if path_time >= min_path_time or path_time + (abs(tx - x) + abs(ty - y)) * TIME_ADVANCE >= min_path_time:
            continue  # discard longer paths (also incomplete paths that theoretically can't be shorter)
        if (x, y, tool) in seen:
            if seen[x, y, tool] <= path_time:
                continue  # discard longer path to point with same tooling
            else:
                seen[x, y, tool] = path_time
        else:
            seen[x, y, tool] = path_time

        for dx, dy in ((x + 1, y), (x, y + 1), (x - 1, y)):
            if tx >= dx >= 0 and ty >= dy >= 0:
                d_zone_type = _erosion_level(dx, dy, tx, ty, depth) % 3
                forbidden_tool = FORBIDDEN_TOOLS[d_zone_type]
                currently_forbidden_tool = FORBIDDEN_TOOLS[_erosion_level(x, y, tx, ty, depth) % 3]
                if tool != forbidden_tool:
                    h.heappush(pqueue, (path_time + TIME_ADVANCE, dx, dy, tool))
                else:
                    for atool in OTHER_TOOLS[forbidden_tool]:
                        if atool == currently_forbidden_tool:
                            continue
                        dl = path_time + TIME_ADVANCE + TIME_TOOL_CHANGE
                        if (dx, dy, atool) not in seen or dl <= seen[dx, dy, atool]:
                            h.heappush(pqueue, (dl, dx, dy, atool))
    return min_path_time


@lru_cache(maxsize=None)
def _erosion_level(x, y, tx, ty, depth):
    return (_geo_index(x, y, tx, ty, depth) + depth) % C_EL


def _geo_index(x, y, tx, ty, depth):
    if x == y == 0 or (x == tx and y == ty):
        return 0
    if y == 0:
        return x * C_Y
    if x == 0:
        return y * C_X
    else:
        return _erosion_level(x, y - 1, tx, ty, depth) * \
               _erosion_level(x - 1, y, tx, ty, depth)


def test_solution1():
    assert 0 == _geo_index(0, 0, 10, 10, 510)
    assert 0 == _geo_index(10, 10, 10, 10, 510)
    assert C_Y == _geo_index(1, 0, 10, 10, 510)
    assert C_X == _geo_index(0, 1, 10, 10, 510)

    assert 510 == _erosion_level(0, 0, 10, 10, 510)
    assert 17317 == _erosion_level(1, 0, 10, 10, 510)
    assert 8415 == _erosion_level(0, 1, 10, 10, 510)

    assert 145722555 == _geo_index(1, 1, 10, 10, 510)
    assert 1805 == _erosion_level(1, 1, 10, 10, 510)


def test2():
    ans = solution2({'depth': 510, 'tx': 10, 'ty': 10})
    assert 45 == ans, 'Incorrect answer: %d' % ans
