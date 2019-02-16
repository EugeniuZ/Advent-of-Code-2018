from collections import defaultdict


def read_input(filename):
    points = []
    maxx = maxy = 0
    with open(filename) as f:
        for line in f:
            x, y = line.strip().split(',')
            x, y = int(x), int(y)
            if x > maxx:
                maxx = x
            if y > maxy:
                maxy = y
            points.append((x, y))
    return {'maxx': maxx, 'maxy': maxy, 'points': points}


def solution1(data):
    maxx, maxy, points = data['maxx'], data['maxy'], data['points']

    def minimal_distance(x, y, point_id, point, table):
        d = _manhattan((x, y), point)
        pd = table[x][y][0]
        if d < pd:  # distance -1 automatically ignored
            table[x][y] = d, point_id
        elif d == pd:
            table[x][y] = d, -1  # same distance for 2 or more points -> ignore

    max_dist = maxx + maxy
    distances = _compute_distances(
        points,
        maxx+1,
        maxy+1,
        minimal_distance,
        (max_dist, None)  # (maximal distance, unspecified point)
    )
    areas = _calculate_areas(distances)
    max_area = 0
    m_point = None
    for point, area in areas.items():
        if area > max_area:
            max_area = area
            m_point = point

    return '%d for point %s' % (max_area, m_point)


def solution2(data):
    maxx, maxy, points = data['maxx'], data['maxy'], data['points']
    max_cumulative_distance = 10000
    area = 0

    def cum_dist(x, y, point_id, point, table):
        table[x][y] += _manhattan((x, y), point)

    table = _compute_distances(points, maxx+1, maxy+1, cum_dist, 0)
    for row in table:
        for cumulative_distance in row:
            if cumulative_distance < max_cumulative_distance:
                area += 1
    return area


def _compute_distances(points, maxx, maxy, distance_function, init_value):
    distances = []
    for x in range(maxx):
        distances.append(list(init_value for _ in range(maxy)))
        for y in range(maxy):
            for point_id, point in enumerate(points):
                distance_function(x, y, point_id, point, distances)
    return distances


def _manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def _get_points_on_border(table):
    points_on_border = set()
    n_rows, n_columns = len(table), len(table[0])
    last_row, last_column = n_rows - 1, n_columns - 1
    for i in range(n_rows):
        point_first_row = table[i][0][1]
        points_on_border.add(point_first_row)
        point_last_row = table[i][last_column][1]
        points_on_border.add(point_last_row)
    for j in range(n_columns):
        point_first_column = table[0][j][1]
        points_on_border.add(point_first_column)
        point_last_column = table[last_row][j][1]
        points_on_border.add(point_last_column)
    return points_on_border


def _calculate_areas(distances):
    infinite_area_points = _get_points_on_border(distances)
    areas = defaultdict(int)
    for i in range(len(distances)):
        for j in range(len(distances[i])):
            _, point = distances[i][j]
            if point not in infinite_area_points:
                areas[point] += 1
    return areas
