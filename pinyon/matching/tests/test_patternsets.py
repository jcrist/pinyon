from pinyon.matching import Pattern, DynamicPatternSet, StaticPatternSet, VAR
from pinyon.term.sexpr import sexpr_context


def inc(x):
    return x + 1


def add(x, y):
    return x + y


def double(x):
    return x * 2


a, b, c = vars = tuple("abc")
p1 = Pattern(sexpr_context, (add, a, 1), vars)
p2 = Pattern(sexpr_context, (add, (inc, a), (inc, a)), vars)
p3 = Pattern(sexpr_context, (add, (inc, b), (inc, a)), vars)
p4 = Pattern(sexpr_context, (add, a, a), vars)
p5 = Pattern(sexpr_context, (sum, [c, b, a]), vars)
p6 = Pattern(sexpr_context, (list, a), vars)

patterns = [p1, p2, p3, p4, p5, p6]
dynamic_pset = DynamicPatternSet(sexpr_context, patterns)
static_pset = StaticPatternSet(sexpr_context, patterns)


def test_DynamicPatternSet():
    net = ({sum: ({list: ({VAR: ({VAR: ({VAR: ({}, [4])}, [])}, [])}, [])}, []),
            list: ({VAR: ({}, [5])}, []), add: ({inc: ({VAR: ({inc: ({VAR: ({},
            [1, 2])}, [])}, [])}, []), VAR: ({1: ({}, [0]), VAR: ({}, [3])},
            [])}, [])}, [])

    assert dynamic_pset._net == net
    assert dynamic_pset.patterns == patterns


def test_StaticPatternSet():
    net = {list: {VAR: (5,)}, sum: {list: {VAR: {VAR: {VAR: (4,)}}}},
           add: {inc: {VAR: {1: (0, 3), inc: {VAR: (1, 2, 3)}, VAR: (3,)}},
           VAR: {1: (0, 3), VAR: (3,)}}}

    assert static_pset._net == net
    assert static_pset.patterns == patterns


def match_tester(pset):
    term = (add, 2, 1)
    matches = pset.match_all(term)
    assert len(matches) == 1
    assert matches[0] == (p1, {'a': 2})
    # Test matches specific before general
    term = (add, 1, 1)
    matches = pset.match_all(term)
    assert len(matches) == 2
    assert matches[0] == (p1, {'a': 1})
    assert matches[1] == (p4, {'a': 1})
    # Test match at depth
    term = (add, (inc, 1), (inc, 1))
    matches = pset.match_all(term)
    assert len(matches) == 3
    assert matches[0] == (p2, {'a': 1})
    assert matches[1] == (p3, {'a': 1, 'b': 1})
    assert matches[2] == (p4, {'a': (inc, 1)})
    # Test non-linear pattern checking
    term = (add, [1], [1])
    matches = pset.match_all(term)
    assert len(matches) == 1
    assert matches[0] == (p4, {'a': [1]})
    term = (add, 2, 3)
    matches = pset.match_all(term)
    assert len(matches) == 0


def test_static_matching():
    match_tester(static_pset)


def test_dynamic_matching():
    match_tester(dynamic_pset)
