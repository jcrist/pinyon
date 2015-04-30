# Pinyon

[![Build Status](https://travis-ci.org/jcrist/pinyon.svg)](https://travis-ci.org/jcrist/pinyon)

A term rewriting engine for Python. Currently under development, not
recommended for use at this time:)

Provides:

- Syntactic pattern matching
- Syntactic term rewriting
- An example term implementation ``pinyon.term.sexpr``

Pinyon is designed to work with any tree like term that has the following
interface:

- ``head(term)``: get the head of term
- ``args(term)``: returns a tuple of subterms from the term
- ``subs(term, sub_dict)``: performs term substitutions
- ``rebuild(head, args)``: create a term from its head and args

If you can implement those 4 function to work on your classes, then Pinyon
should *just work*. Two example implementations can be found in
``pinyon.term.sexpr`` and ``pinyon.term.sympy``.

## Example

```python
>>> from pinyon import Engine
>>> from pinyon.term.sexpr import sexpr_context
>>> from operator import add, mul

# Create an engine
>>> eng = Engine(sexpr_context)

# Create some patterns
>>> x, y = vars = ("x", "y")
>>> pat = lambda x: eng.pattern(x, vars)
>>> patterns = [pat(i) for i in  [(add, x, 1),
...                               (add, x, y),
...                               (add, (mul, x, y), x)]]

# Create a pattern set. This creates a structure for fast pattern matching.
>>> pset = eng.patternset(patterns, 'static')

# Perform pattern matching
>>> pset.match_all((add, 1, 2))
[(Pattern((add, 'x', 'y'), ('x', 'y')), {'x': 1, 'y': 2})]

>>> pset.match_all((add, (mul, 1, 2), 1))
[(Pattern((add, 'x', 1), ('x', 'y')), {'x': (mul, 1, 2)}),
 (Pattern((add, 'x', 'y'), ('x', 'y')), {'x': (mul, 1, 2), 'y': 1}),
 (Pattern((add, (mul, 'x', 'y'), 'x'), ('x', 'y')), {'x': 1, 'y': 2})]
```
