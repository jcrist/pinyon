from pinyon.core import Context

from sympy import Symbol, MatrixSymbol, Number


def isleaf(expr):
    """Returns True if the expr is a leaf node else False"""

    return isinstance(expr, (Symbol, MatrixSymbol, Number))


def head(term):
    """Return the top level node of a term"""

    if isleaf(term):
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
