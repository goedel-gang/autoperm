# vim: ts=4 sw=0 sts=-1 et ai tw=80

"""
Unit test for top-level functions in autoperm.py
"""

import unittest

import string
import random
import os
import io

from pathlib import Path

from autoperm.perm import Perm
from autoperm.autoperm import autoperm_encipher, autoperm_decipher
from autoperm.util import permutation_from_key

TEXTS_DIR = Path(__file__).parent / ".." / "texts"


class TestAutoPerm(unittest.TestCase):
    def test_autoperm_encipher(self):
        sigma = Perm.from_cycle("ABCD")
        tau = Perm.from_cycle("AB") * Perm.from_cycle("CD")
        self.assertEqual(list(autoperm_encipher.func("ABCDAB", sigma, tau)),
                         list("BADCCB"))
        self.assertEqual(list(autoperm_encipher.func("ABCDA", sigma, tau)),
                         list("BADCC"))
        self.assertEqual(list(autoperm_encipher.func("", sigma, tau)), [])
        self.assertEqual(list(autoperm_encipher.func("A", sigma, tau)), ["B"])

    def test_autoperm_decipher(self):
        sigma = Perm.from_cycle("ABCD")
        tau = Perm.from_cycle("AB") * Perm.from_cycle("CD")
        self.assertEqual(list(autoperm_decipher.func("BADCCB", sigma, tau)),
                         list("ABCDAB"))
        self.assertEqual(list(autoperm_decipher.func("BADCC", sigma, tau)),
                         list("ABCDA"))
        self.assertEqual(list(autoperm_decipher.func("", sigma, tau)), [])
        self.assertEqual(list(autoperm_decipher.func("B", sigma, tau)), ["A"])

    # this tests integrated functionality of the whole module. Probably doesn't
    # belong in a unit test suite, but oh well.
    #
    # It functions by making sure that any files in the directory of sample
    # texts don't change when encrypted and decrypted again.
    def test_integration(self):
        found_files = False
        for file_entry in os.scandir(TEXTS_DIR):
            sigma = permutation_from_key(random.choices(string.ascii_uppercase,
                                                        k=random.randrange(30)))
            tau = permutation_from_key(random.choices(string.ascii_uppercase,
                                                      k=random.randrange(30)))
            if not file_entry.is_file():
                continue
            try:
                with open(file_entry.path, "r") as data_file:
                    data = data_file.read()
            # this is everything that I've currently thought of that could go
            # wrong - probably not exhaustive
            except (UnicodeDecodeError, PermissionError):
                continue
            plaintext = io.StringIO(data)
            ciphertext = io.StringIO()
            decrypted_plaintext = io.StringIO()
            autoperm_encipher.preserve(plaintext, ciphertext, sigma, tau)
            ciphertext = io.StringIO(ciphertext.getvalue())
            autoperm_decipher.preserve(ciphertext, decrypted_plaintext,
                                       sigma, tau)
            self.assertEqual(decrypted_plaintext.getvalue(), data)
            found_files = True
        if not found_files:
            raise ValueError("test_integration did not find any files to read")


if __name__ == "__main__":
    unittest.main()
