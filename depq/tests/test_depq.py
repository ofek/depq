import unittest
from depq import DEPQ


def is_ordered(d):
    try:
        for i in range(len(d)):
            if d.popfirst()[1] < d[0][1]:
                return False
    except IndexError:
        return True
    finally:
        return True


