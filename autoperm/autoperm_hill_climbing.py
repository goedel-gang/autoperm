# vim: ts=4 sw=0 sts=-1 et ai tw=80

import string
import random

from hill_climbing import HillClimber, MOD_PERMUTATIONS
from autoperm import autoperm_encipher, autoperm_decipher
from quadgram_metric import quadgram_score
from perm import Perm


class AutopermHillClimber(HillClimber):
    __slots__ = "sigma", "tau"
    def initialise_state(self):
        self.sigma = Perm.random(string.ascii_uppercase)
        self.tau = Perm.random(string.ascii_uppercase)

    def format_state(self):
        print("sigma:\n{}\ntau:\n{}".format(
                self.sigma.table_format(),
                self.tau.table_format()))
        print("plaintext:\n{}...".format(
                "".join(autoperm_decipher.func(self.text, self.sigma, self.tau))
                    [:1000]))

    def modify_state(self):
        # try a random state
        yield tuple(Perm.random(string.ascii_uppercase) for _ in range(2))
        # try modifying just one of sigma or tau
        yield from ((self.sigma * p, self.tau) for p in
                random.sample(MOD_PERMUTATIONS, k=len(MOD_PERMUTATIONS)))
        yield from ((self.sigma, self.tau * p) for p in
                random.sample(MOD_PERMUTATIONS, k=len(MOD_PERMUTATIONS)))

    def get_score(self, state):
        return quadgram_score.no_strip(
                autoperm_decipher.func(self.text, *state))

    def set_state(self, state):
        self.sigma, self.tau = state

    def get_state(self):
        return self.sigma, self.tau


if __name__ == "__main__":
    from metric import BEE_MOVIE
    from util import permutation_from_key, strip_punc
    plaintext = "".join(strip_punc(BEE_MOVIE))
    sigma = permutation_from_key("richardstallman")
    tau = permutation_from_key("linustorvalds")
    ciphertext = "".join(autoperm_encipher.func(plaintext, sigma, tau))
    print("ciphertext: {}".format(ciphertext))
    hill_climber = AutopermHillClimber(ciphertext, 1)
    hill_climber.hill_climb()
