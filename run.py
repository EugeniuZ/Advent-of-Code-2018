import importlib
import sys
import time


def main():
    day = sys.argv[1]
    module = importlib.import_module('%s.solution' % day)
    if hasattr(module, 'test_input'):
        module.test_input()

    data = module.read_input('%s/input.txt' % day)

    if hasattr(module, 'test_solution1'):
        module.test_solution1()
    print('Answer 1: %s' % _timeit(module.solution1, data))

    if hasattr(module, 'test_solution2'):
        module.test_solution2()
    print('Answer 2: %s' % _timeit(module.solution2, data))


def _timeit(func, *args, **kwargs):
    s = time.time()
    r = func(*args, **kwargs)
    e = time.time()
    print(
        'Time for %s: %f seconds' % (
            func.__name__,
            e - s
        )
    )
    return r


if __name__ == '__main__':
    main()
