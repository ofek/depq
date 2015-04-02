.. image:: https://travis-ci.org/Ofekmeister/depq.svg?branch=master
  :target: https://travis-ci.org/Ofekmeister/depq

.. image:: https://coveralls.io/repos/Ofekmeister/depq/badge.svg?branch=master
  :target: https://coveralls.io/r/Ofekmeister/depq?branch=master

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
>>> depq.addfirst('high')  # Default priority DEPQ.start
>>> depq.addlast('low')  # Default priority DEPQ.start
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
  File "C:\Python34\lib\depq.py", line 308, in addfirst
    raise ValueError('Priority must be >= '
ValueError: Priority must be >= highest priority.
>>>
>>> del depq[0]  # As does del
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Python34\lib\depq.py", line 576, in __delitem__
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
DEPQ([(4, 4), (3, 3), (2, 2), (1, 1), (0, 0)])
>>>
>>> binary_depq = pickle.dumps(depq)
>>> print(fill(str(binary_depq), 77))
b'\x80\x03cdepq\nDEPQ\nq\x00)\x81q\x01}q\x02(X\x05\x00\x00\x00itemsq\x03}q\x0
4(X\x03\x00\x00\x00[1]q\x05K\x01X\x03\x00\x00\x00[3]q\x06K\x01X\x03\x00\x00\x
00[2]q\x07K\x01X\x03\x00\x00\x00[4]q\x08K\x01X\x03\x00\x00\x00[0]q\tK\x01uX\x
04\x00\x00\x00dataq\nccollections\ndeque\nq\x0b]q\x0c(]q\rK\x04aK\x04\x86q\x0
e]q\x0fK\x03aK\x03\x86q\x10]q\x11K\x02aK\x02\x86q\x12]q\x13K\x01aK\x01\x86q\x
14]q\x15K\x00aK\x00\x86q\x16e\x85q\x17Rq\x18X\x05\x00\x00\x00startq\x19K\x00u
b.'
>>>
>>> json_depq = json.dumps(depq.to_json())
>>> print(fill(json_depq, 77))
{"items": {"[1]": 1, "[3]": 1, "[2]": 1, "[4]": 1, "[0]": 1}, "data": [[[4],
4], [[3], 3], [[2], 2], [[1], 1], [[0], 0]], "start": 0}
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
  occur in constant time.
