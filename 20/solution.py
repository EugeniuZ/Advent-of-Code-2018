from collections import defaultdict, deque
from copy import deepcopy
from enum import IntFlag


class DFlag(IntFlag):
    UP, DOWN, LEFT, RIGHT = 1, 2, 4, 8


DELTA = {'W': (-1, 0), 'E': (1, 0), 'S': (0, 1), 'N': (0, -1)}
DELTA_DIRECTION = {DFlag.LEFT: (-1, 0), DFlag.RIGHT: (1, 0), DFlag.DOWN: (0, 1), DFlag.UP: (0, -1)}
DIRECTION = {'W': DFlag.LEFT, 'E': DFlag.RIGHT, 'S': DFlag.DOWN, 'N': DFlag.UP}
OPPOSITE = {'W': 'E', 'E': 'W', 'S': 'N', 'N': 'S'}


def read_input(filename):
    labirinth = defaultdict(int)
    with open(filename) as f:
        regex = f.read().strip()
        assert '^$' == regex[0] + regex[-1]
        regex = regex[1:-1]
        for p in _extract_paths(regex):
            _make_board(p, labirinth, [(0, 0)])
        return labirinth


def solution1(labirinth):
    rooms = deque()
    rooms.append((0, 0, 0))
    seen = {(0, 0)}
    while rooms:
        x, y, distance = rooms.popleft()
        for direction in DFlag:
            doors = labirinth[x, y]
            dx, dy = DELTA_DIRECTION[direction]
            nx, ny = dx + x, dy + y
            if doors & direction and (nx, ny) not in seen:
                seen.add((nx, ny))
                rooms.append((dx + x, dy + y, distance + 1))
    return distance


def solution2(labirinth):
    MIN_DISTANCE = 1000
    n = 0
    rooms = deque()
    rooms.append((0, 0, 0))
    seen = {(0, 0)}
    while rooms:
        x, y, distance = rooms.popleft()
        if distance >= MIN_DISTANCE:
            n += 1
        for direction in DFlag:
            dx, dy = DELTA_DIRECTION[direction]
            doors = labirinth[x, y]
            nx, ny = dx + x, dy + y
            if doors & direction and (nx, ny) not in seen:
                seen.add((nx, ny))
                rooms.append((dx + x, dy + y, distance + 1))
    return n


def _make_board(regex, labirinth, rooms):
    if not regex:
        return
    i = 0
    while i < len(regex):
        c = regex[i]
        if c == '(':
            end = i + 1
            bracket_balance = 1
            while bracket_balance:
                if regex[end] == ')':
                    bracket_balance -= 1
                elif regex[end] == '(':
                    bracket_balance += 1
                end += 1
            paths = _extract_paths(regex[i+1:end-1])
            new_rooms = []
            for p in paths:
                path_rooms = deepcopy(rooms)
                _make_board(p, labirinth, path_rooms)
                new_rooms += path_rooms
            i = end
            rooms = new_rooms
            continue
        elif c in 'WESN':
            for j, room in enumerate(rooms):
                x, y = room
                labirinth[x, y] |= DIRECTION[c]
                dx, dy = DELTA[c]
                (x, y) = x + dx, y + dy
                labirinth[x, y] |= DIRECTION[OPPOSITE[c]]
                rooms[j] = x, y
        i += 1


def _extract_paths(regex):
    n = 0
    parts = []
    p = []
    for end, c in enumerate(regex):
        if c == '(':
            n += 1
            p.append(c)
        elif c == ')':
            n -= 1
            p.append(c)
        elif c == '|':
            if n:
                p.append(c)
            else:
                parts.append(''.join(p))
                p = []
        else:
            p.append(c)
    if p:
        parts.append(''.join(p))
    return parts


def test_read_input():
    result = _extract_paths('SEWN')
    assert ['SEWN'] == result, result
    result = _extract_paths('SEWN|NEE|SSN')
    assert ['SEWN', 'NEE', 'SSN'] == result, result
    result = _extract_paths('SEWN|(NEE|WES)|SSN')
    assert ['SEWN', '(NEE|WES)', 'SSN'] == result, result
    result = _extract_paths('SEWN|(NE(E|W)|WES)|SSN')
    assert ['SEWN', '(NE(E|W)|WES)', 'SSN'] == result, result

    result = defaultdict(int)
    _make_board('WES', result, [(0, 0)])
    assert {
               (0, 0): DFlag.LEFT | DFlag.DOWN,
               (-1, 0): DFlag.RIGHT,
               (0, 1): DFlag.UP
           } == result, result

    result = defaultdict(int)
    _make_board('W(N|W)E', result, [(0, 0)])
    assert {
               (0, 0): DFlag.LEFT,
               (-1, 0): DFlag.RIGHT | DFlag.UP | DFlag.LEFT,
               (-1, -1): DFlag.DOWN | DFlag.RIGHT,
               (-2, 0): DFlag.RIGHT,
               (0, -1): DFlag.LEFT
           } == result, result

    assert 3 == _test_longest('WNE')
    assert 10 == _test_longest('ENWWW(NEEE|SSE(EE|N))')
    assert 18 == _test_longest('ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN')
    assert 23 == _test_longest('ESSWWN(E|NNENN(EESS(WNSE|)SSS|WWWSSSSE(SW|NNNE)))')
    assert 23 == _test_longest('ESSWWN(E|NNENN(EESS(WNSE|)SSS|WWWSSSSE(SW|NNNE)))')
    assert 31 == _test_longest('WSSEESWWWNW(S|NENNEEEENN(ESSSSW(NWSW|SSEN)|WSWWN(E|WWS(E|SS))))')


def _test_longest(regex):
    labirinth = defaultdict(int)
    _make_board(regex, labirinth, [(0, 0)])
    return solution1(labirinth)
