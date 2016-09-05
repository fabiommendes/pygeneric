def print_signature(func, types):
    """Return a pretty-printed version of an abstract call to some arguments
    of the given sequence of types.


    Example
    -------

    >>> print_signature(int, (str, int))
    'int(str, int)'
    """

    fname = func.__name__
    args = ', '.join(T.__name__ for T in types)
    return '%s(%s)' % (fname, args)


def tname(x):
    """A shortcut to the object's type name"""
    
    return type(x).__name__