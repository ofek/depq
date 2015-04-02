__license__ = """
Copyright (c) 2015 Ofek Lev ofekmeister@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__doc__ = """
==================================
depq - Double-ended priority queue
==================================

- Python implementation of a thread-safe and efficient
  double-ended priority queue (DEPQ) in which items and their
  priority values are stored in a deque object as tuples.
  This can also be used as a regular priority queue, or simply a
  FIFO/LIFO queue.

Features & advantages of this implementation:
---------------------------------------------

- Completely thread-safe
- Serializable via pickling or JSON
- Priority values can be ints/floats, numpy types, strings, or
  any other comparable type you choose!
- popfirst() and poplast() have O(1) performance instead of
  running in logarithmic time like in a standard DEPQ
- Naturally fast also because deque object is implemented in C
- Items with equal priorities are sorted in the order they were
  originally added
- Specific items can be deleted or their priorities changed
- Membership testing with 'in' operator occurs in O(1) as does
  getting an item's frequency in DEPQ via count(item)

Implementation:
---------------

- Priorities are always in proper order, thus, a binary search
  is performed to find the right index with which to insert new
  items when specifying priority. Normally, this would result in
  O(n log n) performance when adding items via insert(item, priority)
  where self.high() > priority > self.low() because deque (as a
  doubly linked list) random access is O(n).

  Though, ACTUALLY that is not the case here as I've been able to
  reduce that to O(n) by modifying the binary search to operate while
  the internal deque is concurrently rotating.

Examples:
---------

