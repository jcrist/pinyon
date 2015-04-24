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
