I wanted to see how my optimized binary search did against other search algorithms on my
depq, so I wrote 2 other insert functions that would to my knowledge be closest and tested
all 3. The tests are below, followed by the code for both functions. The test shows the
average time it takes to insert 100 items with random priorities and is repeated 50 times.


TESTS:

C:\Users\Ofek>python
Python 3.4.2 (v3.4.2:ab2c023a9432, Oct  6 2014, 22:15:05) [MSC v.1600 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
>>> import timeit
>>> from numpy import mean
>>>
>>> s='''
... from depq import DEPQ
... from random import SystemRandom
... r = SystemRandom()
... randoms = [r.randrange(0, 3000000) for i in range(100)]
... d = DEPQ()
... for i in range(3000000): d.addfirst(i)
... '''
>>>
>>> mean(timeit.Timer('for r in randoms:d.linear_insert(None, r)', setup=s).repeat(50, 1))
3.6656986826664957
>>> mean(timeit.Timer('for r in randoms:d.binary_insert(None, r)', setup=s).repeat(50, 1))
0.96281240967293569
>>> mean(timeit.Timer('for r in randoms:d.insert(None, r)', setup=s).repeat(50, 1))
0.36838486254875036
>>>


CODE:

def linear_insert(self, item, priority):
    """Linear search. Performance is O(n^2)."""

    length = len(self.data)
    count = length

    # in practice, this is better than doing a rotate(-1) every
    # loop and getting self.data[0] each time only because deque
    # implements a very efficient iterator in C
    for i in self.data:
        if priority > i[1]:
            break
        count -= 1

    self.data.rotate(-count)
    self.data.appendleft((item, priority))
    self.data.rotate(length-count)

def binary_insert(self, item, priority):
    """Traditional binary search. Performance: O(n log n)"""

    length = len(self.data)

    index = 0
    min = 0
    max = length - 1

    while max - min > 10:

        mid = (min + max) // 2

        # If index in 1st half of list
        if priority > self.data[mid][1]:
            max = mid - 1

        # If index in 2nd half of list
        else:
            min = mid + 1

    for i in range(min, max + 1):
        if priority > self.data[i][1]:
            index = i
            break
        elif i == max:
            index = max + 1

    shift = length - index

    # Never shift more than half length of depq
    if shift > length // 2:
        shift = length % shift
        self.data.rotate(-shift)
        self.data.appendleft((item, priority))
        self.data.rotate(shift)
    else:
        self.data.rotate(shift)
        self.data.append((item, priority))
        self.data.rotate(-shift)
