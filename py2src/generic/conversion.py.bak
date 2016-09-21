"""
Conversion and promotion between types.
"""
from . import ABCMeta
from .errors import InexactError
__all__ = [
    # Conversions
    'convert', 'get_conversion', 'set_conversion',

    # Promotions
    'promote', 'get_promotion', 'set_promotion', 'set_promotion_rule',
    'promote_type',
]

# In Python 2 we have to handle new style vs old style classes
Type = set([type])
class _cls:
    pass
Type.add(_cls)
Type = tuple(Type)


#
# Define the convert() function and friends.
#
CONVERT_FUNCTIONS = {}


def _do_nothing(x):
    """A function that does nothing and returns its argument"""

    return x


def convert(value, T):
    """Convert *value* to the given type *T*.

    It raises a TypeError if no conversion is possible and a ValueError if
    conversion is possible in general, but not for the specific value given.

    Examples
    --------

    >>> convert(42, float)
    42.0
    >>> convert('42', float)
    Traceback (most recent call last):
    ...
    TypeError: cannot convert 'str' to 'float'

    """

    if value.__class__ is T:
        return value

    try:
        converter = get_conversion(value.__class__, T)
        return converter(value)
    except TypeError:
        if isinstance(value, T):
            return value
        raise


def get_conversion(from_type, to_type):
    """Return a function that converts from input type to the given output
    type"""

    # Look up in dictionary
    try:
        return CONVERT_FUNCTIONS[from_type, to_type]
    except KeyError:
        try:
            if issubclass(to_type, from_type):
                return _do_nothing
        except TypeError:
            raise ValueError('not types: %r, %r' % (from_type, to_type))

    # Handle key error
    if not (isinstance(from_type, Type) and isinstance(to_type, Type)):
        print(Type)
        fmt = type(from_type).__name__, type(to_type).__name__
        raise ValueError('not types: %r, %r' % (from_type, to_type))
    fmt = from_type.__name__, to_type.__name__
    msg = "cannot convert '%s' to '%s'" % fmt
    raise TypeError(msg)


def set_conversion(from_type, to_type, function=None):
    """Register a function that converts between the two given types.


    Examples
    --------

    Can be used as a decorator as in::

        @set_conversion(int, float)
        def int_to_float(x):
            return float(x)

    Now, the integer to floats are handled by the  int_to_float() function,
    i.e.,

    ::
        convert(42, float) <==> int_to_float(42)
    """

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


#
# Define the promote() function and friends.
#
PROMOTION_FUNCTIONS = {}
PROMOTION_RULES = {}


def promote(x, y, *args):
    """Promote x and y to a common type.

    Parameters
    ----------

    This function accept any number of parameters and return the result of
    promotion for all the collected types.

    Returns
    -------

    A tuple with the resulting promotions.

    Examples
    --------

    >>> promote(1, 3.14)
    (1.0, 3.14)
    >>> promote(1, 2, 3.0)
    (1.0, 2.0, 3.0)
    """

    if args:
        return _promote_values(x, y, *args)
    x_type = type(x)
    y_type = type(y)

    # Fast track common types and patterns
    if x_type is y_type:
        return (x, y)
    if x_type is float and y_type is int:
        return x, float(y)
    if x_type is int and y_type is float:
        return float(x), y

    # Generic track for all other types
    promote_func = get_promotion(x_type, y_type)
    return promote_func(x, y)


def _promote_values(*args):
    """Return a promotion of many elements to the most generic type

    Examples
    --------

    >>> _promote_values(1, 2, 3.0)
    (1.0, 2.0, 3.0)
    """

    elements = iter(args)
    out = [next(elements)]

    # Go back and forth doing all promotions
    for x in elements:
        x, y = promote(x, out[-1])
        out[-1] = y
        out.append(x)

    N = len(out)
    for i in range(N - 2, -1, -1):
        x, y = promote(out[i], out[i + 1])
        out[i] = x
        out[i + 1] = y

    return tuple(out)


def get_promotion(T1, T2):
    """Return a function f(x, y) that returns a tuple (X, Y) with the promoted
    versions of x and y. Both outputs X and Y have the same value.

    Raises a TypeError if no promotion function is found"""

    # Check the promotions dictionary
    try:
        return PROMOTION_FUNCTIONS[T1, T2]
    except KeyError:
        pass

    # Check if types are the same
    if T1 is T2:
        return T1

    # Look for a promotion rule for a base type
    return _compute_promotions(T1, T2)


def _compute_promotions(T1, T2):
    """Compute the valid promotions for types T1 and T2, assuming they are not
    present in the PROMOTION_FUNCTIONS dictionary."""

    rules = PROMOTION_FUNCTIONS
    valid = []
    for ti in T1.mro():
        for tj in T2.mro():
            if (ti, tj) in rules and (tj, ti) not in valid:
                valid.append((ti, tj))

    # No rule were found
    if not valid:
        if issubclass(T1, T2):
            # Try to convert to subtype
            def promotion(x, y):
                try:
                    return x, convert(y, T1)
                except TypeError:
                    return x, y

            return promotion
        elif issubclass(T2, T1):
            return get_promotion(T2, T1)
        else:
            aux = (T1.__name__, T2.__name__)
            raise TypeError('no promotion rule found for %s and %s' % aux)

    # More than one rule was found
    elif len(valid) > 1:
        aux = (T1.__name__, T2.__name__)
        raise TypeError('ambiguous promotion found for %s and %s' % aux)

    # A single promotion was found
    else:
        # TODO: cache it?
        return rules[valid[0]]


