import importlib
import sys
import time


def main():
    day = sys.argv[1]
    module = importlib.import_module('%s.solution' % day)
    if hasattr(module, 'test_read_input'):
        print('Testing input processing...')
        module.test_read_input()
        print('Success')

    data = module.read_input('%s/input.txt' % day)

    if hasattr(module, 'test_solution1'):
        print('Testing solution1...')
        module.test_solution1()
        print('Success')
    print('Answer 1: %s' % str(_timeit(module.solution1, data)))

    if hasattr(module, 'test_solution2'):
        print('Testing solution2...')
        module.test_solution2()
        print('Success')
    print('Answer 2: %s' % str(_timeit(module.solution2, data)))


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
