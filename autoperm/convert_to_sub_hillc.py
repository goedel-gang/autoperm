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
from substitution import substitution


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


class ImpatientSubClimber(SubstitutionHillClimber):
    def modify_state(self):
        yield from (self.key * p for p in
                random.sample(MOD_PERMUTATIONS, k=len(MOD_PERMUTATIONS) // 1))


class BigSubConvHillClimber(HillClimber):
    def initialise_state(self):
        print("Running initial climber to optimise blind frequency...")
        init_climber = InitSubConvHillClimber(self.text)
        self.key, _ = init_climber.hill_climb(verbose=False)
        print("Done.")

    # TODO: this is perhaps the most duplicitous code ever written
    def format_state(self):
        print("outer s-t diff key:\n{}".format(self.key.table_format()))
        sub_climber = ImpatientSubClimber(
                "".join(itertools.chain.from_iterable(
                    (a, self.key[b]) if b else (a,)
                        for a, b in chunk(self.text, 2, ""))))
        sigma, score = sub_climber.hill_climb(verbose=False)
        print("inner sub key (sigma):\n{}".format(sigma.table_format()))
        # idk if this is actually right, it's a napkin sitch
        print("implied tau:\n{}".format((self.key.inverse() * sigma)
                .table_format()))
        print("score: {}".format(score))
        print("text: {}".format("".join(substitution.func(
                "".join(itertools.chain.from_iterable(
                    (a, self.key[b]) if b else (a,)
                        for a, b in chunk(self.text, 2, ""))),
                sigma.inverse()))[:1000]))

    def get_score(self, state):
        sub_climber = ImpatientSubClimber(
                "".join(itertools.chain.from_iterable(
                    (a, state[b]) if b else (a,)
                        for a, b in chunk(self.text, 2, ""))))
        return sub_climber.hill_climb(verbose=False)[1]

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
        climber = BigSubConvHillClimber(ciphertext, 1)
        climber.hill_climb()
