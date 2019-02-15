import re
import numpy as np

pat = re.compile('#(?P<cid>\d+) @ (?P<lx>\d+),(?P<ly>\d+): (?P<dx>\d+)x(?P<dy>\d+)')
N = 1000
cloth = np.zeros((N, N))

STATE = {}


def read_input(filename):
    claims = []
    with open(filename) as f:
        for line in f:
            m = re.match(pat, line)
            claim_id = int(m.group('cid'))
            lx = int(m.group('lx'))
            ly = int(m.group('ly'))
            dx = int(m.group('dx'))
            dy = int(m.group('dy'))
            claims.append((claim_id, lx, ly, lx + dx, ly + dy))
    return claims


def solution1(claims):
    global STATE
    overlap_ids = set()
    non_overlap_ids = set()
    for cid, lx, ly, rx, ry in claims:
        overlap = False
        for i in range(lx, rx):
            for j in range(ly, ry):
                if cloth[i][j] == 0:
                    cloth[i][j] = cid
                else:
                    overlap_ids.add(cid)
                    overlap_ids.add(cloth[i][j])
                    cloth[i][j] = -1
                    overlap = True
        if not overlap:
            non_overlap_ids.add(cid)
    c = 0
    STATE['non_overlap_ids'] = non_overlap_ids
    STATE['overlap_ids'] = overlap_ids
    for x in cloth.flat:
        if x == -1:
            c += 1
    return c


def solution2(claims):
    return STATE['non_overlap_ids'].difference(STATE['overlap_ids'])
