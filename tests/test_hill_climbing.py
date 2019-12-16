# vim: ts=4 sw=0 sts=-1 et ai tw=80

"""
Unit tests for hill_climbing.py

It's kind of hard to write unit tests for such numerical, computational, and
somewhat stochastic code (especially when it's unfinished).
"""

import unittest

from autoperm.hill_climbing import SubstitutionHillClimber
