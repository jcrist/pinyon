from .core import VAR
from .pattern import PatternSet
from .util import copy_doc


@copy_doc(PatternSet)
class StaticPatternSet(PatternSet):
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
        self.patterns = patterns
        if not all(self.context == p.context for p in patterns):
            raise ValueError("All patterns in a PatternSet must have the same"
                             "context")
        self._net = build_automata(self.context, self.patterns)

    @copy_doc(PatternSet.match_iter)
    def match_iter(self, t):
        inds, data = self._match(t)
        for i in inds:
            pat = self.patterns[i]
            subs = _process_match(pat, data)
            if subs is not None:
                yield pat, subs

    def _match(self, t):
        """Performs the actual matching operation"""

        net = self._net
        head = self.context.head
        pot = self.context.preorder_traversal(t, True)
        path_lookup = {}
        for term, ind in pot:
            var_val = net.get(VAR, None)
            val = net.get(head(term), None)
            if val is not None:
                net = val
                if var_val is not None:
                    path_lookup[ind] = term
                continue
            if var_val is not None:
                net = var_val
                pot.skip()
                path_lookup[ind] = term
                continue
            return [], {}
        return net, path_lookup


def _process_match(pat, cache):
    path_lookup = pat._path_lookup
    subs = {}
    for var, paths in path_lookup.items():
        subs[var] = first = cache[paths[0]]
        for p in paths[1:]:
            new = cache[p]
            if new != first:
                return None
    return subs


# All functionality below here is used for compilation of a set of patterns
# into a deterministic matching automata, as described in:
#
# Nedjah, Nadia. "Minimal deterministic left-to-right pattern-matching
# automata." ACM Sigplan Notices 33.1 (1998): 40-47.

class MSet(tuple):
    """A set of `MItem`s"""

    def __new__(cls, items):
        return tuple.__new__(cls, (items,))

    def __str__(self):
        data = ",\n".join(str(i) for i in self.items)
        return "MSet([\n{0}])".format(data)

    @property
    def items(self):
        return self[0]

    def is_equivalent(self, other):
        """Determines if two matching sets are equivalent"""

        has_pair = []
        # First loop through self, find equivalent match in other, and put in
        # `has_pair` If no match exists, return False.
        for i1 in self.items:
            for i2 in other.items:
                if i1 == i2:
                    has_pair.append(i2)
                    break
            else:
                return False
        # Then for every item in other, ensure it has been placed at least once
        # in `has_pair`. If it hasn't, return `False`.
        for i2 in other.items:
            if i2 not in has_pair:
                return False
        return True


class MItem(tuple):
    """Represents a single item in a matching set."""

    def __new__(cls, suffix, rule):
        return tuple.__new__(cls, (suffix, rule))

    @property
    def suffix(self):
        return self[0]

    @property
    def rule(self):
        return self[1]


def flatten_with_arity(context, pattern):
    """term -> [(term, arity), ...]"""

    vars = pattern.vars
    def _helper(pot):
        for t in pot:
            if t in vars:
                t = VAR
            yield t, pot.arity
    return list(_helper(context.traverser(pattern.pat)))


def next_terms(M):
    """Set of then next term after the matching position of an MSet"""

    return set(pat.suffix[0] for pat in M.items if pat.suffix)


def match_on(term, *items):
    """Determine if the matching point of term is in items"""

    return term.suffix and term.suffix[0] in items


def delta(context, M, s):
    """The transition function"""

    set1 = [MItem(p.suffix[1:], p.rule) for p in M.items if match_on(p, s, VAR)]
    var_next = [p for p in set1 if match_on(p, (VAR, 0))]
    set2 = []
    for var_pat in var_next:
        for con_pat in set1:
            func, arity = con_pat.suffix[0]
            if func is VAR:
                continue
            suffix = [(func, arity)] + [(VAR, 0)]*arity + var_pat.suffix[1:]
            new = MItem(suffix, var_pat.rule)
            set2.append(new)
    return MSet(set1 + set2)


def build_automata(context, patterns):
    """Construct the deterministic automata"""

    temp = (flatten_with_arity(context, p) for p in patterns)
    L = [MSet([MItem(p, i) for (i, p) in enumerate(temp)])]
    paths = [{}]

    for ind, mset in enumerate(L):
        for t in next_terms(mset):
            new = delta(context, mset, t)
            if new:
                for new_ind, match_set in enumerate(L):
                    if match_set.is_equivalent(new):
                        break
                else:
                    L.append(new)
                    paths.append({})
                    new_ind = len(L) - 1
                # TODO: setting for varargs to include (sym, arity) as key?
                paths[ind][t[0]] = new_ind

    # Replace leaf dicts with sets of the matching patterns
    for i, lk in enumerate(paths):
        if lk == {}:
            paths[i] = tuple(set(m.rule for m in L[i].items))

    # Finalize the automata
    for lk in paths:
        if isinstance(lk, dict):
            for k, v in lk.items():
                lk[k] = paths[v]

    return paths[0]
