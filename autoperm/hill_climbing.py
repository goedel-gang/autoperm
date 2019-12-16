# vim: ts=4 sw=0 sts=-1 et ai tw=80

"""
Early beta release of hill climbing attack on simple substitution ciphers
"""

import string
import itertools
import math
import sys
import random
import time
import collections

import abc

from perm import Perm
from substitution import substitution
from quadgram_metric import quadgram_score
from metric import ENGLISH_FREQUENCIES

MOD_PERMUTATIONS = [Perm.from_cycle(transp)
        for transp in itertools.combinations(string.ascii_uppercase, 2)]


class HillClimber(abc.ABC):
    """
    Class keeping track of the various bits of state needed to climb hills
    """
    __slots__ = "text", "best_score", "total_keys_tried", "update_interval"

    def __init__(self, text, update_interval=1000):
        self.text = text
        self.initialise_state()
        self.best_score = self.get_score(self.get_state())
        self.total_keys_tried = 0
        self.update_interval = update_interval

    @abc.abstractmethod
    def initialise_state(self): ...
    @abc.abstractmethod
    def set_state(self, state): ...
    @abc.abstractmethod
    def get_state(self): ...
    @abc.abstractmethod
    def format_state(self): ...
    @abc.abstractmethod
    def modify_state(self): ...
    @abc.abstractmethod
    def get_score(self, state): ...

    def hill_climb(self):
        start_time = time.time()
        iterations = 0
        while self.hill_climb_iteration():
            iterations += 1
            print("iteration {}, score {:.0f}".format(iterations,
                                                      self.best_score))
            self.format_state()
        end_time = time.time()
        print("optimum reached, score {:.0f}".format(self.best_score))
        print("average {:.1f} keys / s".format(
                self.total_keys_tried / (end_time - start_time)))
        self.format_state()

    def hill_climb_iteration(self):
        for modified_state in self.modify_state():
            self.total_keys_tried += 1
            if self.total_keys_tried % self.update_interval == 0:
                print("\rtried {} keys".format(self.total_keys_tried),
                      end="", file=sys.stderr)
            # no walrus for compatibility
            score = self.get_score(modified_state)
            if score < self.best_score:
                self.set_state(modified_state)
                self.best_score = score
                print("\n", end="", file=sys.stderr)
                return True
        else:
            print("\n", end="", file=sys.stderr)
            return False


class SubstitutionHillClimber(HillClimber):
    __slots__ = "key",

    def initialise_state(self):
        frequencies = collections.Counter(self.text)
        self.key = Perm({a: b for (a, _), (b, _) in
                zip(frequencies.most_common(),
                    collections.Counter(ENGLISH_FREQUENCIES).most_common())})

    def format_state(self):
        print("key:\n{}".format(self.key.inverse().table_format()))
        print("plaintext:\n{}...".format(
                "".join(substitution.func(self.text, self.key))
                    [:1000]))

    def modify_state(self):
        # try a random permutation to see if it sticks
        yield Perm.random(string.ascii_uppercase)
        # try all other permutations, randomly ordered. The shuffling here
        # doesn't take place in a bottleneck, and it hopefully prevents the
        # search path from becoming too homogeneous.
        yield from (self.key * p for p in
                random.sample(MOD_PERMUTATIONS, k=len(MOD_PERMUTATIONS)))

    def get_score(self, state):
        return quadgram_score.no_strip(substitution.func(self.text, state))

    def set_state(self, state):
        self.key = state

    def get_state(self):
        return self.key


if __name__ == "__main__":
    from metric import BEE_MOVIE
    from util import permutation_from_key, strip_punc, file_chars
    if sys.stdin.isatty():
        plaintext = "".join(strip_punc(BEE_MOVIE))
        key = permutation_from_key("linustorvalds")
        ciphertext = "".join(substitution.func(plaintext, key))
    else:
        ciphertext = "".join(strip_punc(file_chars(sys.stdin)))
    hill_climber = SubstitutionHillClimber(ciphertext, 1)
    hill_climber.hill_climb()
