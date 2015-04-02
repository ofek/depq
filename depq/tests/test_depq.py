import unittest
import pickle
import json
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


class HelperOrderedTest(unittest.TestCase):
    def test_correct_order_is_true(self):
        tuple_list = [(None, 3), (None, 2)]
        self.assertEqual(is_ordered(tuple_list), True)

    def test_incorrect_order_is_false(self):
        tuple_list = [(None, 3), (None, 5)]
        self.assertEqual(is_ordered(tuple_list), False)

    def test_empty_is_true(self):
        tuple_list = []
        self.assertEqual(is_ordered(tuple_list), True)


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

    def test_count_unset_with_hashable(self):
        self.assertEqual(self.depq.count('test'), 0)

    def test_count_unset_with_unhashable(self):
        self.assertEqual(self.depq.count(['test']), 0)

    def test_in_operator_unset_hashable(self):
        self.assertEqual('test' in self.depq, False)

    def test_in_operator_unset_unhashable(self):
        self.assertEqual(['test'] in self.depq, False)

    def test_insert_initial_membership_new_hashable_with_in_operator(self):
        self.depq.insert('test', 7)
        self.assertEqual('test' in self.depq, True)

    def test_insert_initial_membership_new_unhashable_with_in_operator(self):
        self.depq.insert(['test'], 7)
        self.assertEqual(['test'] in self.depq, True)

    def test_insert_mass_membership_new_hashable_with_in_operator(self):
        self.depq.insert('test1', 7)
        self.depq.insert('test2', 5)
        self.assertEqual('test2' in self.depq, True)

    def test_insert_mass_membership_new_unhashable_with_in_operator(self):
        self.depq.insert('test1', 7)
        self.depq.insert(['test2'], 5)
        self.assertEqual(['test2'] in self.depq, True)

    def test_insert_mass_membership_add_hashable_with_count(self):
        self.depq.insert('test', 7)
        self.depq.insert('test', 5)
        self.assertEqual(self.depq.count('test'), 2)

    def test_insert_mass_membership_add_unhashable_with_count(self):
        self.depq.insert(['test'], 7)
        self.depq.insert(['test'], 5)
        self.assertEqual(self.depq.count(['test']), 2)

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

    def test_insert_mass_populate_order(self):
        for i in range(self.random.randrange(20, 100)):
            self.depq.insert(None, self.random.randrange(-1000, 1000))
        self.assertEqual(is_ordered(self.depq), True)

    def test__repr__empty(self):
        self.assertEqual(repr(self.depq), "DEPQ([])")

    def test__repr__one_item(self):
        self.depq.insert(None, 5)
        self.assertEqual(repr(self.depq), "DEPQ([(None, 5)])")

    def test__repr__multiple_items(self):
        self.depq.insert(None, 5)
        self.depq.insert('test', 3)
        self.assertEqual(repr(self.depq), "DEPQ([(None, 5), ('test', 3)])")

    def test__str__and__unicode__empty(self):
        self.assertEqual(str(self.depq), "DEPQ([])")
        self.assertEqual(str(self.depq), self.depq.__unicode__())

    def test__str__and__unicode__one_item(self):
        self.depq.insert(None, 5)
        self.assertEqual(str(self.depq), "DEPQ([(None, 5)])")
        self.assertEqual(str(self.depq), self.depq.__unicode__())

    def test__str__and__unicode__multiple_items(self):
        self.depq.insert(None, 5)
        self.depq.insert('test', 3)
        self.assertEqual(str(self.depq), "DEPQ([(None, 5), ('test', 3)])")
        self.assertEqual(str(self.depq), self.depq.__unicode__())

    def test__setitem__calls_insert(self):
        self.depq[None] = 5
        self.assertEqual(None in self.depq, True)

    def test__delitem__raise_error(self):
        self.depq.insert(None, 5)
        with self.assertRaises(NotImplementedError):
            del self.depq[0]

    def test__getitem__empty_raise_error(self):
        with self.assertRaises(IndexError):
            self.depq[0] += 1

    def test__getitem__with_items(self):
        self.depq.insert('last', 1)
        self.depq.insert('first', 7)
        self.depq.insert('middle', 5)
        self.assertEqual(self.depq[0], ('first', 7))
        self.assertEqual(self.depq[1], ('middle', 5))
        self.assertEqual(self.depq[2], ('last', 1))
        self.assertEqual(self.depq[-1], ('last', 1))

    def test_first_and_last_empty_raise_error(self):
        with self.assertRaises(IndexError):
            self.depq.first()
        with self.assertRaises(IndexError):
            self.depq.last()

    def test_first_and_last_one_item(self):
        self.depq.insert(None, 1)
        self.assertEqual(self.depq.first(), None)
        self.assertEqual(self.depq.first(), self.depq.last())

    def test_first_and_last_multiple_items(self):
        self.depq.insert('last', 1)
        self.depq.insert('first', 5)
        self.assertEqual(self.depq.first(), 'first')
        self.assertEqual(self.depq.last(), 'last')

    def test_high_and_low_empty_raise_error(self):
        with self.assertRaises(IndexError):
            self.depq.high()
        with self.assertRaises(IndexError):
            self.depq.low()

    def test_high_and_low_one_item(self):
        self.depq.insert(None, 1)
        self.assertEqual(self.depq.high(), 1)
        self.assertEqual(self.depq.high(), self.depq.low())

    def test_high_and_low_multiple_items(self):
        self.depq.insert(None, 1)
        self.depq.insert(None, 5)
        self.assertEqual(self.depq.high(), 5)
        self.assertEqual(self.depq.low(), 1)

    def test_size_and_len(self):
        self.assertEqual(len(self.depq), 0)
        self.assertEqual(len(self.depq), self.depq.size())
        self.depq.insert(None, 5)
        self.assertEqual(len(self.depq), 1)
        self.assertEqual(len(self.depq), self.depq.size())

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

    def test_addfirst_membership_new_hashable(self):
        self.depq.addfirst('test')
        self.assertEqual(self.depq.count('test'), 1)

    def test_addfirst_membership_new_unhashable(self):
        self.depq.addfirst(['test'])
        self.assertEqual(self.depq.count(['test']), 1)

    def test_addfirst_membership_add_hashable(self):
        self.depq.addfirst('test')
        self.depq.addfirst('test')
        self.assertEqual(self.depq.count('test'), 2)

    def test_addfirst_membership_add_unhashable(self):
        self.depq.addfirst(['test'])
        self.depq.addfirst(['test'])
        self.assertEqual(self.depq.count(['test']), 2)

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

    def test_addlast_membership_new_hashable(self):
        self.depq.addlast('test')
        self.assertEqual(self.depq.count('test'), 1)

    def test_addlast_membership_new_unhashable(self):
        self.depq.addlast(['test'])
        self.assertEqual(self.depq.count(['test']), 1)

    def test_addlast_membership_add_hashable(self):
        self.depq.addlast('test')
        self.depq.addfirst('test')
        self.assertEqual(self.depq.count('test'), 2)

    def test_addlast_membership_add_unhashable(self):
        self.depq.addlast(['test'])
        self.depq.addfirst(['test'])
        self.assertEqual(self.depq.count(['test']), 2)

    def test_popfirst_empty_raise_error(self):
        with self.assertRaises(IndexError):
            self.depq.popfirst()

    def test_popfirst_membership_remove_hashable(self):
        self.depq.insert('test', 5)
        self.depq.popfirst()
        self.assertEqual(self.depq.count('test'), 0)

    def test_popfirst_membership_remove_unhashable(self):
        self.depq.insert(['test'], 5)
        self.depq.popfirst()
        self.assertEqual(self.depq.count(['test']), 0)

    def test_popfirst_membership_decrement_hashable(self):
        self.depq.insert('test', 5)
        self.depq.insert('test', 7)
        self.depq.popfirst()
        self.assertEqual(self.depq.count('test'), 1)

    def test_popfirst_membership_decrement_unhashable(self):
        self.depq.insert(['test'], 5)
        self.depq.insert(['test'], 7)
        self.depq.popfirst()
        self.assertEqual(self.depq.count(['test']), 1)

    def test_popfirst_order(self):
        for i in range(5):
            self.depq.insert('test', i)
        self.depq.popfirst()
        self.assertEqual(self.depq.high(), 3)

    def test_poplast_empty_raise_error(self):
        with self.assertRaises(IndexError):
            self.depq.poplast()

    def test_poplast_membership_remove_hashable(self):
        self.depq.insert('test', 5)
        self.depq.poplast()
        self.assertEqual(self.depq.count('test'), 0)

    def test_poplast_membership_remove_unhashable(self):
        self.depq.insert(['test'], 5)
        self.depq.poplast()
        self.assertEqual(self.depq.count(['test']), 0)

    def test_poplast_membership_decrement_hashable(self):
        self.depq.insert('test', 5)
        self.depq.insert('test', 7)
        self.depq.poplast()
        self.assertEqual(self.depq.count('test'), 1)

    def test_poplast_membership_decrement_unhashable(self):
        self.depq.insert(['test'], 5)
        self.depq.insert(['test'], 7)
        self.depq.poplast()
        self.assertEqual(self.depq.count(['test']), 1)

    def test_poplast_order(self):
        for i in range(5):
            self.depq.insert('test', i)
        self.depq.poplast()
        self.assertEqual(self.depq.low(), 1)

    def test_remove_invalid_count_raise_error(self):
        with self.assertRaises(ValueError):
            self.depq.remove('test', 'test')
        with self.assertRaises(TypeError):
            self.depq.remove('test', [])

    def test_remove_unset_hashable(self):
        self.assertEqual(self.depq.remove('test'), [])

    def test_remove_unset_unhashable(self):
        self.assertEqual(self.depq.remove(['test']), [])

    def test_remove_zero_does_nothing(self):
        self.depq.insert('test', 5)
        self.assertEqual(self.depq.remove('test', 0), [])
        self.assertEqual(self.depq.count('test'), 1)

    def test_remove_default_membership_remove_hashable(self):
        self.depq.insert('test', 5)
        self.depq.remove('test')
        self.assertEqual(self.depq.count('test'), 0)

    def test_remove_default_membership_remove_unhashable(self):
        self.depq.insert(['test'], 5)
        self.depq.remove(['test'])
        self.assertEqual(self.depq.count(['test']), 0)

    def test_remove_default_membership_decrement_hashable(self):
        self.depq.insert('test', 5)
        self.depq.insert('test', 7)
        self.depq.remove('test')
        self.assertEqual(self.depq.count('test'), 1)

    def test_remove_default_membership_decrement_unhashable(self):
        self.depq.insert(['test'], 5)
        self.depq.insert(['test'], 7)
        self.depq.remove(['test'])
        self.assertEqual(self.depq.count(['test']), 1)

    def test_remove_inbound_arg_membership_remove_hashable(self):
        self.depq.insert('test', 5)
        self.depq.insert('test', 7)
        self.depq.remove('test', 2)
        self.assertEqual(self.depq.count('test'), 0)

    def test_remove_inbound_arg_membership_remove_unhashable(self):
        self.depq.insert(['test'], 5)
        self.depq.insert(['test'], 7)
        self.depq.remove(['test'], 2)
        self.assertEqual(self.depq.count(['test']), 0)

    def test_remove_outbound_arg_membership_remove_hashable(self):
        self.depq.insert('test', 5)
        self.depq.insert('test', 7)
        self.depq.remove('test', 100)
        self.assertEqual(self.depq.count('test'), 0)

    def test_remove_outbound_arg_membership_remove_unhashable(self):
        self.depq.insert(['test'], 5)
        self.depq.insert(['test'], 7)
        self.depq.remove(['test'], 100)
        self.assertEqual(self.depq.count(['test']), 0)

    def test_remove_inbound_arg_membership_decrement_hashable(self):
        self.depq.insert('test', 5)
        self.depq.insert('test', 7)
        self.depq.insert('test', 3)
        self.depq.remove('test', 2)
        self.assertEqual(self.depq.count('test'), 1)

    def test_remove_inbound_arg_membership_decrement_unhashable(self):
        self.depq.insert(['test'], 5)
        self.depq.insert(['test'], 7)
        self.depq.insert(['test'], 3)
        self.depq.remove(['test'], 2)
        self.assertEqual(self.depq.count(['test']), 1)

    def test_remove_membership_with_elim(self):
        self.depq.insert('test', 5)
        self.depq.insert('test', 7)
        self.depq.elim('test')
        self.assertEqual(self.depq.count('test'), 0)

    def test_remove_order(self):
        self.depq.insert('test', 5)
        self.depq.insert('test', 7)
        self.depq.insert('test', 3)
        self.depq.insert('test', 1)
        self.depq.remove('test', 2)
        self.assertEqual(self.depq.low(), 5)
        self.assertEqual(is_ordered(self.depq), True)

    def test_pickle(self):
        for i in range(5):
            self.depq.insert([i], i)
        binary_depq = pickle.dumps(self.depq)
        depq_from_pickle = pickle.loads(binary_depq)
        self.assertEqual(self.depq.data, depq_from_pickle.data)
        self.assertEqual(self.depq.items, depq_from_pickle.items)
        self.assertEqual(type(depq_from_pickle.lock).__name__, 'lock')

    def test_json(self):
        for i in range(5):
            self.depq.insert([i], i)
        json_depq = json.dumps(self.depq.to_json())
        depq_from_json = DEPQ.from_json(json_depq)
        self.assertEqual(self.depq.data, depq_from_json.data)
        self.assertEqual(self.depq.items, depq_from_json.items)
        self.assertEqual(type(depq_from_json.lock).__name__, 'lock')

if __name__ == '__main__':
    unittest.main()
