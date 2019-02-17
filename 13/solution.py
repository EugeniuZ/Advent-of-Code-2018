TOP = 1
RIGHT = 2
BOTTOM = 3
LEFT = 4
INTERSECTION = 5

INITIAL_ORIENTATION_TO_DIRECTION = {
    '^': TOP,
    'v': BOTTOM,
    '>': RIGHT,
    '<': LEFT
}

DRIVING_RULES = {
    TOP: {'|': TOP, '/': RIGHT, '\\': LEFT, '+': INTERSECTION},
    RIGHT: {'/': TOP, '\\': BOTTOM, '-': RIGHT, '+': INTERSECTION},
    BOTTOM: {'|': BOTTOM, '/': LEFT, '\\': RIGHT, '+': INTERSECTION},
    LEFT: {'/': BOTTOM, '\\': TOP, '-': LEFT, '+': INTERSECTION},
}

INTERSECTION_CHOICES = {
    TOP: (LEFT, TOP, RIGHT),
    RIGHT: (TOP, RIGHT, BOTTOM),
    BOTTOM: (RIGHT, BOTTOM, LEFT),
    LEFT: (BOTTOM, LEFT, TOP),
}


class Cart:
    def __init__(self, x, y, c):
        self.x = x
        self.y = y
        self.direction = INITIAL_ORIENTATION_TO_DIRECTION[c]
        self.intersection_choice = 0

    def move(self, road):
        if self.direction == TOP:
            self.y -= 1
        elif self.direction == BOTTOM:
            self.y += 1
        elif self.direction == LEFT:
            self.x -= 1
        elif self.direction == RIGHT:
            self.x += 1
        road_direction = road[self.y][self.x]
        direction = DRIVING_RULES[self.direction][road_direction]
        if direction == INTERSECTION:
            self.direction = INTERSECTION_CHOICES[self.direction][self.intersection_choice]
            self.intersection_choice = (self.intersection_choice + 1) % 3
        else:
            self.direction = direction

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __lt__(self, other):
        return (self.y, self.x) < (other.y, other.x)


def read_input(filename):
    road = []
    carts = []
    with open(filename) as f:
        y = 0
        for line in f.readlines():
            row = [c for c in line]
            for x, c in enumerate(row):
                if c in ('v', '^', '>', '<'):
                    carts.append(Cart(x, y, c))
                    row[x] = '-' if c in ('>', '<') else '|'
            road.append(row)
            y += 1
    return {'road': road, 'carts': carts}


def solution1(data):
    road, carts = data['road'], data['carts']
    first_car_crash_location = None
    crashed_carts = []
    while not crashed_carts:
        carts, crashed_carts = _move_carts(carts, road)
        if crashed_carts:
            first_car_crash_location = crashed_carts[0].x, crashed_carts[0].y
    data['carts'] = carts  # keep updated position for solution2
    return 'First crash at location %s' % (first_car_crash_location, )


def solution2(data):
    road, carts = data['road'], data['carts']
    while len(carts) > 1:
        carts, _ = _move_carts(carts, road)
    return 'Last cart is located at: (%d, %d)' % (carts[0].x, carts[0].y)


def _move_carts(carts, road):
    carts = sorted(carts)
    crashed_carts = []
    for i, c in enumerate(carts):
        c.move(road)
        for j, cc in enumerate(carts):
            if c == cc and i != j:
                crashed_carts.append(c)
                crashed_carts.append(cc)
    if crashed_carts:
        carts = [c for c in carts if c not in crashed_carts]
    return sorted(carts), crashed_carts


def test_solution1():
    carts = [Cart(4, 5, '^'), Cart(1, 2, '^'), Cart(22, 2, '^')]
    carts1 = sorted(carts)
    assert carts1[0] == carts[1]
    assert carts1[1] == carts[2]
    assert carts1[2] == carts[0]
