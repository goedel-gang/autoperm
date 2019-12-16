# vim: ts=4 sw=0 sts=-1 et ai tw=80

"""
Implementing a substitution cipher
"""

import argparse

from cipher_streamer import CipherStreamer
from util import permutation_from_key


@CipherStreamer
def substitution(text, perm):
    """
    Simple substitution cipher.
    """
    return (perm[c] for c in text)


# TODO: just write a generic CipherStreamer.main method rather than copying all
#       of this code every time
def get_args():
    """
    Parse argv
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "in_file", type=argparse.FileType("r"), default="-", nargs="?",
            help="Input file (plaintext or ciphertext)")
    parser.add_argument(
            "out_file", type=argparse.FileType("w"), default="-", nargs="?",
            help="Output file (plaintext or ciphertext)")
    parser.add_argument(
            "-k", "--key", required=True, help="Encryption key")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
            "-e", "--encrypt", action="store_true",
            help="Perform encryption")
    action.add_argument(
            "-d", "--decrypt", action="store_true",
            help="Perform decryption")
    return parser.parse_args()


def main(args):
    """
    Main function
    """
    key = permutation_from_key(args.key)
    if args.decrypt:
        key = key.inverse()
    with args.in_file, args.out_file:
        substitution.strip(args.in_file, args.out_file, key)


if __name__ == "__main__":
    main(get_args())
