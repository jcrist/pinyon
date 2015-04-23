from pinyon.core import Context

from sympy import Symbol, MatrixSymbol, Number


def is_leaf(expr):
    """Returns True if the expr is a leaf node else False"""

    _leaves = (Symbol, MatrixSymbol, Number)
    return isinstance(expr, _leaves)


def head(term):
    """Return the top level node of a term"""

    if is_leaf(term):
        return term
    else:
        return type(term)


def args(term):
    return term.args


def rebuild(head, args):
    return head(*args)


def subs(term, sd):
    return term.subs(sd)


sympy_context = Context(head, args, subs, rebuild)
