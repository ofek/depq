import unittest
from random import SystemRandom
from depq import DEPQ


def is_ordered(d):
    try:
        previous = d[0][1]
        for tup in d:
            if previous < tup[1]:
                return False
            previous = tup[1]
    except IndexError:
        return True
    return True


class DEPQTest(unittest.TestCase):

    def setUp(self):
        self.depq = DEPQ()
        self.random = SystemRandom()

    def tearDown(self):
        self.depq.clear()

    def test_init_default(self):
        self.assertEqual(self.depq.start, 0)

    def test_init_set_start(self):
        depq_non_default = DEPQ(start=5)
        self.assertEqual(depq_non_default.start, 5)

    def test_insert_initial_populate_first(self):
        self.depq.insert(None, 4)
        self.depq.insert(None, 6)
        self.assertEqual(is_ordered(self.depq), True)
        self.depq.insert(None, 5)
        self.assertEqual(is_ordered(self.depq), True)

    def test_insert_initial_populate_last(self):
        self.depq.insert(None, 6)
        self.depq.insert(None, 4)
        self.assertEqual(is_ordered(self.depq), True)
        self.depq.insert(None, 5)
        self.assertEqual(is_ordered(self.depq), True)

    def test_insert_mass_populate(self):
        for i in range(self.random.randrange(20, 100)):
            self.depq.insert(None, self.random.randrange(-1000, 1000))
        self.assertEqual(is_ordered(self.depq), True)

    def test_high_and_low(self):
        self.depq.insert(None, 1)
        self.assertEqual(self.depq.high(), 1)
        self.assertEqual(self.depq.high(), self.depq.low())
        self.depq.insert(None, 5)
        self.assertEqual(self.depq.high(), 5)
        self.assertEqual(self.depq.low(), 1)

    def test_first_and_last(self):
        self.depq.insert('last', 1)
        self.assertEqual(self.depq.first(), 'last')
        self.assertEqual(self.depq.first(), self.depq.last())
        self.depq.insert('first', 5)
        self.assertEqual(self.depq.first(), 'first')
        self.assertEqual(self.depq.last(), 'last')

    def test_size_and_len(self):
        self.assertEqual(len(self.depq), 0)
        self.assertEqual(len(self.depq.items), 0)
        self.depq.insert(None, 5)
        self.assertEqual(self.depq.size(), 1)
        self.assertEqual(len(self.depq.items), 1)

    def test_is_empty(self):
        self.assertEqual(self.depq.is_empty(), True)
        self.depq.insert(None, 5)
        self.assertEqual(self.depq.is_empty(), False)

    def test_clear(self):
        self.depq.insert('last', 1)
        self.assertEqual(self.depq.size(), 1)
        self.assertEqual(len(self.depq.items), 1)
        self.depq.clear()
        self.assertEqual(self.depq.size(), 0)
        self.assertEqual(len(self.depq.items), 0)

    def test_addfirst_populate_default(self):
        for i in range(self.random.randrange(20, 100)):
            self.depq.addfirst(None)
        self.assertEqual(is_ordered(self.depq), True)
        self.assertEqual(self.depq.high(), self.depq.low())

    def test_addfirst_populate_with_arg(self):
        for i in range(self.random.randrange(20, 100)):
            self.depq.addfirst(None, i)
        self.assertEqual(is_ordered(self.depq), True)
        self.assertGreater(self.depq.high(), self.depq.low())

    def test_addfirst_initial_priority(self):
        self.depq.addfirst(None)
        self.assertEqual(self.depq.high(), self.depq.start)

    def test_addfirst_initial_priority_with_arg(self):
        self.depq.addfirst(None, 10)
        self.assertEqual(self.depq.high(), 10)

    def test_addfirst_smaller_priority_raise_error(self):
        self.depq.addfirst(None, 7)
        with self.assertRaises(ValueError):
            self.depq.addfirst(None, 6)

    def test_addlast_populate_default(self):
        for i in range(self.random.randrange(20, 100)):
            self.depq.addlast(None)
        self.assertEqual(is_ordered(self.depq), True)
        self.assertEqual(self.depq.high(), self.depq.low())

    def test_addlast_populate_with_arg(self):
        for i in reversed(range(self.random.randrange(20, 100))):
            self.depq.addlast(None, i)
        self.assertEqual(is_ordered(self.depq), True)
        self.assertGreater(self.depq.high(), self.depq.low())

    def test_addlast_initial_priority(self):
        self.depq.addlast(None)
        self.assertEqual(self.depq.high(), self.depq.start)

    def test_addlast_initial_priority_with_arg(self):
        self.depq.addlast(None, 10)
        self.assertEqual(self.depq.high(), 10)

    def test_addlast_larger_priority_raise_error(self):
        self.depq.addlast(None, 7)
        with self.assertRaises(ValueError):
            self.depq.addlast(None, 8)


if __name__ == '__main__':
    unittest.main()









