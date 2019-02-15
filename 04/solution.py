import re

from collections import Counter


pat = re.compile('\[(?P<date>\d{4}-\d{2}-\d{2}) (?P<h>\d{2}):(?P<m>\d{2})\] (?P<event>.+)')
patg = re.compile('\d+')


def read_input(filename):
    guard_journal = {}
    guard_on_shift = None
    sleep_start = None
    with open(filename) as f:
        for i, line in enumerate(sorted(f.readlines())):
            date, hour, minute, event = _parse(line)
            if event.endswith('begins shift'):
                guard_on_shift = _get_guard_id(event)
                if not guard_on_shift in guard_journal:
                    guard_journal[guard_on_shift] = {}
                sleep_start = 0
            elif event == 'falls asleep':
                sleep_start = minute
            elif event == 'wakes up':
                guard_info = guard_journal[guard_on_shift]
                if date not in guard_info:
                    guard_info[date] = []
                guard_info[date] += range(sleep_start, minute)
    return guard_journal


def _parse(line):
    m = re.match(pat, line)
    if not m:
        raise Exception('Invalid line: %s' % line)
    return m.group('date'), int(m.group('h')), int(m.group('m')), m.group('event')


def _get_guard_id(event):
    m = re.search(patg, event)
    if not m:
        raise Exception('Invalid new shift entry: %s' % event)
    return int(m.group(0))


def solution1(guard_journal):
    max_sleep = 0
    max_count_by_minute = None
    m_gid = None
    for gid, sleep_schedule in guard_journal.items():
        count_by_minute = sum(
            [Counter(d_m) for d_m in sleep_schedule.values()],
            Counter()
        )
        total_sleep_for_guard = sum(count_by_minute.values())
        if total_sleep_for_guard > max_sleep:
            m_gid = gid
            max_sleep = total_sleep_for_guard
            max_count_by_minute = count_by_minute
    minute, max_f = max_count_by_minute.most_common(1)[0]
    print(
        'guard %d slept for %d minutes, most frequent sleeps on minute %d: %d times'
        % (m_gid, max_sleep, minute, max_f)
    )
    return m_gid * minute


def solution2(guard_journal):
    top_frequency = 0
    t_gid = None
    top_minute = None

    for gid, sleep_schedule in guard_journal.items():
        count_by_minute = sum([Counter(d_m) for d_m in sleep_schedule.values()], Counter())
        if count_by_minute:  # some guards may not sleep at all
            minute, frequency = count_by_minute.most_common(1)[0]
            if frequency > top_frequency:
                top_frequency = frequency
                t_gid = gid
                top_minute = minute

    print('Guard %d sleeps the most (%d times) on minute %d' % (t_gid, top_frequency, top_minute))
    return t_gid * top_minute
