from sympy import symbols, Function, MatrixSymbol, sympify, Add
from pinyon.term.sympy import isleaf, head, args, subs, rebuild, sympy_context

f = Function('f')
g = Function('g')
X = MatrixSymbol('X', 2, 2)
a, b, c, x, y = symbols('a, b, c, x, y')


def test_isleaf():
    assert isleaf(a)
    assert isleaf(X)
    assert isleaf(sympify(1))
    assert isleaf(sympify(1.0))
    assert not isleaf(a + b)
    assert not isleaf(f(a))


def test_head():
    assert head(a) == a
    assert head(sympify(1)) == sympify(1)
    assert head(f(a)) == f
    assert head(a + b) == Add


def test_args():
    assert args(f(a, b, c)) == (a, b, c)
    assert args(f(g(a), b, c)) == (g(a), b, c)
    assert args(g(a)) == (a,)


def test_subs():
    assert subs(f(a, b, c), {a: g(a), b: g(b)}) == f(g(a), g(b), c)
    assert subs(f(a, b, c), {a: b}) == f(b, b, c)


def test_rebuild():
    assert rebuild(f, (a, b, c)) == f(a, b, c)
    assert rebuild(g, (a,)) == g(a)
    assert rebuild(f, (g(a), b, c)) == f(g(a), b, c)


def test_context():
    assert sympy_context.head == head
    assert sympy_context.args == args
    assert sympy_context.subs == subs
    assert sympy_context.rebuild == rebuild
    # Test that traverse works
    term = f(g(a), b, c)
    assert list(sympy_context.traverse(term)) == [f(g(a), b, c),
            g(a), a, b, c]
    assert list(sympy_context.traverse(term, 'copyable')) == [f(g(a), b, c),
            g(a), a, b, c]
    # Test get
    assert sympy_context.get(term, 0) == g(a)
    assert sympy_context.get(term, 1) == b
    # Test index
    term = g(g(g(g(a, b), b), b), b)
    assert sympy_context.index(term, ()) == term
    assert sympy_context.index(term, (0, 0)) == g(g(a, b), b)
    assert sympy_context.index(term, (0, 0, 0, 1)) == b
