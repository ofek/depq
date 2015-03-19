# Copyright (c) 2015 Ofek Lev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# Designed and coded by Ofek Lev ofekmeister@gmail.com
#
# Description:
#
# Python implementation of a thread-safe and efficient
# double-ended priority queue (DEPQ) in which items and their
# priority values are stored in a deque object as tuples.
#
# Advantages of this implementation:
#    - popfirst() and poplast() have O(1) performance instead of
#      running in logarithmic time like in a standard DEPQ
#    - Items with equal priorities are sorted in the order they were
#      originally added
#    - Specific items can be deleted or their priorities changed
#    - Priority values can be floats and negative
#    - Naturally fast also because deque object is implemented in C
#
# Implementation:
#    - Priorities are always in proper order, thus, a binary search
#      is performed to find the right index with which to insert new
#      items when specifying priority. This should result in the standard
#      O(log n) performance when adding items via insert(item, priority)
#      where self.high() > priority > self.low(), though, it actually
#      occurs in somewhere between O(log n) and O(k) only because deque
#      (as a doubly linked list) random access is closer to O(k) towards
#      the middle. In actual use cases though, this infinitesimal increase
#      in run time is irrelevant, especially when one considers the extra
#      functionality gained coupled with the fact that the other 2 main
#      operations popfirst() and poplast() now occur in constant time.
#
# Notes:
#
# To be compatible with earlier versions of Python, remove
# 'from None' from raised exceptions

from collections import deque

