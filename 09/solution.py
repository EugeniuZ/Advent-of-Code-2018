import re

from blist import blist

from collections import defaultdict
from itertools import cycle


pat = re.compile('\d+')


def read_input(filename):
    with open(filename) as f:
        m = re.findall(pat, f.read())
        return {'nplayers': int(m[0]), 'nmarbles': int(m[1])}


def solution1(data):
    winners = _play_game(data['nplayers'], data['nmarbles'])
    return winners


def solution2(data):
    winners = _play_game(data['nplayers'], data['nmarbles'] * 100)
    return winners


def _play_game(n_players, n_marbles, magic_number=23):
    players = cycle(range(1, n_players + 1))
    scores = defaultdict(int)
    marbles = blist([0])
    current = 0
    for marble in range(1, n_marbles + 1):
        player = next(players)
        if marble % magic_number == 0:
            score, current = _make_special_move(marble, current, marbles)
            scores[player] += score
        else:
            current = _place_marble(marble, current, marbles)
    winners = sorted(scores, key=lambda x: -scores[x])
    print('Top 3 players: %s' % {player_id: scores[player_id] for player_id in winners[:3]})
    return scores[winners[0]]


def _make_special_move(marble, current, marbles):
    n = len(marbles)
    pos = (n + current - 7) % n
    mp = marbles[pos]
    del marbles[pos]
    return marble + mp, pos


def _place_marble(marble, current, marbles):
    n = len(marbles)
    c2 = (n + current + 1) % n + 1
    marbles.insert(c2, marble)
    return c2
