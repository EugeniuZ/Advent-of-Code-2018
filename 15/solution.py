from collections import deque

ATTACK_POWER = 3
INIT_HIT_POINTS = 200

ELF = 'E'
GOBLIN = 'G'
OPEN_CAVERN = '.'
WALL = '#'

AREA = None


class EarlyGameOver(Exception):
    pass


class Player:
    def __init__(self, x, y, team, power, hit_points):
        self.x = x
        self.y = y
        self.team = team
        self.power = power
        self.hit_points = hit_points
        self._team_str = 'Elf' if team == 'E' else 'Goblin'

    def __eq__(self, other):
        return (
            self.x == other.x and
            self.y == other.y and
            self.team == other.team and
            self.power == other.power and
            self.hit_points == other.hit_points
        )

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

    def __repr__(self):
        return '%s(x=%d, y=%d, power=%d, hit_points=%d)' % (self._team_str, self.x, self.y, self.power, self.hit_points)

    def alive(self):
        return self.hit_points > 0

    def take_turn(self, players):
        enemies = [p for p in players if p.team != self.team and p.alive()]
        if not enemies:
            raise EarlyGameOver('%s win before round ends!' % self._team_str)
        if self.attack(enemies):
            return
        else:
            in_range_positions = self.range(enemies)
            if in_range_positions:
                self.move(in_range_positions)
                self.attack(enemies)

    def attack(self, enemies):
        # it is faster to check adjacent cells of self first
        # that to collect adjacent cells of enemies and compare to position of self
        targets = [
            (x, y) for x, y in (
                (self.x - 1, self.y),
                (self.x, self.y - 1),
                (self.x, self.y + 1),
                (self.x + 1, self.y)
            ) if x >= 0 and y >= 0 and AREA[x][y] == enemies[0].team
        ]
        if targets:
            targeted_enemies = [enemy for enemy in enemies if (enemy.x, enemy.y) in targets]
            selected_enemy = targeted_enemies[0]
            for te in targeted_enemies[1:]:
                if (te.hit_points, te.x, te.y) < (selected_enemy.hit_points, selected_enemy.x, selected_enemy.y):
                    selected_enemy = te
            selected_enemy.hit_points -= self.power
            if selected_enemy.hit_points <= 0:
                AREA[selected_enemy.x][selected_enemy.y] = OPEN_CAVERN
            return selected_enemy

    def range(self, enemies):
        result = []
        for enemy in enemies:
            result += [
                (x, y) for x, y in (
                    (enemy.x - 1, enemy.y),
                    (enemy.x, enemy.y - 1),
                    (enemy.x, enemy.y + 1),
                    (enemy.x + 1, enemy.y)
                ) if x >= 0 and y >= 0 and AREA[x][y] == OPEN_CAVERN
            ]
        # pre-optimize the search for shortest paths by searching first for path to closest units
        return sorted(result, key=lambda c: abs(self.x - c[0]) + abs(self.y - c[1]))

    def move(self, candidate_positions):
        next_move = None
        shortest_distance = float('inf')
        for x, y in candidate_positions:
            next_location, distance = _find_shortest_path(self.x, self.y, x, y, shortest_distance)
            if next_location and (distance < shortest_distance or next_location < next_move):
                next_move = next_location
                shortest_distance = distance
        if next_move:
            AREA[self.x][self.y] = OPEN_CAVERN
            self.x, self.y = next_move
            AREA[self.x][self.y] = self.team


def _find_shortest_path(ox, oy, tx, ty, max_distance):
    queue = deque([(tx, ty, 0, None)])
    seen = set()
    while queue:
        px, py, distance, parent = queue.popleft()
        if distance > max_distance or (px, py) in seen:
            continue
        seen.add((px, py))
        if (px, py) == (ox, oy):
            return parent, distance
        for x, y in [
            (px - 1, py),
            (px, py - 1),
            (px, py + 1),
            (px + 1, py)
        ]:
            if x >= 0 and y >= 0 and (AREA[x][y] == OPEN_CAVERN or (x, y) == (ox, oy)):
                queue.append((x, y, distance + 1, (px, py)))
    return None, None


def read_input(filename):
    with open(filename) as f:
        return f.read()


