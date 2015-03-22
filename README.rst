# depq - Designed and coded by Ofek Lev ofekmeister@gmail.com

Description:

  - Python implementation of a thread-safe and efficient
    double-ended priority queue (DEPQ) in which items and their
    priority values are stored in a deque object as tuples.
    This can also be used as a regular priority queue, or simply a
    FIFO/LIFO queue.

Features & advantages of this implementation:

  - Completely thread-safe
  - Priority values can be ANY comparable type you choose!
  - popfirst() and poplast() have O(1) performance instead of
    running in logarithmic time like in a standard DEPQ
  - Naturally fast also because deque object is implemented in C
  - Items with equal priorities are sorted in the order they were
    originally added
  - Specific items can be deleted or their priorities changed
  - Ability to get an item's frequency in DEPQ via count(item) in O(1)
  - Membership testing with 'in' operator also occurs in O(1)

Implementation:

  - Priorities are always in proper order, thus, a binary search
    is performed to find the right index with which to insert new
    items when specifying priority. Normally, this would result in
    O(n log n) performance when adding items via insert(item, priority)
    where self.high() > priority > self.low() because deque (as a
    doubly linked list) random access is O(n).

    Though, ACTUALLY I've been able to reduce that to O(n) by modifying
    the binary search to operate while the internal deque is rotating.

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
    occur in constant time.
