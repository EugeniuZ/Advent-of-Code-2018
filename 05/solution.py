import string


def read_input(filename):
    with open(filename) as f:
        return [c for c in f.read()]


def solution1(polymer):
    reduced_polymer = _reduce(list(polymer))
    return len(reduced_polymer)


def solution2(polymer):
    min_len = len(polymer)
    unit = None
    for uu in string.ascii_uppercase:
        polymer_with_unit_removed = ''.join(polymer).replace(uu, '').replace(uu.lower(), '')
        reduced_polymer = _reduce(list(polymer_with_unit_removed))
        r_len = len(reduced_polymer)
        print(
            'Removing problem polymer %s: Original: %d, after reaction: %d' % (
                uu, len(polymer_with_unit_removed), r_len
            )
        )
        if r_len < min_len:
            unit = uu
            min_len = r_len
    print('Maximal reduction obtained after removing unit %s: %d size' % (unit, min_len))
    return min_len


def _reduce(poly):
    left = 0
    N = len(poly)
    for right in range(1, N):
        if abs(ord(poly[left]) - ord(poly[right])) == 32:
            poly[left] = '0'
            poly[right] = '0'
            while left > 0 and poly[left] == '0':  # skip all previously removed units
                left -= 1
            if left == 0 and poly[left] == '0':  # all units were previously removed
                left = right
        else:
            left = right
    return [c for c in poly if c != '0']
