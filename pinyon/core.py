from collections import Iterator, deque


class Context(object):
    """Abstracting the interface for a term"""

    def __init__(self, head=None, args=None, subs=None, rebuild=None):
        self.head = head
        self.args = args
        self.subs = subs
        self.rebuild = rebuild

    def preorder_traversal(self, term, path=False):
        return PreorderTraversal(self, term, path)

    def traverser(self, term):
        return Traverser(self, term)


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


class Traverser(object):
    """Traverser interface for terms.

    Class for storing the state while performing a preorder-traversal of a
    term.

    Parameters
    ----------
    term : term
        The term to be traversed

    Attributes
    ----------
    term
        The current element in the traversal
    current
        The head of the current element in the traversal. This is simply `head`
        applied to the attribute `term`.
    """

    def __init__(self, context, term, stack=None):
        self.term = term
        self.context = context
        if not stack:
            self._stack = deque([END])
        else:
            self._stack = stack

    def __iter__(self):
        while self.term is not END:
            yield self.current
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

    def __init__(self, context, node, path=False):
        self._head = context.head
        self._args = context.args
        self._skip_flag = False
        if path:
            self._pt = self._preorder_and_index(node, ())
        else:
            self._pt = self._preorder_traversal(node)

    def _preorder_traversal(self, node):
        yield self._head(node)
        if self._skip_flag:
            self._skip_flag = False
            return
        for t in self._args(node):
            for st in self._preorder_traversal(t):
                yield st

    def _preorder_and_index(self, node, cur_path):
        yield node, cur_path
        if self._skip_flag:
            self._skip_flag = False
            return
        for i, t in enumerate(self._args(node)):
            for st, path in self._preorder_and_index(t, cur_path + (i,)):
                yield st, path

    def skip(self):
        self._skip_flag = True

    def __next__(self):
        return next(self._pt)

    def __iter__(self):
        return self
