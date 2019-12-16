# vim: ts=4 sw=0 sts=-1 et ai tw=80

"""
Unit tests for quadgram_metric.py
"""

import unittest

from autoperm.quadgram_metric import (
        rolling_slice, get_quadgram_score, letters_to_integers, quadgram_score)


class TestQuadgramMetric(unittest.TestCase):
    def test_rolling_slice(self):
        self.assertEqual(list(map(list, rolling_slice([], 1))), [])
        self.assertEqual(list(map(list, rolling_slice([], 2))), [])
        self.assertEqual(list(map(list, rolling_slice([], 3))), [])
        self.assertEqual(list(map(list, rolling_slice([1], 2))), [])
        self.assertEqual(list(map(list, rolling_slice([1], 3))), [])
        self.assertEqual(list(map(list, rolling_slice([1], 1))), [[1]])
        self.assertEqual(list(map(list, rolling_slice([1, 2], 1))), [[1], [2]])
        self.assertEqual(list(map(list, rolling_slice([1, 2], 2))), [[1, 2]])
        self.assertEqual(list(map(list, rolling_slice([1, 2], 3))), [])
        self.assertEqual(list(map(list, rolling_slice([1, 2, 3], 3))),
                         [[1, 2, 3]])
        self.assertEqual(list(map(list, rolling_slice([1, 2, 3], 2))),
                         [[1, 2], [2, 3]])
        self.assertEqual(list(map(list, rolling_slice([1, 2, 3, 4], 2))),
                         [[1, 2], [2, 3], [3, 4]])
        self.assertEqual(list(map(list, rolling_slice([1, 2, 3, 4], 3))),
                         [[1, 2, 3], [2, 3, 4]])

    def test_letters_to_integers(self):
        self.assertEqual(list(letters_to_integers("")), [])
        self.assertEqual(list(letters_to_integers("A")), [0])
        self.assertEqual(list(letters_to_integers("Z")), [25])
        self.assertEqual(list(letters_to_integers("AAAA")), [0, 0, 0, 0])
        self.assertEqual(list(letters_to_integers("ABCD")), [0, 1, 2, 3])
        self.assertEqual(list(letters_to_integers("ZZZZ")), [25] * 4)

    def test_get_quadgram_score(self):
        self.assertAlmostEqual(get_quadgram_score([0, 0, 0, 0]), 6.4268008571)
        self.assertAlmostEqual(get_quadgram_score([0, 0, 0, 1]), 7.02886084843)
        self.assertAlmostEqual(get_quadgram_score([0, 0, 0, 7]), 6.72783085276)
        self.assertAlmostEqual(get_quadgram_score([25] * 4), 7.02886084843)
        self.assertLess(get_quadgram_score(list(letters_to_integers("THET"))),
                        get_quadgram_score(list(letters_to_integers("XZWX"))))

    def test_quadgram_score(self):
        self.assertEqual(quadgram_score(""), 0)
        self.assertEqual(quadgram_score("A"), 0)
        self.assertEqual(quadgram_score("AA"), 0)
        self.assertEqual(quadgram_score("AAA"), 0)
        self.assertEqual(quadgram_score("A??A&*A"), 0)
        self.assertAlmostEqual(quadgram_score("AAAA"), 6.4268008571)
        self.assertAlmostEqual(quadgram_score("AAAAB"),
                               6.4268008571 + 7.02886084843)
