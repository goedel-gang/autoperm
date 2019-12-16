# vim: ts=4 sw=0 sts=-1 et ai tw=80

"""
Utilities for use throughout. Mostly to do with stripping text and reading
files.
"""

import string
import collections

# I think it's fine to import from perm because perm is a very stand-alone sort
# of module
from perm import Perm

def file_chars(file):
    """
    Generate the characters in a file one by one.

    This just reads the file into memory. It's not worth doing anything stupid
    with iterators because we're dealing with tiny tiny files.
    """
    return file.read()


# TODO: try to do something with stripping accents from Unicode characters with
#       unicodedata. Basically the mixing and matching of str.isalphas and
#       str.uppers means that because Python is very good at
#       internationalisation, if you have plaintext or keys with wéïrd unicode
#       characters in, things will probably break.
#
#       An improvement for now would be to just re-write this explicitly talking
#       about ASCII characters a-z and A-Z.
def strip_punc(gen):
    """
    Remove all but the letters and make them uppercase
    """
    return map(str.upper, filter(str.isalpha, gen))


def permutation_from_key(key):
    """
    Generate a low-level permutation from a key consisting of letters, by
    removing repeated letters and filling in the rest of the alphabet going from
    the last letter. Eg "linustorvalds" as key becomes
    ABCDEFGHIJKLMNOPQRSTUVWXYZ
    LINUSTORVADEFGHJKMPQWXYZBC
    This method is /not/ completely standard. Wikipedia would have you believe
    that you should just chug along with the rest of the alphabet from the first
    letter, but this bleeds huge amounts of information into your permutation,
    as xyz will often map to xyz, whereas here they're basically randomly
    offset. (Wikipedia's example sneakily has a z in the key so you don't notice
    this)

    This function generously strips any punctuation and makes the string
    uppercase, so should be fairly robust on any input.
    """
    mapping = {}
    alphabet = set(string.ascii_uppercase)
    from_iterable = iter(string.ascii_uppercase)
    # use an OrderedDict so as to retain compatibility with 3.6 spec
    key_unique = "".join(collections.OrderedDict.fromkeys(strip_punc(key)))
    # in case of empty key (although that's not a good idea)
    k = 'A'
    for k, a in zip(key_unique, from_iterable):
        mapping[a] = k
        alphabet.remove(k)
    alphabet = sorted(alphabet)
    start_index = 0
    while start_index < len(alphabet) and alphabet[start_index] < k:
        start_index += 1
    for ind, k in enumerate(from_iterable):
        mapping[k] = alphabet[(start_index + ind) % len(alphabet)]
    return Perm(mapping)
