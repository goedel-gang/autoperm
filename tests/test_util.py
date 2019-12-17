# vim: ts=4 sw=0 sts=-1 et ai tw=80

"""
Unit tests for util.py
"""

import unittest

import io
import string
import random

from autoperm.perm import Perm
from autoperm.util import file_chars, strip_punc, permutation_from_key, chunk


class TestUtil(unittest.TestCase):
    def setUp(self):
        self.strings = [
                ("", ""),
                ("ABC", "ABC"),
                ("abc", "ABC"),
                ("aBc", "ABC"),
                (",A987B^&*C*", "ABC")]

    def test_chunk(self):
        self.assertEqual(list(chunk([], 1)), [])
        self.assertEqual(list(chunk([], 2)), [])
        self.assertEqual(list(chunk(range(4), 2)),
                         [(0, 1), (2, 3)])
        self.assertEqual(list(chunk(range(4), 3)),
                         [(0, 1, 2), (3, None, None)])
        self.assertEqual(list(chunk(range(4), 3, 4)),
                         [(0, 1, 2), (3, 4, 4)])

    def test_file_chars(self):
        for input_text, _ in self.strings:
            self.assertEqual("".join(file_chars(io.StringIO(input_text))),
                             input_text)

    def test_strip_punc(self):
        for input_text, result in self.strings:
            self.assertEqual("".join(strip_punc(input_text)), result)

    def test_permutation_from_key(self):
        self.assertEqual(Perm(), permutation_from_key(""))
        self.assertEqual(Perm(), permutation_from_key("a"))
        self.assertEqual(Perm(), permutation_from_key("A"))
        self.assertEqual(Perm(), permutation_from_key("?a?"))
        self.assertEqual(Perm(), permutation_from_key("!!"))
        for ind, l in enumerate(string.ascii_uppercase):
            self.assertEqual(Perm.from_cycle(string.ascii_uppercase) ** ind,
                             permutation_from_key(l))
        self.assertEqual(Perm(dict(zip(string.ascii_uppercase,
                                       "LINUSTORVADEFGHJKMPQWXYZBC"))),
                         permutation_from_key("linustorvalds"))
        self.assertEqual(Perm(dict(zip(string.ascii_uppercase,
                                       "LINUSTORVADEFGHJKMPQWXYZBC"))),
                         permutation_from_key("linuStOrvALds"))
        self.assertEqual(Perm(dict(zip(string.ascii_uppercase,
                                       "LINUSTORVADEFGHJKMPQWXYZBC"))),
                         permutation_from_key("  lin\nuStO&&(*rvA)*)(*Lds"))
        self.assertEqual(Perm(dict(zip(string.ascii_uppercase,
                                       "RICHADSTLMNOPQUVWXYZBEFGJK"))),
                         permutation_from_key("richardstallman"))
        self.assertEqual(Perm(dict(zip(string.ascii_uppercase,
                                       "ZEBRACDFGHIJKLMNOPQSTUVWXY"))),
                         permutation_from_key("zebra"))
        for _ in range(100):
            key = "".join(random.choices(string.ascii_uppercase,
                                         k=random.randrange(30)))
            self.assertTrue(permutation_from_key(key).is_permutation())


if __name__ == "__main__":
    unittest.main()
