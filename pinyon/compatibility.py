from __future__ import absolute_import, division, print_function

import sys

PY3 = sys.version_info[0] == 3

if PY3:
    from collections import Iterator
    from functools import reduce
else:
    class Iterator(object):
        def next(self):
            return type(self).__next__(self)
    reduce = reduce
