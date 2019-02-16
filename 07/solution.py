from collections import defaultdict, deque
from copy import deepcopy


def read_input(filename):
    steps = defaultdict(set)
    deps = defaultdict(set)

    with open(filename) as f:
        for line in f:
            tokens = line.split()
            first, second = tokens[1], tokens[7]
            steps[first].add(second)
            if second not in steps:
                steps[second] = set()
            deps[second].add(first)
            if first not in deps:
                deps[first] = set()
    return {'steps': steps, 'deps': deps}


def solution1(data):
    data = deepcopy(data)
    steps, deps = data['steps'], data['deps']
    return _solve(steps, deps, 1, step_time=lambda x: 1)


def solution2(data):
    data = deepcopy(data)
    steps, deps = data['steps'], data['deps']
    return _solve(steps, deps, 5, step_time=lambda x: ord(x) - 64 + 60)


def _solve(steps, deps, n_workers, step_time):
    total = 0
    result = []
    steps_in_progress = {}
    while steps or any(steps_in_progress):
        # schedule steps
        available_steps = deque(
            sorted(
                s for s in steps if not deps[s] and s not in steps_in_progress and s not in result
            )
        )
        while available_steps and len(steps_in_progress) < n_workers:
            scheduled_step = available_steps.popleft()
            steps_in_progress[scheduled_step] = step_time(scheduled_step)
        # work on steps
        finished_steps, time_work_done, steps_in_progress = _work(steps_in_progress)
        result += finished_steps
        total += time_work_done

        # remove finished tasks from the dependency list

        for finished_step in finished_steps:
            for next_step in steps[finished_step]:
                deps[next_step].remove(finished_step)
            del steps[finished_step]
    return 'Answer: %d, order: %s' % (total, ''.join(result))


def _work(steps_in_progress):
    worked_time = min(steps_in_progress.values())
    remaining_work_in_progress = {}
    finished_steps = []
    for step, time_step in steps_in_progress.items():
        time_left = time_step - worked_time
        if time_left:
            remaining_work_in_progress[step] = time_left
        else:
            finished_steps.append(step)
    return sorted(finished_steps), worked_time, remaining_work_in_progress
