'''
Define the convert() function and friends.
'''

CONVERT_FUNCTIONS = {}

__all__ = ['convert', 'get_conversion', 'set_conversion']


def do_nothing(x):
    '''A function that does nothing and returns its argument'''

    return x


#
# Conversion between numerical types
#
def convert(value, T):
    '''Convert value to the given type.

    It raises a TypeError if no conversion is possible and a ValueError if
    conversion is possible in general, but not for the specific value given.

    Example
    -------

    >>> convert(42, float)
    42.0
    >>> convert('42', float)
    Traceback (most recent call last):
    ...
    TypeError: cannot convert 'str' to 'float'

    '''

    if value.__class__ is T:
        return value

    try:
        converter = get_conversion(value.__class__, T)
        return converter(value)
    except ValueError:
        if isinstance(value, T):
            return value
        raise


def get_conversion(from_type, to_type):
    '''Return a function that converts from input type to the given output
    type'''

    # Look up in dictionary
    try:
        return CONVERT_FUNCTIONS[from_type, to_type]
    except KeyError:
        if issubclass(to_type, from_type):
            return do_nothing

    # Handle key error
    if not (isinstance(from_type, type) and isinstance(to_type, type)):
        fmt = type(from_type).__name__, type(to_type).__name__
        raise ValueError('expect types, got: (%s, %s)' % fmt)
    fmt = from_type.__name__, to_type.__name__
    msg = "cannot convert '%s' to '%s'" % fmt
    raise TypeError(msg)


def set_conversion(from_type, to_type, function=None):
    '''Register a function that converts between the two given types.

    Can be used as a decorator as in::

        @set_conversion(int, float)
        def int_to_float(x):
            return float(x)

    '''

    # Decorator form
    if function is None:
        def decorator(func):
            set_conversion(from_type, to_type, func)
            return func
        return decorator

    # Forbid redefinitions
    if (from_type, to_type) in CONVERT_FUNCTIONS:
        fmt = from_type.__name__, to_type.__name__
        raise ValueError('cannot overwrite convertion from %s to %s' % fmt)

    CONVERT_FUNCTIONS[from_type, to_type] = function
