from collections import Iterator, deque
from functools import reduce


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


class Token(object):
    """A token object.

    Used to express certain objects in the traversal of a term or pattern."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


# A variable to represent *all* variables in a discrimination net
VAR = Token('?')
# Represents the end of the traversal of an expression. We can't use `None`,
# 'False', etc... here, as anything may be an argument to a function.
END = Token('end')


# TODO: It would be really nice to get rid of one of the following traversal
# implementations. The stack based implementation is only used by the dynamic
# pattern sets, but a way to store the iteration state is necessary for
# backtracking. Conversely, the recursive algorithm is only necessary for the
# static pattern sets, as the path index of the current term is much faster to
# find in a recursive fashion.  I'm fairly certain there must be a way to
# eliminate one of these...
class Traverser(object):
    """Stack based preorder traversal of terms.

    This provides a copyable traversal object, which can be used to store
    choice points when backtracking."""

    def __init__(self, context, term, stack=None):
        self.term = term
        self.context = context
        if not stack:
            self._stack = deque([END])
        else:
            self._stack = stack

    def __iter__(self):
        while self.term is not END:
            yield self.term
            self.next()

    def copy(self):
        """Copy the traverser in its current state.

        This allows the traversal to be pushed onto a stack, for easy
        backtracking."""

        return Traverser(self.context, self.term, deque(self._stack))

    def next(self):
        """Proceed to the next term in the preorder traversal."""

        subterms = self.context.args(self.term)
        if not subterms:
            # No subterms, pop off stack
            self.term = self._stack.pop()
        else:
            self.term = subterms[0]
            self._stack.extend(reversed(subterms[1:]))

    @property
    def current(self):
        return self.context.head(self.term)

    @property
    def arity(self):
        return len(self.context.args(self.term))

    def skip(self):
        """Skip over all subterms of the current level in the traversal"""
        self.term = self._stack.pop()


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
