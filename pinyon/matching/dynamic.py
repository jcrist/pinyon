from __future__ import absolute_import, division, print_function
from collections import deque

from .core import VAR, END, PatternSet
from ..util import copy_doc


class DynamicPatternSet(PatternSet):
    """A set of patterns.

    Forms a structure for fast matching over a set of patterns. This allows for
    matching of terms to patterns for many patterns at the same time.

    Attributes
    ----------
    patterns : list
        A list of `Pattern`s included in the `PatternSet`.
    """

    def __init__(self, context, patterns):
        self.context = context
        self._net = Node()
        self.patterns = []
        for p in patterns:
            self.add(p)

    def add(self, pat):
        """Add a pat to the DynamicPatternSet.

        Parameters
        ----------
        pat : Pattern
        """

        if self.context != pat.context:
            raise ValueError("All patterns in a PatternSet must have the same"
                             "context")
        vars = pat.vars
        curr_node = self._net
        ind = len(self.patterns)
        # List of variables, in order they appear in the POT of the term
        for t in map(self.context.head, self.context.traverse(pat.pat)):
            prev_node = curr_node
            if t in vars:
                t = VAR
            if t in curr_node.edges:
                curr_node = curr_node.edges[t]
            else:
                curr_node.edges[t] = Node()
                curr_node = curr_node.edges[t]
        # We've reached a leaf node. Add the term index to this leaf.
        prev_node.edges[t].patterns.append(ind)
        self.patterns.append(pat)

    @copy_doc(PatternSet.match_iter)
    def match_iter(self, term):
        S = self.context.traverse(term, 'copyable')
        for m, syms in _match(S, self._net):
            for i in m:
                pat = self.patterns[i]
                subs = _process_match(pat, syms)
                if subs is not None:
                    yield pat, subs


class Node(tuple):
    """A Discrimination Net node."""

    __slots__ = ()

    def __new__(cls, edges=None, patterns=None):
        edges = edges if edges else {}
        patterns = patterns if patterns else []
        return tuple.__new__(cls, (edges, patterns))

    @property
    def edges(self):
        """A dictionary, where the keys are edges, and the values are nodes"""
        return self[0]

    @property
    def patterns(self):
        """A list of all patterns that currently match at this node"""
        return self[1]


def _match(S, N):
    """Structural matching of term S to discrimination net node N."""

    stack = deque()
    restore_state_flag = False
    # matches are stored in a tuple, because all mutations result in a copy,
    # preventing operations from changing matches stored on the stack.
    matches = ()
    while True:
        if S.term is END:
            yield N.patterns, matches
        try:
            # This try-except block is to catch hashing errors from un-hashable
            # types. This allows for variables to be matched with un-hashable
            # objects.
            n = N.edges.get(S.current, None)
            if n and not restore_state_flag:
                stack.append((S.copy(), N, matches))
                N = n
                S.next()
                continue
        except TypeError:
            pass
        n = N.edges.get(VAR, None)
        if n:
            restore_state_flag = False
            matches = matches + (S.term,)
            S.skip()
            N = n
            continue
        try:
            # Backtrack here
            (S, N, matches) = stack.pop()
            restore_state_flag = True
        except:
            return


def _process_match(pat, syms):
    """Process a match to determine if it is correct, and to find the correct
    substitution that will convert the term into the pattern.

    Parameters
    ----------
    pat : Pattern
    syms : iterable
        Iterable of subterms that match a corresponding variable.

    Returns
    -------
    A dictionary of {vars : subterms} describing the substitution to make the
    pattern equivalent with the term. Returns `None` if the match is
    invalid."""

    subs = {}
    varlist = pat._varlist
    if not len(varlist) == len(syms):
        raise RuntimeError("length of varlist doesn't match length of syms.")
    for v, s in zip(varlist, syms):
        if v in subs and subs[v] != s:
            return None
        else:
            subs[v] = s
    return subs
