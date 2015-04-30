from __future__ import absolute_import, division, print_function
from collections import deque


class Pattern(object):
    """A pattern.

    Parameters
    ----------
    context : Context
    pat : term
    vars: tuple, optional
        Tuple of variables found in the pattern.
    """
    def __init__(self, context, pat, vars=()):
        self.context = context
        self.pat = pat
        self.vars = vars
        self._build(context)

    def __repr__(self):
        return "Pattern({0}, {1})".format(self.pat, self.vars)

    def _build(self, context):
        """Initialized once a context is set"""
        path_lookup = {}
        varlist = []
        for term, path in context.traverse(self.pat, 'path'):
            if term in self.vars:
                path_lookup.setdefault(term, []).append(path)
                varlist.append(term)
        # For deterministic nets
        self._path_lookup = path_lookup
        # For nondeterministic nets
        self._varlist = varlist


class PatternSet(object):
    """A set of patterns.

    Forms a structure for fast matching over a set of patterns. This allows for
    matching of terms to patterns for many patterns at the same time.

    Attributes
    ----------
    context : Context
    patterns : list
        A list of `Pattern`s included in the `PatternSet`.
    """

    def match_iter(self, term):
        """A generator that lazily finds matchings for term from the PatternSet.

        Paramters
        ---------
        term : term

        Yields
        ------
        Tuples of `(pat, subs)`, where `pat` is the pattern being matched, and
        `subs` is a dictionary mapping the variables in the pattern to their
        matching values in the term."""
        pass

    def match_all(self, term):
        """Finds all matchings for term in the PatternSet.

        Equivalent to ``list(pat_set.match_iter(term))``.

        Paramters
        ---------
        term : term

        Returns
        -------
        List containing tuples of `(pat, subs)`, where `pat` is the pattern
        being matched, and `subs` is a dictionary mapping the variables in the
        pattern to their matching values in the term."""

        return list(self.match_iter(term))

    def match_one(self, term):
        """Finds the first matching for term in the PatternSet.

        Paramters
        ---------
        term : term

        Returns
        -------
        A tuple `(pat, subs)`, where `pat` is the pattern being matched, and
        `subs` is a dictionary mapping the variables in the pattern to their
        matching values in the term. In the case of no matchings, a tuple
        (None, None) is returned."""

        for pat, subs in self.match_iter(term):
            return pat, subs
        return None, None


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
