"""
Holds all special error classes defined for the generic module.
"""


class InexactError(ValueError):
    """Raised on conversion of float values with decimal places to integer
    types"""


class DispatchError(TypeError):
    """Raised when the type dispatcher cannot encounter an unique dispatch for
    some argument types."""


#
# Error functions
#
def no_methods_error(func, args=None, types=None):
    """Format and return a TypeError for the given func when called with
    the
    given arguments"""

    if args:
        types = [type(x) for x in args]

    name = func if isinstance(func, str) else getattr(func, '__name__', func)

    if types is None:
        return DispatchError('invalid call to %s()' % func)
    else:
        data = ', '.join(T.__name__ for T in types)
        return DispatchError('no method found for %s(%s)' % (name, data))


def raise_no_methods(func, args=None, types=None):
    """Format and raises a TypeError for the given func when called with
    the
    given arguments"""

    raise no_methods_error(func, args, types)


def raise_unordered_types(T1, T2):
    """Format and raises a TypeError saying that types T1 and T2 are not
    orderable"""

    raise get_unordered_types_error(T1, T2)


def get_unordered_types_error(T1, T2):
    """Format and returns a TypeError saying that types T1 and T2 cannot be
    ordered."""

    names = T1.__name__, T2.__name__
    return TypeError('there is no order relation for %s and %s.' % names)


def raise_unordered(x, y):
    """Format and raises a TypeError saying that the types for x and y cannot
    be ordered."""

    raise get_unordered_types_error(type(x), type(y))


