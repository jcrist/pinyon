"""An example term implementation. This implements terms used for dask"""

from itertools import count

from pinyon.core import Context

def istask(x):
    """ Is x a runnable task?

    A task is a tuple with a callable first argument

    Example
    -------

    >>> inc = lambda x: x + 1
    >>> istask((inc, 1))
    True
    >>> istask(1)
    False
    """
    return isinstance(x, tuple) and x and callable(x[0])


def head(task):
    """Return the top level node of a task"""

    if istask(task):
        return task[0]
    elif isinstance(task, list):
        return list
    else:
        return task


def args(task):
    """Get the arguments for the current task"""

    if istask(task):
        return task[1:]
    elif isinstance(task, list):
        return task
    else:
        return ()


def subs(expr, sub_dict):
    """Perform direct matching substitution."""
    if expr in sub_dict:
        return sub_dict[expr]
    elif not args(expr):
        return expr
    new_args = (subs(arg, sub_dict) for arg in args(expr))
    return rebuild(head(expr), new_args)


def rebuild(func, args):
    return (func,) + tuple(args)


sexpr_context = Context(head, args, subs, rebuild)


# Other fun things for a term implementation:

def preorder_traversal(task):
    """A generator to preorder-traverse a task."""

    for item in task:
        if istask(item):
            for i in preorder_traversal(item):
                yield i
        elif isinstance(item, list):
            yield list
            for i in preorder_traversal(item):
                yield i
        else:
            yield item


def run(task):
    """Run a task"""

    if istask(task):
        func = task[0]
        return func(*(run(i) for i in task[1:]))
    else:
        return task


def funcify(args, task):
    """Compile a task into a callable function"""

    lookup = {}
    names = ("_gensym_%d" %i for i in count(1))
    arg_string = ", ".join(str(i) for i in args)
    code_string = _compile(args, task, lookup, names)
    code = "lambda {0}: {1}".format(arg_string, code_string)
    return eval(code, lookup)


# Helpers
def _code_print(args, t, lookup, names):
    """Print t as code"""

    if t in args:
        return str(t)
    elif isinstance(t, (int, float, str, bool)):
        return str(t)
    else:
        name = next(names)
        lookup[name] = t
        return name


def _compile(func_args, task, lookup, names):
    """Print a task. Modifies lookup in place"""

    if istask(task):
        func = _code_print(func_args, head(task), lookup, names)
        new_args = (_compile(func_args, i, lookup, names) for i in args(task))
        return "{0}({1})".format(func, ", ".join(new_args))
    else:
        return _code_print(func_args, task, lookup, names)
