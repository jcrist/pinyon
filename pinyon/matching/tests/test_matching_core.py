from pinyon.term.sexpr import sexpr_context
from pinyon.matching.core import Traverser, Pattern


def inc(x):
    return x + 1


def add(x, y):
    return x + y


def double(x):
    return x * 2


def test_traverser():
    term = (add, (inc, 1), (double, (inc, 1)))
    t = Traverser(sexpr_context, term)
    t2 = t.copy()
    assert t.current == add
    assert t.arity == 2
    t.next()
    assert t.current == inc
    assert t.arity == 1
    # Ensure copies aren't advanced when the original advances
    assert t2.current == add
    t.skip()
    assert t.current == double
    t.next()
    assert t.current == inc
    t.next()
    assert t.current == 1
    assert t.arity == 0
    assert list(map(sexpr_context.head, t2)) == [add, inc, 1, double, inc, 1]


def test_pattern():
    a, b, c = vars = tuple("abc")

    p = Pattern(sexpr_context, (add, a, b), vars)
    assert p._varlist == [a, b]
    assert p._path_lookup == {a: [(0,)], b: [(1,)]}

    p = Pattern(sexpr_context, (add, a, a), vars)
    assert p._varlist == [a, a]
    assert p._path_lookup == {a: [(0,), (1,)]}

    p = Pattern(sexpr_context, (add, (double, a), b), vars)
    assert p._varlist == [a, b]
    assert p._path_lookup == {a: [(0, 0)], b: [(1,)]}

    p = Pattern(sexpr_context, (add, 1, 2), vars)
    assert p._varlist == []
    assert p._path_lookup == {}
