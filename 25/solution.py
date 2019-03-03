from functools import lru_cache


@lru_cache()
def _dist(p):
    return sum(abs(i) for i in p)


class Constellation:
    def __init__(self, points, dist=3):
        self.points = sorted(points, key=_dist)
        self.d = dist

    def __contains__(self, p):
        return any(_manhattan_distance(p, pc) <= self.d for pc in self.points)

    def __repr__(self):
        return 'Constellation(%s, dist=%d)' % (self.points, self.d)

    def __str__(self):
        return str(self.points)

    def __eq__(self, other):
        return self.d == other.d and self.points == other.points

    def __iter__(self):
        return iter(self.points)

    def add(self, p):
        d = _dist(p)
        for i, pc in enumerate(self.points):
            if _dist(pc) > d:
                self.points.insert(i, p)
                break
            elif p == pc:
                return
        else:
            self.points.append(p)

    def merge(self, c):
        for p in c:
            self.add(p)


def read_input(filename):
    with open(filename) as f:
        return _parse_contents(f.read())


def _parse_contents(content):
    points = [tuple(int(t) for t in line.split(',')) for line in content.splitlines()]
    return points


def _manhattan_distance(p1, p2):
    return sum(abs(i1 - i2) for i1, i2 in zip(p1, p2))


def solution1(points):
    points = sorted(points, key=_dist)
    constellations = []
    for point in points:
        constellations_for_point = []
        for i, constellation in enumerate(constellations):
            if point in constellation:
                constellation.add(point)
                constellations_for_point.append(i)
        if not constellations_for_point:
            constellation = Constellation([point])
            constellations.append(constellation)
        elif len(constellations_for_point) > 1:
            constellation = constellations[constellations_for_point[0]]
            constellations_for_point = constellations_for_point[1:]
            for mc in constellations_for_point:
                constellation.merge(constellations[mc])
            for i in sorted(constellations_for_point, reverse=True):
                constellations.remove(constellations[i])
    return len(constellations)


def solution2(_):
    return 'Reindeer\'s nose !'


def test_solution1():
    assert 2 == solution1([
        (0, 0, 0, 0),
        (3, 0, 0, 0),
        (0, 3, 0, 0),
        (0, 0, 3, 0),
        (0, 0, 0, 3),
        (0, 0, 0, 6),
        (9, 0, 0, 0),
        (12, 0, 0, 0),
    ])

    pts = _parse_contents("""-1,2,2,0
0,0,2,-2
0,0,0,-2
-1,2,0,0
-2,-2,-2,2
3,0,2,-1
-1,3,2,2
-1,0,-1,0
0,2,1,-2
3,0,0,0""")
    assert 4 == solution1(pts)

    pts = _parse_contents("""1,-1,0,1
2,0,-1,0
3,2,-1,0
0,0,3,1
0,0,-1,-1
2,3,-2,0
-2,2,0,0
2,-2,0,-1
1,-1,0,-1
3,2,0,2""")
    assert 3 == solution1(pts)

    pts = _parse_contents("""1,-1,-1,-2
-2,-2,0,1
0,2,1,3
-2,3,-2,1
0,2,3,-2
-1,-1,1,-2
0,-2,-1,0
-2,2,3,-1
1,2,2,0
-1,-2,0,-2""")
    assert 8 == solution1(pts)