def _initialize_game(contents, elf_power):
    global AREA
    AREA = []
    players = []
    for row, line in enumerate(contents.splitlines()):
        line = line.strip()
        l = []
        for column, char in enumerate(line):
            if char in (GOBLIN, ELF):
                p = Player(row, column, char, ATTACK_POWER if char == GOBLIN else elf_power, INIT_HIT_POINTS)
                players.append(p)
            l.append(char)
        AREA.append(l)
    return players


def solution1(contents):
    score, team, winner_losses = _play_game(contents, ATTACK_POWER)
    return score


def solution2(contents):
    winning_team = GOBLIN
    winner_losses = None
    elf_power = ATTACK_POWER + 1
    while winning_team == GOBLIN or winner_losses:
        score, team, winner_losses = _play_game(contents, elf_power)
        print('%s wins with score %d (elf power = %d)' % (team, score, elf_power))
        winning_team = team
        elf_power += 1
    return score


def _play_game(contents, elf_power):
    players = _initialize_game(contents, elf_power)
    init_players = {GOBLIN: sum(1 for p in players if p.team == GOBLIN)}
    init_players[ELF] = len(players) - init_players[GOBLIN]
    rounds = 0
    try:
        while not _game_over(players):
            for player in sorted(players):
                if player.alive():
                    player.take_turn(players)
            players = sorted(p for p in players if p.alive())
            rounds += 1
    except EarlyGameOver as e:
        print(e)
    finally:
        players = sorted(p for p in players if p.alive())
    winner_team = players[0].team
    winning_team_loses = init_players[winner_team] - len(players)
    return rounds * sum(p.hit_points for p in players), winner_team, winning_team_loses


def _game_over(players):
    p0 = players[0]
    return all(p0.team == p.team for p in players[1:])


def test_read_input():
    players = _initialize_game("""#######
#E..G.#
#...#.#
#.G.#G#
#######""", ATTACK_POWER)
    assert [
               ['#', '#', '#', '#', '#', '#', '#'],
               ['#', 'E', '.', '.', 'G', '.', '#'],
               ['#', '.', '.', '.', '#', '.', '#'],
               ['#', '.', 'G', '.', '#', 'G', '#'],
               ['#', '#', '#', '#', '#', '#', '#', ]
           ] == AREA

    assert [
               Player(1, 1, ELF, ATTACK_POWER, INIT_HIT_POINTS),
               Player(1, 4, GOBLIN, ATTACK_POWER, INIT_HIT_POINTS),
               Player(3, 2, GOBLIN, ATTACK_POWER, INIT_HIT_POINTS),
               Player(3, 5, GOBLIN, ATTACK_POWER, INIT_HIT_POINTS)
           ] == players


def test_solution1():
    _test_sort()

    contents = """#######
#.G...#
#...EG#
#.#.#G#
#..G#E#
#.....#
#######"""
    result = solution1(contents)
    assert 47 * (200 + 131 + 59 + 200) == result, result

    contents = """#######
#G..#E#
#E#E.E#
#G.##.#
#...#E#
#...E.#
#######"""
    result = solution1(contents)
    assert 37 * 982 == result, result

    contents = """#######
#E..EG#
#.#G.E#
#E.##E#
#G..#.#
#..E#.#
#######"""
    result = solution1(contents)
    assert 46 * 859 == result, result

    contents = """#######
#E.G#.#
#.#G..#
#G.#.G#
#G..#.#
#...E.#
#######"""
    result = solution1(contents)
    assert 35 * 793 == result, result

    contents = """#######
#.E...#
#.#..G#
#.###.#
#E#G#G#
#...#G#
#######"""
    result = solution1(contents)
    assert 54 * 536 == result, result

    contents = """#########
#G......#
#.E.#...#
#..##..G#
#...##..#
#...#...#
#.G...G.#
#.....G.#
#########"""
    result = solution1(contents)
    assert 20 * 937 == result, result


def _test_sort():
    p1 = Player(1, 1, ELF, ATTACK_POWER, INIT_HIT_POINTS)
    p2 = Player(1, 4, GOBLIN, ATTACK_POWER, INIT_HIT_POINTS)
    p3 = Player(3, 2, GOBLIN, ATTACK_POWER, INIT_HIT_POINTS)
    p4 = Player(3, 5, GOBLIN, ATTACK_POWER, INIT_HIT_POINTS)

    players = [p3, p2, p4, p1]
    result = sorted(players)
    assert [p1, p2, p3, p4] == result, result
