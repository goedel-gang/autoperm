"""
Early beta release of hill climbing attack on simple substitution ciphers
"""

# TODO: write this all more generally probably. Currently more of a proof of
#       concept than anything else

import string
import itertools
import math
import sys
import random

import abc

from perm import Perm
from substitution import substitution
from quadgram_metric import quadgram_score

MOD_PERMUTATIONS = [Perm.from_cycle(transp)
        for transp in itertools.combinations(string.ascii_uppercase, 2)]
UPDATE_INTERVAL = 1000

class HillClimber(abc.ABC):
    """
    Class keeping track of the various bits of state needed to climb hills
    """
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
        iterations = 0
        while True:
            if self.hill_climb_iteration():
                iterations += 1
                print("iteration {}, score {:.0f}".format(iterations,
                                                          self.best_score))
                self.format_state()
            else:
                break
        print("optimum reached, score {:.0f}".format(self.best_score))
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
    def initialise_state(self):
        self.key = Perm.random(string.ascii_uppercase)

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
    from autoperm import permutation_from_key
    from util import strip_punc
    plaintext = "".join(strip_punc(BEE_MOVIE))
    key = permutation_from_key("linustorvalds")
    ciphertext = "".join(substitution.func(plaintext, key))
    print("ciphertext: {}".format(ciphertext))
    hill_climber = SubstitutionHillClimber(ciphertext, 1)
    hill_climber.hill_climb()