def set_promotion(T1, T2, *,
                  function=None, symmetric=True, restype=None):
    """Define the promotion rule for the pair of types (T1, T2).

    It is usually more convenient to use the set_promotion_rule() function.
    Otherwise the user must take care of the order of arguments and manual
    conversions.

    Parameters
    ----------

    T1,T2: type
        The two input types the promotion function relates to
    function : callable
        A function f(x, y) --> (X, Y) that performs the promotion.
    symmetric : bool
        If True (default), the promotion is considered to be symmetric: i.e.,
        promotion for (T2, T1) is given calling f(y, x)
    restype : type
        Optional type of the promotion. It is considered to be a bad practice
        to define a promotion that may return a different type depending on the
        argument values. This optional parameters tells the expected output
        type for the given promotion. This information may be useful by other
        functions in order to make stronger assumptions about promotions.
    """

    # Decorator form
    if function is None:
        def decorator(func):
            set_promotion(T1, T2, function=func)
            return func
        return decorator

    # Check if promotion is valid
    if T1 is T2 and not isinstance(T1, ABCMeta):
        raise RuntimeError('cannot set a promotion rule for identical contrete types.')
    if (T1, T2) in PROMOTION_FUNCTIONS or (symmetric and (T2, T1) in PROMOTION_FUNCTIONS):
        out_name = restype.__name__ if restype else (function.__name__ + '()')
        fmt = T1.__name__, T2.__name__, out_name
        msg = 'cannot overwrite promotion rule: (%s, %s) --> %s' % fmt
        raise RuntimeError(msg)

    PROMOTION_FUNCTIONS[T1, T2] = function
    PROMOTION_RULES[T1, T2] = restype
    if symmetric:
        def reverse_function(x, y):
            y, x = function(y, x)
            return x, y
        PROMOTION_FUNCTIONS[T2, T1] = reverse_function
        PROMOTION_RULES[T2, T1] = restype


def set_promotion_rule(T1, T2, T3):
    """Set the simple promotion rule for when the promotion from type T1 with
    type T2 is a simple convertion to type T3.

    Usually T3 is one of T1 or T2, but this is not necessary. The user does
    not have to specify the symmetric promotion (T2, T1) to T3."""

    # Check types
    if (T1, T2) in PROMOTION_FUNCTIONS or (T2, T1) in PROMOTION_FUNCTIONS:
        fmt = T1.__name__, T2.__name__, T3.__name__
        raise RuntimeError(
            'cannot overwrite promotion rule: (%s, %s) --> %s' % fmt)

    # Check trivial promotion
    if T1 is T2:
        raise RuntimeError('cannot set a promotion rule for identical types.')

    # Saves the direct promotion T1, T2 -> T3
    convert13 = get_conversion(T1, T3)
    convert23 = get_conversion(T2, T3)

    if T1 is T3:
        def promote_direct(x, y):
            return (x, convert23(y))

        def promote_reverse(y, x):
            return (convert23(y), x)

    elif T2 is T3:
        def promote_direct(x, y):
            return (convert13(x), y)

        def promote_reverse(y, x):
            return (y, convert13(x))

    else:
        def promote_direct(x, y):
            x = convert13(x)
            y = convert23(y)
            return (x, y)

        def promote_reverse(y, x):
            x = convert13(x)
            y = convert23(y)
            return (y, x)

    PROMOTION_FUNCTIONS[T1, T2] = promote_direct
    PROMOTION_FUNCTIONS[T2, T1] = promote_reverse
    PROMOTION_RULES[T1, T2] = T3
    PROMOTION_RULES[T2, T1] = T3


def promote_type(T1, T2):
    """Return the output type for the promotion rule with types T1 and T2"""

    try:
        return PROMOTION_RULES[T1, T2]
    except KeyError:
        if issubclass(T1, T2):
            return T2
        elif issubclass(T2, T1):
            return T1
        else:
            fmt = T1.__name__, T2.__name__
            raise TypeError('no promotion rule for (%s, %s)' % fmt)


#
# Conversion rules
#
set_conversion(int, float, float)
set_conversion(int, complex, complex)
set_conversion(float, complex, complex)
set_conversion(bool, int, int)
set_conversion(bool, float, float)
set_conversion(bool, complex, complex)


@set_conversion(float, bool)
@set_conversion(int, bool)
@set_conversion(complex, bool)
def number2bool(x):
    if x == 0:
        return False
    elif x == 1:
        return True
    else:
        raise InexactError(x)


@set_conversion(complex, int)
@set_conversion(float, int)
def number2int(x):
    out = int(x)
    if out == x:
        return out
    else:
        raise InexactError(x)

#

# Promotion rules
#
set_promotion_rule(int, float, float)
set_promotion_rule(int, complex, complex)
set_promotion_rule(float, complex, complex)
set_promotion_rule(bool, int, int)
set_promotion_rule(bool, float, float)
set_promotion_rule(bool, complex, complex)
