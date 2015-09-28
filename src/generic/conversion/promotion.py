'''
Define the promote() function and friends.
'''

from . import get_conversion

PROMOTION_FUNCTIONS = {}
PROMOTION_RULES = {}

__all__ = ['promote', 'get_promotion', 'set_promotion', 'set_promotion_rule',
           'promote_type']


def promote(x, y, *args):
    '''Promote x and y to a common type.

    Example
    -------

    >>> promote(1, 3.14)
    (1.0, 3.14)
    >>> promote(1, 2, 3.0)
    (1.0, 2.0, 3.0)
    '''

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
    '''Return a promotion of many elements to the most generic type

    Example
    -------

    >>> _promote_values(1, 2, 3.0)
    (1.0, 2.0, 3.0)
    '''

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
    '''Return a function f(x, y) that returns a tuple (X, Y) with the promoted
    versions of x and y. Both outputs X and Y have the same value.

    Raises a TypeError if no promotion function is found'''

    # Check the promotions dictionary
    try:
        return PROMOTION_FUNCTIONS[T1, T2]
    except KeyError:
        pass

    # Check if types are the same
    if T1 is T2:
        return T1

    # Look for a promotion rule for a base type
    rules = PROMOTION_FUNCTIONS
    valid = []
    for ti in T1.mro():
        for tj in T2.mro():
            if (ti, tj) in rules and (tj, ti) not in valid:
                valid.append((ti, tj))

    # No valid rules found
    if not valid:
        aux = (T1.__name__, T2.__name__)
        raise TypeError('no promotion rule found for %s and %s' % aux)

    # More than one rule was found
    if len(valid) > 1:
        aux = (T1.__name__, T2.__name__)
        raise TypeError('ambiguous promotion found for %s and %s' % aux)

    # A single promotion was found
    # TODO: cache it?
    return rules[valid[0]]


def set_promotion(T1, T2, function=None, symmetric=True,
                  outtype=None):
    '''Define the promotion rule for the pair of types (T1, T2).

    It is usually more convenient to use the set_promotion_rule() function.
    Otherwise the user must take care of the order of arguments and manual
    conversions.

    Parameters
    ----------

    T1, T2: type
        The two input types the promotion function relates to
    function : callable
        A function f(x, y) --> (X, Y) that performs the promotion.
    symmetric : bool
        If True (default), the promotion is considered to be symmetric: i.e.,
        promotion for (T2, T1) is given calling f(y, x)
    outtype : type
        Optional type of the promotion. It is considered to be a bad practice
        to define a promotion that may return a different type depending on the
        argument values. This optional parameters tells the expected output
        type for the given promotion. This information may be useful by other
        functions in order to make stronger assumptions about promotions.
    '''

    # Decorator form
    if function is None:
        def decorator(func):
            set_promotion(T1, T2, func)
            return func
        return decorator

    if (T1, T2) in PROMOTION_FUNCTIONS:
        out_name = outtype.__name__ if outtype else (function.__name__ + '()')
        fmt = T1.__name__, T2.__name__, out_name
        raise RuntimeError(
            'cannot overwrite promotion rule: (%s, %s) --> %s' % fmt)

    PROMOTION_FUNCTIONS[T1, T2] = function

    if symmetric:
        def reverse_function(x, y):
            y, x = function(y, x)
            return x, y

        PROMOTION_FUNCTIONS[T2, T1] = reverse_function


def set_promotion_rule(T1, T2, T3):
    '''Set the simple promotion rule for when the promotion from type T1 with
    type T2 is a simple convertion to type T3.

    Usually T3 is one of T1 or T2, but this is not necessary. The user does
    not have to specify the symmetric promotion (T2, T1) to T3.'''

    # Check types
    if (T1, T2) in PROMOTION_FUNCTIONS or (T2, T1) in PROMOTION_FUNCTIONS:
        fmt = T1.__name__, T2.__name__, T3.__name__
        raise RuntimeError(
            'cannot overwrite promotion rule: (%s, %s) --> %s' % fmt)

    # Check trivial promotion
    if T1 is T2 and T2 is T3:
        def do_nothing(x, y):
            return (x, y)
        PROMOTION_FUNCTIONS[T1, T2] = PROMOTION_FUNCTIONS[T2, T1] = do_nothing
        return

    # Saves the direct promotion T1, T2 -> T3
    convert13 = get_conversion(T1, T3)
    convert23 = get_conversion(T2, T3)

    if T3 is T1:
        def promote_direct(x, y):
            return (x, convert23(y))
    elif T3 is T2:
        def promote_direct(x, y):
            return (convert13(x), y)
    else:
        def promote_direct(x, y):
            x = convert13(x)
            y = convert23(y)
            return (x, y)

    # Saves the reverse promotion T2, T1 -> T3
    PROMOTION_RULES[T2, T1] = T3

    if T3 is T1:
        def promote_reverse(x, y):
            return (convert23(y), x)
    elif T3 is T2:
        def promote_reverse(x, y):
            return (y, convert13(x))
    else:
        def promote_reverse(x, y):
            return (convert23(y), convert13(x))

    PROMOTION_FUNCTIONS[T1, T2] = promote_direct
    PROMOTION_FUNCTIONS[T2, T1] = promote_reverse
    PROMOTION_RULES[T1, T2] = T3
    PROMOTION_RULES[T2, T1] = T3


def promote_type(T1, T2):
    '''Return the output type for the promotion rule with types T1 and T2'''

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
