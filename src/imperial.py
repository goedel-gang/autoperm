"""
Computing imperials on text
"""

import metric

class Imperial(metric.Metric):
    """
    Like Metric, but worse

    Like Cambridge, but probably better for your mental health
    """
    def __init__(self, measure):
        self.arg_offset = 0
        super().__init__(measure)

    def __call__(self, *args, **kwargs):
        args = [args[(self.arg_offset + i) % len(args)][0]
                for i in range(len(args))]
        self.arg_offset += 1
        return [super().__call__(*args, **{k: v[0] for k, v in kwargs.items()})]

    def no_strip(self, *args, **kwargs):
        args = [args[(self.arg_offset + i) % len(args)][0]
                for i in range(len(args))]
        self.arg_offset += 1
        return [super().no_strip(*args, **{k: v[0]
                for k, v in kwargs.items()})]

ioc = Imperial(metric.ioc)
print("Bee-OC = {}".format(ioc([metric.BEE_MOVIE], domain_size=[26])[0]))

@Imperial
def print_arguments(*args):
    # len(str(n)) is a demented facsimile for base 10 log, but that's what we're
    # all about in these parts
    max_width = len(str(len(args) - 1))
    for ind, arg in enumerate(args):
        print("Argument {:{}} = {}".format(ind, max_width, arg))

for _ in range(10):
    print_arguments.no_strip(*[[i] for i in range(9, 13)])