class DEPQ:

    def __init__(self, priority=float):
        """Initialize as a double-ended queue"""

        self.data = deque()
        self.priority = priority
    
    def linear_insert(self, item, priority):
        """Adds item to depq with given priority. Performance is O(n)."""

        length = len(self.data)
        count = length
            
        for i in self.data:
            if priority > i[1]:
                break
            count -= 1
            
        self.data.rotate(-count)
        self.data.appendleft((item, priority))
        self.data.rotate(length-count)
    
    def insert(self, item, priority):
        """Adds item to depq with given priority. Performance is
        somewhere between O(n log n) and O(n)."""

        if self.data:
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
                        if shift > length // 2:
                            shift = length % shift + 1
                            self.data.rotate(-shift)
                        else:
                            self.data.rotate(shift)
                        break

        else:
            self.data.append((item, priority))

    def binary_insert(self, item, priority):
        """Adds item to depq with given priority. Method uses
        a modified binary search for finding proper place to
        insert items into depq. Search transitions to linear
        when possibilities are <= 10. Performance: O(n log n)"""

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

    def addfirst(self, item, step = 1):
        """Adds item to depq as highest priority.
        The default starting priority is 0, the
        default increment is 1 (one). If step is 0,
        self.high() is used as item's priority.
        Performance: O(1)"""
        
        if step < 0:
            raise TypeError('\nIncrement must be represented\n\
                             as a positive number or 0')

        # If not empty
        if self.data:
            priority = self.high() + step

        # Otherwise, start at 0
        else:
            priority = self.priority(0)

        self.data.appendleft((item, priority))

    def addlast(self, item, step = -1):
        """Adds item to depq as lowest priority.
        The default starting priority is 0, the
        default increment is -1 (negative one).
        If step is 0, self.low() is used as
        item's priority. Performance: O(1)"""
        
        if step > 0:
            raise TypeError('\nIncrement must be represented\n\
                             as a negative number or 0')

        # If not empty
        if self.data:
            priority = self.low() + step

        # Otherwise, start at 0
        else:
            priority = self.priority(0)

        self.data.append((item, priority))

    def popfirst(self):
        """Removes item with highest priority from depq, makes use of the
        deque class's fast manipulation of both ends. Performance: O(1)"""

        try:
            return self.data.popleft()
        except IndexError:
            raise IndexError('depq is already empty')

    def poplast(self):
        """Removes item with lowest priority from depq, makes use of the
        deque class's fast manipulation of both ends. Performance: O(1)"""

        try:
            return self.data.pop()
        except IndexError:
            raise IndexError('depq is already empty')

    def first(self):
        """Gets item with highest priority. Performance: O(1)"""
        return self._getitem(0)

    def last(self):
        """Gets item with lowest priority. Performance: O(1)"""
        return self._getitem(-1)

    def high(self):
        """Gets highest priority. Performance: O(1)"""
        return self._getpriority(0)

    def low(self):
        """Gets lowest priority. Performance: O(1)"""
        return self._getpriority(-1)

    def size(self):
        """Gets length of depq. Performance: O(1)"""
        return len(self.data)

    def clear(self):
        """Empties depq. Performance: O(1)"""
        self.data.clear()

    def is_empty(self):
        """Returns True if depq is empty"""
        return len(self.data) == 0

    def get(self, index):
        """Returns item and priority of given index as a tuple."""
        try:
            t = self.data[index]
            return (t[0], t[1])
        except IndexError:
            raise IndexError('depq has no index ' + str(index))

    def remove(self, item):
        """Removes first occurrence of given item with lowest
        priority. Useful for tasks that no longer require completion,
        ex-clients, etc."""

        index = 0
        match = 0

        for i in reversed(self.data):
            if item == i[0]:
                match = 1
                break
            index += 1

        if match:
            index = (len(self.data) - 1) - index
            priority = self.data[index][1]
            del self.data[index]
            return priority

    def elim(self, item):
        """Remove all occurrences of item."""
        while self.remove(item):
            pass

    def sub(self, item1, item2):
        """Substitutes item1 for item2, raises TypeError
        if item isn't in depq."""
        self.insert(item2, self.remove(item1))

    def set(self, item, priority):
        """Changes priority of first occurrence of given item with
        lowest priority. item added to depq if not found."""
        self.remove(item)
        self.insert(item, priority)

    def mode(self):
        """Gets most frequent and highest priority value"""

        try:
            if self.data:
                length = len(self.data)
                value = ''
                priority = self.data[0][1]
                freq =  0
                count = 0
                iter =  0

                for index in range(length):

                    # If another occurrence of value, continue counting
                    if value == self.data[index][1]:
                        count += 1
                        # End of loop
                        if iter == length - 1 and count > freq:
                            freq = count
                            priority = value

                    # If new value encountered, test then start count over
                    else:
                        if count > freq:
                            freq = count
                            priority = value
                        value = self.data[index][1]
                        count = 1

                    iter += 1

                return priority
            else:
                return None
        except IndexError:
            raise IndexError('depq is empty')

    def median(self):
        """Gets median priority value"""

        try:
            if self.data:
                length = len(self.data)

                # Get average of middle two indices
                if length % 2 == 0:
                    mid = length // 2 - 1
                    return (self.data[mid][1] + self.data[mid + 1][1]) / 2.0

                # Or get middle index
                else:
                    mid = (length - 1) // 2
                    return self.data[mid][1]
            else:
                return None
        except IndexError:
            raise IndexError('depq is empty')

    def mean(self):
        """Gets average priority value as a float"""
        
        if self.data:
            total = self.priority(0)
            for item in self.data:
                total += item[1]
            return total/len(self.data)
        else:
            return None

    def _getitem(self, index):
        """Gets priority at given index"""
        try:
            return self.data[index][0]
        except IndexError:
            return None

    def _getpriority(self, index):
        """Gets priority at given index"""
        try:
            return self.data[index][1]
        except IndexError:
            return None

    def __contains__(self, item):
        """Checks for presence in depq"""
        for i in self.data:
            if item == i[0]:
                return True
        return False

    def __iter__(self):
        """Generator for iteration over depq"""
        return iter(self.data)

    def __getitem__(self, index):
        """Gets item at given index"""
        try:
            return self.data[index][0]
        except IndexError:
            raise IndexError('depq has no index ' + str(index))

    def __setitem__(self, item, priority):
        self.set(item, priority)

    def __delitem__(self, index):
        raise Exception('\nItems cannot be deleted by\n\
                         referencing arbitrary indices')

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return 'depq([{}])'.format(', '.join(str(s) for s in self.data))

    def __str__(self):
        return '[{}]'.format(', '.join(str(s) for s in self.data))