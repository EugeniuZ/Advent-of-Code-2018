import re

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.animation import FuncAnimation

pat = re.compile('\-?\d+')

x = y = vx = vy = None

h = 10**10
w = 10**10

t = None


def read_input(filename):
    stars = []
    with open(filename) as f:
        for line in f:
            m = re.findall(pat, line)
            x, y, vx, vy = int(m[0]), int(m[1]), int(m[2]), int(m[3])
            stars.append((x, y, vx, vy))
    return stars


def solution1(stars):
    global h, w
    x = np.array([i[0] for i in stars])
    y = np.array([i[1] for i in stars])
    vx = np.array([i[2] for i in stars])
    vy = np.array([i[3] for i in stars])

    s = 0
    while h > 2000 or w > 2000:
        x += vx
        y += vy
        h = max(x) - min(x)
        w = max(y) - min(y)
        s += 1

    fig, ax = plt.subplots()
    scat = ax.scatter(x, y, s=h/12)

    ani = FuncAnimation(fig, _update_plot, fargs=(x, y, vx, vy, ax, scat, s), interval=1)
    plt.show()
    return ''


def solution2(stars):
    return t[1]


def _update_plot(i, x, y, vx, vy, ax, scat, s):
    global h, w, t
    x += vx
    y += vy
    xmax = max(x)
    xmin = min(x)
    ymax = max(y)
    ymin = min(y)
    if h * w > (xmax - xmin) * (ymax - ymin):
        h = ymax - ymin
        mid = h / 2.0 + ymin
        w = xmax - xmin
        if h < 1000 and w < 1000:
            scat.set_offsets([(i, 2 * mid - j) for i, j in zip(x, y)])
            ax.set_xlim(xmin-0.1*(xmax-xmin), xmax+0.1*(xmax-xmin))
            ax.set_ylim((ymin-0.1*(ymax-ymin)), (ymax+0.1*(ymax-ymin)))
            scat.set_sizes(np.full(x.shape, 20))
        t = i, i + s + 2, h, w
        print(t)  # need to +2 because i = 0 is called 2 times (for init and for first update)
    return scat,
