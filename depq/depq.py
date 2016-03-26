import json
from collections import defaultdict, deque
from threading import Lock


class DEPQ:

    def __init__(self, iterable=None, maxlen=None):

        self.data = deque()
        self.items = defaultdict(int)
        self._maxlen = maxlen
        self.lock = Lock()

        if iterable is not None:
            self.extend(iterable)

    def insert(self, item, priority):
        """Adds item to DEPQ with given priority by performing a binary
        search on the concurrently rotating deque. Amount rotated R of
        DEPQ of length n would be n <= R <= 3n/2. Performance: O(n)"""

        with self.lock:

            self_data = self.data
            rotate = self_data.rotate
            self_items = self.items
            maxlen = self._maxlen

            try:

                if priority <= self_data[-1][1]:
                    self_data.append((item, priority))
                elif priority > self_data[0][1]:
                    self_data.appendleft((item, priority))
                else:

                    length = len(self_data) + 1
                    mid = length // 2
                    shift = 0

                    while True:

                        if priority <= self_data[0][1]:
                            rotate(-mid)
                            shift += mid
                            mid //= 2
                            if mid == 0:
                                mid += 1

                        else:
                            rotate(mid)
                            shift -= mid
                            mid //= 2
                            if mid == 0:
                                mid += 1

                        if self_data[-1][1] >= priority > self_data[0][1]:
                            self_data.appendleft((item, priority))

                            # When returning to original position, never shift
                            # more than half length of DEPQ i.e. if length is
                            # 100 and we rotated -75, rotate -25, not 75
                            if shift > length // 2:
                                shift = length % shift
                                rotate(-shift)
                            else:
                                rotate(shift)

                            break

                try:
                    self_items[item] += 1
                except TypeError:
                    self_items[repr(item)] += 1

            except IndexError:
                self_data.append((item, priority))
                try:
                    self_items[item] = 1
                except TypeError:
                    self_items[repr(item)] = 1

            if maxlen is not None and maxlen < len(self_data):
                self._poplast()

    def extend(self, iterable):
        """Adds items from iterable to DEPQ. Performance: O(n)"""
        for item in iterable:
            self.insert(*item[:2])

    def addfirst(self, item, new_priority=None):
        """Adds item to DEPQ as highest priority. The default
        starting priority is 0, the default new priority is
        self.high(). Performance: O(1)"""

        with self.lock:

            self_data = self.data

            try:
                priority = self_data[0][1]
                if new_priority is not None:
                    if new_priority < priority:
                        raise ValueError('Priority must be >= '
                                         'highest priority.')
                    else:
                        priority = new_priority
            except IndexError:
                priority = 0 if new_priority is None else new_priority

            self_data.appendleft((item, priority))
            self_items = self.items
            maxlen = self._maxlen

            try:
                self_items[item] += 1
            except TypeError:
                self_items[repr(item)] += 1

            if maxlen is not None and maxlen < len(self_data):
                self._poplast()

    def addlast(self, item, new_priority=None):
        """Adds item to DEPQ as lowest priority. The default
        starting priority is 0, the default new priority is
        self.low(). Performance: O(1)"""

        with self.lock:

            self_data = self.data
            maxlen = self._maxlen

            if maxlen is not None and maxlen == len(self_data):
                return

            try:
                priority = self_data[-1][1]
                if new_priority is not None:
                    if new_priority > priority:
                        raise ValueError('Priority must be <= '
                                         'lowest priority.')
                    else:
                        priority = new_priority
            except IndexError:
                priority = 0 if new_priority is None else new_priority

            self_data.append((item, priority))
            self_items = self.items

            try:
                self_items[item] += 1
            except TypeError:
                self_items[repr(item)] += 1

    def popfirst(self):
        """Removes item with highest priority from DEPQ. Returns
        tuple(item, priority). Performance: O(1)"""

        with self.lock:

            try:
                tup = self.data.popleft()
            except IndexError as ex:
                ex.args = ('DEPQ is already empty',)
                raise

            self_items = self.items

            try:
                self_items[tup[0]] -= 1
                if self_items[tup[0]] == 0:
                    del self_items[tup[0]]
            except TypeError:
                r = repr(tup[0])
                self_items[r] -= 1
                if self_items[r] == 0:
                    del self_items[r]

            return tup

    def poplast(self):
        """Removes item with lowest priority from DEPQ. Returns
        tuple(item, priority). Performance: O(1)"""
        with self.lock:
            return self._poplast()

    def _poplast(self):
        """For avoiding lock during inserting to keep maxlen"""

        try:
            tup = self.data.pop()
        except IndexError as ex:
            ex.args = ('DEPQ is already empty',)
            raise

        self_items = self.items

        try:
            self_items[tup[0]] -= 1
            if self_items[tup[0]] == 0:
                del self_items[tup[0]]
        except TypeError:
            r = repr(tup[0])
            self_items[r] -= 1
            if self_items[r] == 0:
                del self_items[r]

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

    @property
    def maxlen(self):
        """Returns maxlen"""
        return self._maxlen

    @maxlen.setter
    def maxlen(self, length):
        """Sets maxlen"""
        with self.lock:
            self._maxlen = length
            while len(self.data) > length:
                print('llllllllllllllllllllll')
                self._poplast()

    def count(self, item):
        """Returns number of occurrences of item in DEPQ. Performance: O(1)"""
        try:
            return self.items.get(item, 0)
        except TypeError:
            return self.items.get(repr(item), 0)

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
            self_items = self.items

            try:
                item_freq = self_items[item]
                item_repr = item
                if item_freq == 0:
                    return removed
            except TypeError:
                item_freq = self_items[repr(item)]
                item_repr = repr(item)
                if item_freq == 0:
                    return removed

            if count == -1:
                count = item_freq

            self_data = self.data
            rotate = self_data.rotate
            pop = self_data.pop
            counter = 0

            for i in range(len(self_data)):
                if count > counter and item == self_data[-1][0]:
                    removed.append(pop())
                    counter += 1
                    continue
                rotate()

            if item_freq <= count:
                del self_items[item_repr]
            else:
                self_items[item_repr] -= count

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
