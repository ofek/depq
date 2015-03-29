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

__doc__ = """==========
depq - Double-ended priority queue
==========

  - Python implementation of a thread-safe and efficient
    double-ended priority queue (DEPQ) in which items and their
    priority values are stored in a deque object as tuples.
    This can also be used as a regular priority queue, or simply a
    FIFO/LIFO queue.

Features & advantages of this implementation:

  - Completely thread-safe
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

  - Priorities are always in proper order, thus, a binary search
    is performed to find the right index with which to insert new
    items when specifying priority. Normally, this would result in
    O(n log n) performance when adding items via insert(item, priority)
    where self.high() > priority > self.low() because deque (as a
    doubly linked list) random access is O(n).

    Though, ACTUALLY that is not the case here as I've been able to
    reduce that to O(n) by modifying the binary search to operate while
    the internal deque is concurrently rotating.

Notes:

  - The items in DEPQ are also stored along with their frequency in a
    separate dict for O(1) lookup. If item is un-hashable, the repr()
    of that item is stored instead. So 'item in DEPQ' would check the
    dict for item and if TypeError is thrown it would try repr(item).
  - This implementation inserts in the middle in linear time whereas
    a textbook DEPQ is O(log n). In actual use cases though, this
    infinitesimal increase in run time is irrelevant, especially when
    one considers the extra functionality gained coupled with the
    fact that the other 2 main operations popfirst() and poplast() now
    occur in constant time."""

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
                        raise ValueError
                    else:
                        priority = new_priority
            except IndexError:
                priority = self.start if new_priority is None else new_priority
            except ValueError:
                raise ValueError('\nPriority must be >= highest priority.')

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
                        raise ValueError
                    else:
                        priority = new_priority
            except IndexError:
                priority = self.start if new_priority is None else new_priority
            except ValueError:
                raise ValueError('\nPriority must be <= lowest priority.')

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
            except IndexError:
                raise IndexError('DEPQ is already empty')

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
            except IndexError:
                raise IndexError('DEPQ is already empty')

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
            except IndexError:
                raise IndexError('DEPQ is empty')

    def last(self):
        """Gets item with lowest priority. Performance: O(1)"""
        with self.lock:
            try:
                return self.data[-1][0]
            except IndexError:
                raise IndexError('DEPQ is empty')

    def high(self):
        """Gets highest priority. Performance: O(1)"""
        with self.lock:
            try:
                return self.data[0][1]
            except IndexError:
                raise IndexError('DEPQ is empty')

    def low(self):
        """Gets lowest priority. Performance: O(1)"""
        with self.lock:
            try:
                return self.data[-1][1]
            except IndexError:
                raise IndexError('DEPQ is empty')

    def size(self):
        """Gets length of DEPQ. Performance: O(1)"""
        with self.lock:
            return len(self.data)

    def clear(self):
        """Empties DEPQ. Performance: O(1)"""
        with self.lock:
            self.data.clear()
            self.items.clear()

    def is_empty(self):
        """Returns True if DEPQ is empty, else False. Performance: O(1)"""
        with self.lock:
            return len(self.data) == 0

    def count(self, item):
        """Returns number of occurrences of item in DEPQ. Performance: O(1)"""

        with self.lock:

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
            except ValueError:
                raise ValueError('{} cannot be represented as '
                                 'an integer'.format(count))
            except TypeError:
                raise TypeError('{} cannot be represented as '
                                'an integer'.format(count))

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
            except IndexError:
                raise IndexError('DEPQ has no index {}'.format(index))

    def __setitem__(self, item, priority):
        """Alias for self.insert"""
        self.insert(item, priority)

    def __delitem__(self, index):
        raise NotImplementedError('\nItems cannot be deleted by '
                                  'referencing arbitrary indices.')

    def __len__(self):
        with self.lock:
            return len(self.data)

    def __repr__(self):
        with self.lock:
            return 'DEPQ([{}])'.format(', '.join(str(item) for item in self.data))

    def __str__(self):
        with self.lock:
            return 'DEPQ([{}])'.format(', '.join(str(item) for item in self.data))

    def __unicode__(self):
        return self.__str__()
