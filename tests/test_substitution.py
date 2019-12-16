# vim: ts=4 sw=0 sts=-1 et ai tw=80

"""
Unit tests for substitution.py
"""

import unittest

from autoperm.substitution import substitution
from autoperm.perm import Perm


class TestSubstitution(unittest.TestCase):
    def test_substitution(self):
        self.assertEqual("".join(substitution.func("", Perm())), "")
        self.assertEqual(
                "".join(substitution.func("ABC", Perm.from_cycle("AB"))),
                "BAC")
        self.assertEqual(
                "".join(substitution.func("ABCBD", Perm.from_cycle("AB"))),
                "BACAD")
        self.assertEqual(
                "".join(substitution.func("ABCBD", Perm.from_cycle("CD"))),
                "ABDBC")
