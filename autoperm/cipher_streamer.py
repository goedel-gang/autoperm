# vim: ts=4 sw=0 sts=-1 et ai tw=80

"""
Cipher streamer class
"""

import itertools

from util import file_chars, strip_punc

# Block default of 4 makes much more sense :P
BLOCK_DEFAULT = 4
WIDTH_DEFAULT = 80


def chunk(iterable, size, fillvalue=None):
    """
    Split an iterable into chunks of size `size`. Padded with `fillvalue` if
    necessary.
    """
    return itertools.zip_longest(*[iter(iterable)] * size, fillvalue=fillvalue)


def get_lines(iterable, block, width):
    """
    Convert into iterable of characters into regular blocks of characters,
    wrapped after a certain length.
    - If block <= 0, do not insert spaces
    - If width <= 0, do not insert newlines

    It is *excruciatingly* lazy, to the point of illegibility. But I think it's
    fun :).
    """
    # Each of the four cases is expected to produce an iterable `lines`,
    # consisting of iterables of strings to be joined and written as lines to
    # out_file.
    if block <= 0:
        if width <= 0:
            lines = iterable,
        else:
            # chunk output into lines of length `width`
            lines = chunk(iterable, width, "")
    else:
        # chunk the output into blocks of size `block`
        chunks = chunk(iterable, block, "")
        # add a space after each block
        chunks_spaced = map(itertools.chain.from_iterable,
                            zip(chunks, itertools.repeat(" ")))
        if width <= 0:
            # just write all the blocks
            lines = itertools.chain.from_iterable(chunks_spaced),
        else:
            if width < block:
                raise ValueError("`width` should be >= `block`")
            blocks_per_line = (width + 1) // (block + 1)
            # split blocks into lines
            lines = map(itertools.chain.from_iterable,
                        chunk(chunks_spaced, blocks_per_line, ""))
    # Just strip of any extra spaces at this stage rather than worrying about
    # removing them earlier.
    return ("".join(line).strip() for line in lines)


class CipherStreamer:
    """
    Context to stream a file object through a function and write it to an
    output, exposing the input as only uppercase letters. This class can handle
    case correction and punctuation, if the caller wants it to.

    This is implemented as a decorator, that takes the arguments `in_file` and
    `out_file`, a readable and writeable file respectively. A keyword argument
    `preserve` is also understood, and then depending on the value of that, the
    further keyword arguments `block` and `width` may be absorbed - see method
    documentation. Any further arguments are passed on to the function being
    decorated.

    (Make sure your function doesn't have any arguments with the same name as
    these!)

    Obviously the preservative functionality isn't very useful if you're doing
    serious cryptography, but I think it's more aesthetic to keep punctuation in
    (and it makes for an easy way to lower the difficulty of cryptanalysis for
    cipher challenge type things).

    It is perhaps worth mentioning that it is still perfectly possible to access
    the underlying generator:
    >>> @CipherStreamer
    ... def my_cipher(text):
    ...     pass
    >>> my_cipher.func
    """
    __slots__ = "func",

    def __init__(self, func):
        """
        Func should be a generator with first positional argument an iterable of
        alphabetic characters, and further arguments passed through *args,
        **kwargs. Func should yield alphabetic characters to be written.
        """
        self.func = func

    def __call__(self, *args, **kwargs):
        """
        This is what happens when people actually call the function. It
        helpfully tells you to decide what you actually want in life.
        """
        raise TypeError("You should call {0}.preserve or {0}.strip explicitly"
                .format(self.func.__name__))

    def strip(self, in_file, out_file, *args, compare=False, lowercase=False,
              block=BLOCK_DEFAULT, width=WIDTH_DEFAULT, **kwargs):
        """
        Strip all punctuation from the output, convert output to uppercase, and
        format the output into blocks of size `block`, with lines wrapped to
        length `width`. If width is <= 0, no wrapping is done. If block is <= 0,
        no spaces are inserted.

        Of course you could simulate the case with width <= 0, block > 0 with
        the case width > 0, block <= 0 (and vice versa). But I think it's a nice
        courtesy to support both.

        If it is passed `compare=True`, it alternates between printing lines of
        the original text and the processed text (so they can be compared). If
        either runs out, empty lines will be printed until the other is
        exhausted.

        If it is passed `lowercase=True`, output it lowercase rather than
        uppercase.
        """
        if compare and 0 < width <= 2:
            raise ValueError("width should be > 2 in compare mode")
        input_chars = strip_punc(file_chars(in_file))
        if compare:
            input_chars, plaintext = itertools.tee(input_chars)
        output = self.func(input_chars, *args, **kwargs)
        if compare:
            lines = get_lines(output, block, width - 2)
        else:
            lines = get_lines(output, block, width)
        if lowercase:
            post_func = lambda s: "{}\n".format(s.lower())
        else:
            post_func = lambda s: "{}\n".format(s.upper())
        if compare:
            plain_lines = get_lines(plaintext, block, width - 2)
            for line, plain in itertools.zip_longest(lines, plain_lines,
                                                     fillvalue=""):
                out_file.write("i:{}".format(post_func(plain)))
                out_file.write("o:{}".format(post_func(line)))
                out_file.write("\n")
        else:
            for line in lines:
                out_file.write(post_func(line))

    # TODO: do this better (more lazily), with itertools or something. As it
    #       stands this could easily just be written as a function returning a
    #       closure.
    #       I think we have to ask for func to be implemented as a coroutine to
    #       do this nicely
    def preserve(self, in_file, out_file, *args, **kwargs):
        """
        Restore punctuation and case after the generator.

        If more output letters are produced than there were input letters, the
        extra letters are all written as they are, with no separation.

        At the end, all remaining punctuation is written to the output file.
        This is useful because for instance it means that the last trailing
        newline (which is present in any file made by a sane person) will be
        written as output.
        """
        in_file_1, in_file_2 = itertools.tee(file_chars(in_file))
        output = self.func(strip_punc(in_file_1), *args, **kwargs)
        for c in output:
            punc = ' '
            for punc in in_file_2:
                if punc.isalpha():
                    break
                out_file.write(punc)
            if not punc.isalpha():
                out_file.write(c)
            elif punc.isupper():
                out_file.write(c.upper())
            else:
                out_file.write(c.lower())
        for punc in in_file_2:
            if not punc.isalpha():
                out_file.write(punc)
