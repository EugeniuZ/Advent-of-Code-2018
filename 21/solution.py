def read_input(filename):
    pass


def _run(stop_on_first=False):
    B = 0
    A = -1
    seen = set()
    lastB = B
    while B != A:
        if B and stop_on_first:
            break
        if B in seen:
            B = lastB
            break
        else:
            seen.add(B)
            lastB = B
        F = B | 0x10000
        B = 8595037  # (0x83265d)
        while True:
            D = F & 0xFF
            B = B + D
            B = B & 0xFFFFFF
            B = B * 65899
            B = B & 0xFFFFFF
            if 256 > F:
                break
            # while True:
            #     C = D + 1
            #     C = C << 8
            #     if C > F:
            #         C = 1
            #         F = D
            #         break
            #     else:
            #         D = D + 1
            F //= 256
    return B


def solution1(_):
    return _run(stop_on_first=True)


def solution2(_):
    return _run()
