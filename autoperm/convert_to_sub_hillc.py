"""
Apply hill climbing to an autoperm-enciphered ciphertext to try and make it
resemble a regular substitution cipher. This is done by...
"""

import string
import itertools
import random

from hill_climbing import HillClimber, MOD_PERMUTATIONS, SubstitutionHillClimber
from metric import blind_frequency_fit
from perm import Perm
from util import chunk


class InitSubConvHillClimber(HillClimber):
    def initialise_state(self):
        # TODO: reduce code duplication
        self.key = Perm.random(string.ascii_uppercase)

    def format_state(self):
        print("key: {}".format(self.key))
        print("text: {}".format("".join(
                itertools.chain.from_iterable(
                    (a, self.key[b]) if b else (a,)
                        for a, b in chunk(self.text, 2, "")))))

    # TODO: reduce code duplication
    def modify_state(self):
        yield from (self.key * p for p in
                random.sample(MOD_PERMUTATIONS, k=len(MOD_PERMUTATIONS)))

    def get_score(self, state):
        return blind_frequency_fit.no_strip(
                itertools.chain.from_iterable(
                    (a, state[b]) if b else (a,)
                        for a, b in chunk(self.text, 2, "")))

    def set_state(self, state):
        self.key = state

    def get_state(self):
        return self.key


class BigSubConvHillClimber(HillClimber):
    def initialise_state(self):
        init_climber = InitSubConvHillClimber(self.text)
        self.key, _ = init_climber.hill_climb()

    def format_state(self):
        print("key:\n{}".format(self.key))
        print("text: {}".format(
                "".join(itertools.chain.from_iterable(
                    (a, self.key[b]) if b else (a,)
                        for a, b in chunk(self.text, 2, "")))))

    def get_score(self, state):
        sub_climber = SubstitutionHillClimber(
                "".join(itertools.chain.from_iterable(
                    (a, state[b]) if b else (a,)
                        for a, b in chunk(self.text, 2, ""))))
        return sub_climber.hill_climb()[1]

    def set_state(self, state):
        self.key = state

    def get_state(self):
        return self.key

    # TODO: reduce code duplication
    def modify_state(self):
        yield from (self.key * p for p in
                random.sample(MOD_PERMUTATIONS, k=len(MOD_PERMUTATIONS)))


if __name__ == "__main__":
    import sys
    from util import strip_punc, file_chars
    if sys.stdin.isatty():
        print("nah")
    else:
        ciphertext = "".join(strip_punc(file_chars(sys.stdin)))
        climber = BigSubConvHillClimber(ciphertext)
        climber.hill_climb()
