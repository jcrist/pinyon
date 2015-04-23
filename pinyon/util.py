def copy_doc(wrap_func, strip_context=False):
    """Copy the docstring from one function to another.
    If `strip_context` is `True`, removes the line `"context : Context"` from
    the docstring"""

    def wrapper(func):
        if not strip_context:
            func.__doc__ = wrap_func.__doc__
        else:
            ctx_line = "    context : Context"
            doc = wrap_func.__doc__
            doc = '\n'.join(i for i in doc.splitlines() if i != ctx_line)
            func.__doc__ = doc
        return func
    return wrapper
