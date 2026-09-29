def print_signature(func, types, restype=None):
    """
    Return a pretty-printed version of an abstract call to some arguments
    of the given sequence of types.


    Example:
        >>> print_signature(int, (str, int))
        'int(str, int)'
    """

    fname = func.__name__
    args = ', '.join(map(tname, types))
    if restype is None:
        return f'{fname}({args})'
    else:
        return f'{fname}({args}) -> {tname(restype)}'



def tname(x):
    """A shortcut to the object's type name"""
    return type(x).__name__