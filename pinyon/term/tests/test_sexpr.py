from pinyon.term.sexpr import (istask, head, args, subs, rebuild, run, funcify,
        sexpr_context)


def inc(x):
    return x + 1


def add(x, y):
    return x + y


def test_istask():
    assert istask((inc, 1))
    assert not istask(1)
    assert not istask((1, 2))


def test_head():
    assert head((inc, 1)) == inc
    assert head((add, 1, 2)) == add
    assert head((add, (inc, 1), (inc, 1))) == add
    assert head([1, 2, 3]) == list


def test_args():
    assert args((inc, 1)) == (1,)
    assert args((add, 1, 2)) == (1, 2)
    assert args(1) == ()
    assert args([1, 2, 3]) == [1, 2, 3]


def test_subs():
    assert subs((add, (add, 1, 'x')), {'x': 2}) == (add, (add, 1, 2))
    assert subs((add, (add, 'x', 'x')), {'x': 2}) == (add, (add, 2, 2))


def test_rebuild():
    assert rebuild(add, (1, 2)) == (add, 1, 2)
    assert rebuild(inc, (1,)) == (inc, 1)
    assert rebuild(add, ((add, 1, 2), 2)) == (add, (add, 1, 2), 2)


def test_run():
    assert run((add, 1, 2)) == 3
    assert run((add, (add, 1, 2), 2)) == 5


def test_funcify():
    term = (add, 'x', 'x')
    f = funcify(('x',), term)
    assert f(1) == 2
    assert f(2) == 4
    term = (add, 'x', (add, 'x', 'y'))
    f = funcify(('x', 'y'), term)
    assert f(1, 2) == 4
    assert f(3, 5) == 11


def test_context():
    assert sexpr_context.head == head
    assert sexpr_context.args == args
    assert sexpr_context.subs == subs
    assert sexpr_context.rebuild == rebuild
    # Test that traverse works
    term = (add, (inc, 'x'), 'y')
    assert list(sexpr_context.traverse(term)) == [(add, (inc, 'x'), 'y'),
        (inc, 'x'), 'x', 'y']
    assert list(sexpr_context.traverse(term, 'copyable')) == [
        (add, (inc, 'x'), 'y'), (inc, 'x'), 'x', 'y']
    # Test get
    assert sexpr_context.get(term, 0) == (inc, 'x')
    assert sexpr_context.get(term, 1) == 'y'
    # Test index
    term = (add, (add, (add, (add, 1, 2), 2), 2), 2)
    assert sexpr_context.index(term, ()) == term
    assert sexpr_context.index(term, (0, 0)) == (add, (add, 1, 2), 2)
    assert sexpr_context.index(term, (0, 0, 0, 1)) == 2
