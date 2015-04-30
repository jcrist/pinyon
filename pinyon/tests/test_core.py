from pinyon.term.sexpr import sexpr_context
from pinyon.core import PreorderTraversal, Engine
from pinyon.matching import Pattern, StaticPatternSet, DynamicPatternSet


def inc(x):
    return x + 1


def add(x, y):
    return x + y


def double(x):
    return x * 2


def test_preorder_traversal():
    term = (add, (inc, 1), (double, (inc, 1)))
    pot = list(PreorderTraversal(sexpr_context, term))
    assert pot == [(add, (inc, 1), (double, (inc, 1))), (inc, 1), 1,
            (double, (inc, 1)), (inc, 1), 1]
    pot = list(PreorderTraversal(sexpr_context, term, 'arity'))
    assert pot == [((add, (inc, 1), (double, (inc, 1))), 2), ((inc, 1), 1),
            (1, 0), ((double, (inc, 1)), 1), ((inc, 1), 1), (1, 0)]
    pot = list(PreorderTraversal(sexpr_context, term, 'path'))
    assert pot == [((add, (inc, 1), (double, (inc, 1))), ()), ((inc, 1), (0,)),
            (1, (0, 0)), ((double, (inc, 1)), (1,)), ((inc, 1), (1, 0)),
            (1, (1, 0, 0))]
    # Test skip
    def helper(pot):
        # advance twice, then skip. should skip to double
        next(pot)
        next(pot)
        pot.skip()
    pot = PreorderTraversal(sexpr_context, term)
    helper(pot)
    assert list(pot) == [(double, (inc, 1)), (inc, 1), 1]
    pot = PreorderTraversal(sexpr_context, term, 'arity')
    helper(pot)
    assert list(pot) == [((double, (inc, 1)), 1), ((inc, 1), 1), (1, 0)]
    pot = PreorderTraversal(sexpr_context, term, 'path')
    helper(pot)
    assert list(pot) == [((double, (inc, 1)), (1,)), ((inc, 1), (1, 0)),
            (1, (1, 0, 0))]


def test_engine():
    # Just check that the interface for eng actually works
    eng = Engine(sexpr_context)
    p1 = eng.pattern((add, 'a', 'b'), ('a', 'b'))
    p2 = eng.pattern((add, 'a', 'a'), ('a', 'b'))
    pats = [p1, p2]
    assert isinstance(p1, Pattern)
    static_pset = eng.patternset(pats, 'static')
    assert isinstance(static_pset, StaticPatternSet)
    assert static_pset.patterns == pats
    dynamic_pset = eng.patternset(pats, 'dynamic')
    assert isinstance(dynamic_pset, DynamicPatternSet)
    assert dynamic_pset.patterns == pats
