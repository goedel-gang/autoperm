# vim: ts=4 sw=0 sts=-1 et ai tw=80

"""
A metric scoring text based on expected quadgram frequency.

This is a separate file because it loads a pretty considerable amount of data.
"""

import collections
import itertools

from pathlib import Path

import metric

# this reads a huge array of floats from quadgrams.dat. They're indexed by
# treating the quadgrams like base-26 integers.
QUADGRAMS_PATH = Path(__file__).parent / ".." / "data" / "quadgrams.dat"
with QUADGRAMS_PATH.open("r") as quadgram_file:
    QUADGRAM_FREQUENCIES = list(map(float, quadgram_file))


def rolling_slice(iterable, n):
    """
    Yield every slice of length n of the iterable. It yields the same internal
    deque that it modifies, so the caller is responsible for deep-copying if
    they need to.
    """
    window = collections.deque(itertools.islice(iterable, n), maxlen=n)
    if len(window) == n:
        yield window
    for i in iterable:
        window.append(i)
        yield window


def get_quadgram_score(quadgram):
    """
    Convert a quadgram to an score from the dataset. The quadgram should be
    represented as integers (A = 0, ..., Z = 25)
    """
    return QUADGRAM_FREQUENCIES[
            sum(r * 26 ** (3 - i) for i, r in enumerate(quadgram))]


@metric.Metric
def quadgram_score(text):
    """
    A metric scoring text based on expected quadgram frequency.

    This metric is useful because it is quite good at recognising text that is
    "starting to look like" English, so is appropriate for optimisation
    techniques like hill climbing. Quadgrams are a nice size in that we can
    feasibly store a frequency for each possible quadgram, and also quadgrams
    are long enough that certain patterns, like "XZXZ" can get heavily punished.

    Here a lower score means closer to English. Scores cannot be compared
    between texts of differing lengths, although maybe this could be corrected
    by dividing by the length. But I haven't thought about that. And in any case
    I have no idea what the scale of the frequencies in the dataset is supposed
    to be.
    """
    return sum(get_quadgram_score(quadgram)
            for quadgram in rolling_slice((ord(c) - 0x41 for c in text), 4))


if __name__ == "__main__":
    import sys
    from util import file_chars
    print("Total frequency: {} (?)".format(sum(QUADGRAM_FREQUENCIES)))
    print("English: {}".format(quadgram_score.english()))
    print("Random: {}".format(quadgram_score.random()))
    if not sys.stdin.isatty():
        print("stdin: {}".format(quadgram_score(file_chars(sys.stdin))))
