from collections import Iterator
from functools import reduce

from .matching import (Traverser, Pattern, PatternSet, StaticPatternSet,
        DynamicPatternSet)
from .util import copy_doc


class Engine(object):
    """Main entry point for Pinyon"""

    def __init__(self, context):
        self.context = context

    @copy_doc(Pattern, True)
    def pattern(self, pat, vars=()):
        return Pattern(self.context, pat, vars)

    @copy_doc(PatternSet, True)
    def patternset(self, patterns, type='static'):
        if type == 'dynamic':
            return DynamicPatternSet(self.context, patterns)
        else:
            return StaticPatternSet(self.context, patterns)


class Context(object):
    """Abstracting the interface for a term"""

    def __init__(self, head=None, args=None, subs=None, rebuild=None):
        self.head = head
        self.args = args
        self.subs = subs
        self.rebuild = rebuild

    def index(self, term, inds):
        """Get a subterm from its path index"""
        return reduce(self.get, inds, term)

    def get(self, term, ind):
        """Get the `ind`th subterm of `term`."""
        return self.args(term)[ind]

    def traverse(self, term, variant="normal"):
        """Perform a preorder traversal of a term.

        Parameters
        ----------
        term : term
        variant : str, optional
            Specify a variation of preorder traversal. Options are:
            - ``"normal"``: yields ``term``
            - ``"path"``: yields ``(term, path_index)``
            - ``"arity"``: yields ``(term, arity)``
            - ``"copyable"``: a copyable, stack based implementation, good for
              backtracking. Yields ``term``
        """

        if variant == 'copyable':
            return Traverser(self, term)
        else:
            return PreorderTraversal(self, term, variant)


# TODO: It would be really nice to get rid of one of the traversal
# implementations. The stack based implementation (`Traverser`, imported from
# matching/core.py) is only used by the dynamic pattern sets, but a way to
# store the iteration state is necessary for backtracking. Conversely, the
# recursive algorithm is only necessary for the static pattern sets, as the
# path index of the current term is much faster to find in a recursive fashion.
# I'm fairly certain there must be a way to eliminate one of these...
class PreorderTraversal(Iterator):
    """Preorder traversal of a generic term"""

    def __init__(self, context, node, variant="normal"):
        self._skip_flag = False

        args = context.args
        if variant == "path":
            # Yield (node, path index)
            def _traverse(self, node, cur_path=()):
                yield node, cur_path
                if self._skip_flag:
                    self._skip_flag = False
                    return
                for i, t in enumerate(args(node)):
                    for st, path in _traverse(self, t, cur_path + (i,)):
                        yield st, path
        elif variant == "arity":
            # Yield (node, path index)
            def _traverse(self, node):
                childs = args(node)
                yield node, len(childs)
                if self._skip_flag:
                    self._skip_flag = False
                    return
                for t in childs:
                    for res in _traverse(self, t):
                        yield res
        elif variant is "normal":
            # Yield node
            def _traverse(self, node):
                yield node
                if self._skip_flag:
                    self._skip_flag = False
                    return
                for t in args(node):
                    for st in _traverse(self, t):
                        yield st
        self._pt = _traverse(self, node)

    def skip(self):
        self._skip_flag = True

    def __next__(self):
        return next(self._pt)

    def __iter__(self):
        return self
