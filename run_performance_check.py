__doc__ = """I wanted to see how my optimized binary search did against other
search algorithms on my DEPQ, so I wrote 2 other insert functions that would
to my knowledge be closest and tested all 3. The test results are below and
can be run again by executing the performance check. The test shows the stats
regarding the time it takes to insert 100 items with random priorities and is
repeated 150 times. Only the lowest 100 times are used in calculations to
avoid OS introduced inconsistencies. The check tests the speed of 3 different
sized DEPQ instances to show how the algorithms scale.\n\n
"""

import os
import timeit


def get_stats(data):
    data = sorted(data)[:100]
    n = len(data)
    i = (n + 1) // 4
    m = n // 2
    if n % 4 in (0, 3):
        q1 = (data[i] + data[i - 1]) / 2
        q3 = (data[-i - 1] + data[-i]) / 2
    else:
        q1 = data[i]
        q3 = data[-i - 1]
    if n % 2 == 0:
        q2 = (data[m - 1] + data[m]) / 2
    else:
        q2 = data[m]
    return data[0], data[-1], (q1 + 2*q2 + q3) / 4.0


def linear_insert(self, item, priority):
    """Linear search. Performance is O(n^2)."""

    with self.lock:
        self_data = self.data
        rotate = self_data.rotate
        maxlen = self._maxlen
        length = len(self_data)
        count = length

        # in practice, this is better than doing a rotate(-1) every
        # loop and getting self.data[0] each time only because deque
        # implements a very efficient iterator in C
        for i in self_data:
            if priority > i[1]:
                break
            count -= 1

        rotate(-count)
        self_data.appendleft((item, priority))
        rotate(length-count)

        try:
            self.items[item] += 1
        except TypeError:
            self.items[repr(item)] += 1

        if maxlen is not None and maxlen < len(self_data):
                self._poplast()

def binary_insert(self, item, priority):
    """Traditional binary search. Performance: O(n log n)"""

    with self.lock:
        self_data = self.data
        rotate = self_data.rotate
        maxlen = self._maxlen
        length = len(self_data)

        index = 0
        min = 0
        max = length - 1

        while max - min > 10:

            mid = (min + max) // 2

            # If index in 1st half of list
            if priority > self_data[mid][1]:
                max = mid - 1

            # If index in 2nd half of list
            else:
                min = mid + 1

        for i in range(min, max + 1):
            if priority > self_data[i][1]:
                index = i
                break
            elif i == max:
                index = max + 1

        shift = length - index

        # Never shift more than half length of depq
        if shift > length // 2:
            shift = length % shift
            rotate(-shift)
            self_data.appendleft((item, priority))
            rotate(shift)
        else:
            rotate(shift)
            self_data.append((item, priority))
            rotate(-shift)

        try:
            self.items[item] += 1
        except TypeError:
            self.items[repr(item)] += 1

        if maxlen is not None and maxlen < len(self_data):
                self._poplast()

def get_times(size):
    size_text = 'Size of DEPQ: {}\n{}\n'.format(size, ''.join(('=' for _ in range(40))))
    print(size_text)
    setup = ('from depq.depq import DEPQ\n'
             'from run_performance_check import binary_insert, linear_insert\n'
             'DEPQ.binary_insert, DEPQ.linear_insert = binary_insert, linear_insert\n'
             'from random import SystemRandom\n'
             'r = SystemRandom()\n'
             'randoms = [r.randrange(0, {}) for i in range(100)]\n'
             'd = DEPQ()\n'
             'for i in range({}): d.addfirst(None, i)\n'.format(size, size))

    linear = get_stats(timeit.Timer('for r in randoms:d.linear_insert(None, r)', setup=setup).repeat(150, 1))
    linear_result = 'Linear search result:\n==> Minimum: {}\n==> Maximum: {}\n==> Trimean: {}\n\n'.format(*linear)
    print(linear_result)

    binary = get_stats(timeit.Timer('for r in randoms:d.binary_insert(None, r)', setup=setup).repeat(150, 1))
    binary_result = 'Binary search result:\n==> Minimum: {}\n==> Maximum: {}\n==> Trimean: {}\n\n'.format(*binary)
    print(binary_result)

    custom = get_stats(timeit.Timer('for r in randoms:d.insert(None, r)', setup=setup).repeat(150, 1))
    custom_result = 'Custom search result:\n==> Minimum: {}\n==> Maximum: {}\n==> Trimean: {}\n\n'.format(*custom)
    print(custom_result)

    return size_text, linear_result, binary_result, custom_result

def main():
    print(__doc__)
    a = get_times(500000)
    b = get_times(1000000)
    c = get_times(3000000)

    here = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(here, 'performance_results.txt'), 'w') as f:
        f.write(__doc__)
        f.write('{}{}{}{}'.format(*a))
        f.write('{}{}{}{}'.format(*b))
        f.write('{}{}{}{}'.format(*c))

    input('\n\nPress enter to quit ')

if __name__ == '__main__':
    main()