>>> from textwrap import fill  # For nice wrapped printing
>>> from depq import DEPQ
>>>
>>> depq = DEPQ(start=0)  # Default. DEPQ.start only used for addfirst &
>>>                       # addlast without argument on empty DEPQ
>>>
>>> # Add some characters with their ordinal
>>> # values as priority and keep count
>>> for c in 'AN_ERRONEOUS_STRING':
...     count = list(  # This is hacky and not important, skip next 4 lines :)
...         x + 1 if '{} #{}'.format(c, x + 1) in depq
...         else next(iter(())) if x != 0 else 0
...         for x in range(len(depq) + 1)
...     )[-1]
...     depq.insert('{} #{}'.format(c, count + 1), ord(c))
...
>>> print(fill(str(depq), 77))
DEPQ([('_ #1', 95), ('_ #2', 95), ('U #1', 85), ('T #1', 84), ('S #1', 83),
('S #2', 83), ('R #1', 82), ('R #2', 82), ('R #3', 82), ('O #1', 79), ('O
#2', 79), ('N #1', 78), ('N #2', 78), ('N #3', 78), ('I #1', 73), ('G #1',
71), ('E #1', 69), ('E #2', 69), ('A #1', 65)])
>>>
>>> # As you can see items with equal priorities are sorted in the order
>>> # they were originally added. Also note DEPQ root (depq[0]) is highest
>>> # priority like a max heap.
>>>
>>> depq.first()
'_ #1'
>>> depq.last()
'A #1'
>>> depq.high()
95
>>> depq.low()
65
>>> depq[7]  # Returns tuple(item, priority)
('R #2', 82)
>>>
>>> depq.poplast()
('A #1', 65)
>>> depq.last()
'E #2'
>>>
>>> depq.size()  # Alias for len(DEPQ)
18
>>> depq.is_empty()
False
>>> depq.clear()
>>> depq.is_empty()
True
>>>
>>> depq.addfirst('starter')  # For an empty DEPQ, addfirst & addlast are
>>>                           # functionally identical; they add item to DEPQ
>>> depq                      # with given priority, or default DEPQ.start
DEPQ([('starter', 0)])
>>>
>>> depq.addfirst('high')  # Default priority DEPQ.high()
>>> depq.addlast('low')  # Default priority DEPQ.low()
>>> depq
DEPQ([('high', 0), ('starter', 0), ('low', 0)])
>>> depq.addfirst('higher', depq.high() + 1)
>>> depq.addlast('lower', depq.low() - 1)
>>> depq
DEPQ([('higher', 1), ('high', 0), ('starter', 0), ('low', 0), ('lower', -1)])
>>>
>>> depq.addfirst('highest', 0)  # Invalid priority raises exception
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Python34\lib\depq.py", line 309, in addfirst
    raise ValueError('Priority must be >= '
ValueError: Priority must be >= highest priority.
>>>
>>> del depq[0]  # As does del
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Python34\lib\depq.py", line 577, in __delitem__
    raise NotImplementedError('Items cannot be deleted by '
NotImplementedError: Items cannot be deleted by referencing arbitrary indices.
>>>
>>> depq.clear()
>>> depq.count(None)
0
>>> for i in range(10):
...     depq.insert(None, i)
...
>>> print(fill(str(depq), 77))
DEPQ([(None, 9), (None, 8), (None, 7), (None, 6), (None, 5), (None, 4),
(None, 3), (None, 2), (None, 1), (None, 0)])
>>>
>>> None in depq
True
>>> depq.count(None)
10
>>> depq.remove(None)  # Removes item from DEPQ, default # of removals is 1
[(None, 0)]
>>>
>>> print(fill(str(depq), 77))
DEPQ([(None, 9), (None, 8), (None, 7), (None, 6), (None, 5), (None, 4),
(None, 3), (None, 2), (None, 1)])
>>>
>>> depq.remove(None, 4)  # As you see, returns list of tuple(item, priority)
[(None, 1), (None, 2), (None, 3), (None, 4)]
>>> print(fill(str(depq), 77))
DEPQ([(None, 9), (None, 8), (None, 7), (None, 6), (None, 5)])
>>>
>>> depq[None] = 7  # Alias for DEPQ.insert(item, priority)
>>> print(fill(str(depq), 77))
DEPQ([(None, 9), (None, 8), (None, 7), (None, 7), (None, 6), (None, 5)])
>>>
>>> depq.elim(None)  # This simply calls DEPQ.remove(item, -1)
[(None, 5), (None, 6), (None, 7), (None, 7), (None, 8), (None, 9)]
>>> print(fill(str(depq), 77))
DEPQ([])
>>>
>>> import pickle  # Pickling won't work if items aren't picklable
>>> import json  # JSON won't work if items aren't JSON serializable
>>>
>>> for i in range(5):
...     depq.insert([i], i)  # Unhashable types allowed but don't mutate them!
...
>>> depq
DEPQ([([4], 4), ([3], 3), ([2], 2), ([1], 1), ([0], 0)])
>>>
>>> binary_depq = pickle.dumps(depq)
>>> json_depq = json.dumps(depq.to_json())
>>>
>>> depq_from_pickle = pickle.loads(binary_depq)
>>> depq_from_json = DEPQ.from_json(json_depq)  # Classmethod returns new DEPQ
>>>
>>> depq
DEPQ([([4], 4), ([3], 3), ([2], 2), ([1], 1), ([0], 0)])
>>> depq_from_pickle
DEPQ([([4], 4), ([3], 3), ([2], 2), ([1], 1), ([0], 0)])
>>> depq_from_json
DEPQ([([4], 4), ([3], 3), ([2], 2), ([1], 1), ([0], 0)])
>>>

Notes:
------

- The items in DEPQ are also stored along with their frequency in a
  separate dict for O(1) lookup. If item is un-hashable, the repr()
  of that item is stored instead. So 'item in DEPQ' would check the
  dict for item and if TypeError is raised it would try repr(item).
- This implementation inserts in the middle in linear time whereas
  a textbook DEPQ is O(log n). In actual use cases though, this
  infinitesimal increase in run time is irrelevant, especially when
  one considers the extra functionality gained coupled with the
  fact that the other 2 main operations popfirst() and poplast() now
  occur in constant time."""

import json
from collections import deque
from threading import Lock


class DEPQ:

    def __init__(self, start=0):
        """Initialize as a double-ended queue."""

        self.data = deque()
        self.items = dict()
        self.start = start
        self.lock = Lock()

    def insert(self, item, priority):
        """Adds item to DEPQ with given priority by performing a binary
        search on the concurrently rotating deque. Amount rotated R of
        DEPQ of length n would be n <= R <= 3n/2. Performance: O(n)"""

        with self.lock:

            try:

                if priority > self.data[0][1]:
                    self.data.appendleft((item, priority))
                elif priority <= self.data[-1][1]:
                    self.data.append((item, priority))
                else:

                    length = len(self.data)
                    mid = length // 2
                    shift = 0

                    while True:

                        if priority <= self.data[0][1]:
                            self.data.rotate(-mid)
                            shift += mid
                            mid //= 2
                            if mid == 0:
                                mid += 1

                        else:
                            self.data.rotate(mid)
                            shift -= mid
                            mid //= 2
                            if mid == 0:
                                mid += 1

                        if self.data[-1][1] >= priority > self.data[0][1]:
                            self.data.appendleft((item, priority))

                            # When returning to original position, never shift
                            # more than half length of DEPQ i.e. if length is
                            # 100 and we rotated -75, rotate -25, not 75
                            if shift > length // 2:
                                shift = length % shift + 1
                                self.data.rotate(-shift)
                            else:
                                self.data.rotate(shift)

                            break

                try:
                    self.items[item] += 1
                except KeyError:
                    self.items[item] = 1
                except TypeError:
                    try:
                        self.items[repr(item)] += 1
                    except KeyError:
                        self.items[repr(item)] = 1

            except IndexError:
                self.data.append((item, priority))
                try:
                    self.items[item] = 1
                except TypeError:
                    self.items[repr(item)] = 1

    def addfirst(self, item, new_priority=None):
        """Adds item to DEPQ as highest priority. The default
        starting priority is self.start, the default new
        priority is self.high(). Performance: O(1)"""

        with self.lock:

            try:
                priority = self.data[0][1]
                if new_priority is not None:
                    if new_priority < priority:
                        raise ValueError('Priority must be >= '
                                         'highest priority.')
                    else:
                        priority = new_priority
            except IndexError:
                priority = self.start if new_priority is None else new_priority

            self.data.appendleft((item, priority))

            try:
                self.items[item] += 1
            except KeyError:
                self.items[item] = 1
            except TypeError:
                try:
                    self.items[repr(item)] += 1
                except KeyError:
                    self.items[repr(item)] = 1

    def addlast(self, item, new_priority=None):
        """Adds item to DEPQ as lowest priority. The default
        starting priority is self.start, the default new
        priority is self.low(). Performance: O(1)"""

        with self.lock:

            try:
                priority = self.data[-1][1]
                if new_priority is not None:
                    if new_priority > priority:
                        raise ValueError('Priority must be <= '
                                         'lowest priority.')
                    else:
                        priority = new_priority
            except IndexError:
                priority = self.start if new_priority is None else new_priority

            self.data.append((item, priority))

            try:
                self.items[item] += 1
            except KeyError:
                self.items[item] = 1
            except TypeError:
                try:
                    self.items[repr(item)] += 1
                except KeyError:
                    self.items[repr(item)] = 1

    def popfirst(self):
        """Removes item with highest priority from DEPQ. Returns
        tuple(item, priority). Performance: O(1)"""

        with self.lock:

            try:
                tup = self.data.popleft()
            except IndexError as ex:
                ex.args = ('DEPQ is already empty',)
                raise

            try:
                self.items[tup[0]] -= 1
                if self.items[tup[0]] == 0:
                    del self.items[tup[0]]
            except TypeError:
                r = repr(tup[0])
                self.items[r] -= 1
                if self.items[r] == 0:
                    del self.items[r]

            return tup

    def poplast(self):
        """Removes item with lowest priority from DEPQ. Returns
        tuple(item, priority). Performance: O(1)"""

        with self.lock:

            try:
                tup = self.data.pop()
            except IndexError as ex:
                ex.args = ('DEPQ is already empty',)
                raise

            try:
                self.items[tup[0]] -= 1
                if self.items[tup[0]] == 0:
                    del self.items[tup[0]]
            except TypeError:
                r = repr(tup[0])
                self.items[r] -= 1
                if self.items[r] == 0:
                    del self.items[r]

            return tup

    def first(self):
        """Gets item with highest priority. Performance: O(1)"""
        with self.lock:
            try:
                return self.data[0][0]
            except IndexError as ex:
                ex.args = ('DEPQ is empty',)
                raise

    def last(self):
        """Gets item with lowest priority. Performance: O(1)"""
        with self.lock:
            try:
                return self.data[-1][0]
            except IndexError as ex:
                ex.args = ('DEPQ is empty',)
                raise

    def high(self):
        """Gets highest priority. Performance: O(1)"""
        with self.lock:
            try:
                return self.data[0][1]
            except IndexError as ex:
                ex.args = ('DEPQ is empty',)
                raise

    def low(self):
        """Gets lowest priority. Performance: O(1)"""
        with self.lock:
            try:
                return self.data[-1][1]
            except IndexError as ex:
                ex.args = ('DEPQ is empty',)
                raise

    def size(self):
        """Gets length of DEPQ. Performance: O(1)"""
        return len(self.data)

    def clear(self):
        """Empties DEPQ. Performance: O(1)"""
        with self.lock:
            self.data.clear()
            self.items.clear()

    def is_empty(self):
        """Returns True if DEPQ is empty, else False. Performance: O(1)"""
        return len(self.data) == 0

    def count(self, item):
        """Returns number of occurrences of item in DEPQ. Performance: O(1)"""

        # If item isn't in DEPQ, returning 0 is
        # more appropriate than None, methinks.
        try:
            return self.items[item]
        except KeyError:
            return 0
        except TypeError:
            try:
                return self.items[repr(item)]
            except KeyError:
                return 0

    def remove(self, item, count=1):
        """Removes occurrences of given item in ascending priority. Default
        number of removals is 1. Useful for tasks that no longer require
        completion, inactive clients, certain algorithms, etc. Returns a
        list of tuple(item, priority). Performance: O(n)"""

        with self.lock:

            try:
                count = int(count)
            except ValueError as ex:
                ex.args = ('{} cannot be represented as an '
                           'integer'.format(count),)
                raise
            except TypeError as ex:
                ex.args = ('{} cannot be represented as an '
                           'integer'.format(count),)
                raise

            removed = []

            try:
                item_freq = self.items[item]
                item_repr = item
            except KeyError:
                return removed
            except TypeError:
                try:
                    item_freq = self.items[repr(item)]
                    item_repr = repr(item)
                except KeyError:
                    return removed

            if count == -1:
                count = item_freq

            counter = 0

            for i in range(len(self.data)):
                if count > counter and item == self.data[-1][0]:
                    removed.append(self.data.pop())
                    counter += 1
                    continue
                self.data.rotate()

            if item_freq <= count:
                del self.items[item_repr]
            else:
                self.items[item_repr] -= count

            return removed

    def elim(self, item):
        """Removes all occurrences of item. Returns a list of
        tuple(item, priority). Performance: O(n)"""
        return self.remove(item, -1)

    def to_json(self):
        with self.lock:
            state = self.__dict__.copy()
            state['data'] = list(state['data'])
            del state['lock']
            return state

    @classmethod
    def from_json(cls, json_str):
        depq = DEPQ()
        state = json.loads(json_str)
        state['data'] = deque(tuple(pair) for pair in state['data'])
        depq.__dict__.update(state)
        return depq

    def __getstate__(self):
        with self.lock:
            state = self.__dict__.copy()
            del state['lock']
            return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lock = Lock()

    def __contains__(self, item):
        try:
            return item in self.items
        except TypeError:
            return repr(item) in self.items

    def __iter__(self):
        """Returns highly efficient deque C iterator."""
        with self.lock:
            return iter(self.data)

    def __getitem__(self, index):
        with self.lock:
            try:
                return self.data[index]
            except IndexError as ex:
                ex.args = ('DEPQ has no index {}'.format(index),)
                raise

    def __setitem__(self, item, priority):
        """Alias for self.insert"""
        self.insert(item, priority)

    def __delitem__(self, index):
        raise NotImplementedError('Items cannot be deleted by '
                                  'referencing arbitrary indices.')

    def __len__(self):
        return len(self.data)

    def __str__(self):
        with self.lock:
            return 'DEPQ([{}])'.format(
                ', '.join(str(item) for item in self.data)
            )

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()
