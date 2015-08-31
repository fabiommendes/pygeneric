'''
Global functions that register/control conversion between scalar types. This
model is based on Julia's approach to explicit conversions between types.
'''

CONVERT_RULES = {}
PROMOTION_RULES = {}
_type = type

#
# Conversion between numerical types
#


def convert(value, type):
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

    # Fast track common conversions
    t_value = _type(value)
    if t_value is type:
        return value
    elif t_value is int and type is float:
        return float(value)

    converter = get_converter_function(t_value, type)
    return converter(value)


def get_converter_function(from_type, to_type):
    '''Return a function that converts from input type to the given output
    type'''

    # Look up in dictionary
    try:
        return CONVERT_RULES[from_type, to_type]
    except KeyError:
        pass

    # Handle key error
    fmt = from_type.__name__, to_type.__name__
    raise TypeError("cannot convert '%s' to '%s'" % fmt)


def set_converter_function(from_type, to_type, function=None):
    '''Register a function that converts between the two given types.

    Can be used as a decorator as in::

        @set_converter_function(int, float)
        def int_to_float(x):
            return float(x)

    '''

    # Decorator form
    if function is None:
        def decorator(func):
            return set_converter_function(from_type, to_type, func)
        return decorator

    # Forbid redefinitions
    if (from_type, to_type) in CONVERT_RULES:
        fmt = from_type.__name__, to_type.__name__
        raise ValueError('cannot overwrite convertion from %s to %s' % fmt)

    CONVERT_RULES[from_type, to_type] = function


def convert_list(L, type):
    '''Return a list of all elements of the given sequence converted to the
    given type

    Example
    -------

    >>> convert_list([1, 2, 3.0], float)
    [1.0, 2.0, 3.0]
    '''

    func = convert
    return [func(x, type) for x in L]


#
# Promotion rules
#
def promote(x, y):
    '''Promote x and y to a common type.

    Example
    -------

    >>> promote(1, 3.14)
    (1.0, 3.14)
    '''

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
    promote_func = get_promotion_function(x_type, y_type)
    return promote_func(x, y)


def get_promotion_function(T1, T2):
    '''Promote two types to the type which has highest resolution. Raises a
    TypeError if no promotion is found'''

    # Check the promotions dictionary
    try:
        return PROMOTION_RULES[T1, T2]
    except KeyError:
        pass

    # Check if types are the same
    if T1 is T2:
        return T1

    # Look for a promotion rule for a base type
    rules = PROMOTION_RULES
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


def set_promotion_function(T1, T2, function=None):
    '''Define the promotion rule for the pair of types (T1, T2).

    It is usually more convenient to use the set_promotion_rule() function.
    Otherwise the user must take care of the order of arguments and manual
    conversions.'''

    # Decorator form
    if function is None:
        def decorator(func):
            return set_promotion_function(T1, T2, func)
        return decorator

    if (T1, T2) in PROMOTION_RULES:
        fmt = T1.__name__, T2.__name__
        raise RuntimeError('cannot overwrite promotion rule: %s' % fmt)

    PROMOTION_RULES[T1, T2] = function


def set_promotion_rule(T1, T2, T3):
    '''Set the simple promotion rule for when the promotion from type T1 with
    type T2 is convertion to type T3.'''

    # Check types
    if (T1, T2) in PROMOTION_RULES or (T2, T1) in PROMOTION_RULES:
        fmt = T1.__name__, T2.__name__
        raise RuntimeError('cannot overwrite promotion rule: %s' % fmt)

    # Check trivial promotion
    if T1 is T2 and T2 is T3:
        do_nothing = lambda x, y: (x, y)
        PROMOTION_RULES[T1, T2] = PROMOTION_RULES[T2, T1] = do_nothing
        return

    # Saves the direct promotion T1, T2 -> T3
    if T3 is T1:
        def promote_direct(x, y):
            return (x, convert(y, T3))
    elif T3 is T2:
        def promote_direct(x, y):
            return (convert(x, T3), y)
    else:
        def promote_direct(x, y):
            x = convert(x, T3)
            y = convert(y, T3)
            return (x, y)

    # Saves the reverse promotion T2, T1 -> T3
    if T3 is T1:
        def promote_reverse(x, y):
            return (convert(y, T3), y)
    elif T3 is T2:
        def promote_reverse(x, y):
            return (x, convert(x, T3))
    else:
        promote_reverse = promote_direct

    PROMOTION_RULES[T1, T2] = promote_direct
    PROMOTION_RULES[T2, T1] = promote_reverse


def promote_list(L):
    '''Return a list of all elements of the given sequence promoted to the
    most generic type

    Example
    -------

    >>> promote_list([1, 2, 3.0])
    [1.0, 2.0, 3.0]
    '''

    elements = iter(L)
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

    return out

###############################################################################
#                  Common conversions & promotions
###############################################################################
#
# This section defines common convertion and promotion rules for numeric types.
# The conversion mechanism is used for arithmetic operations in objects that
# support it.
#
# All arithmetic functions such as add(x, y) have a fallback mechanism that
# works similarly as the implementation bellow:
#
#     def add(x, y):
#         return add(*promote(x, y))
#
# This tries to convert x and y to a common type that should support arithmetic
# operations. There is only a caveat that when (x, y) are of the same type
# which does not support addition, an error must be raised.
#
# The rationale behind the promotion functions is that two numeric types should
# (as long as possible) be converted to a common type able to represent most
# of the values from both types. This may happen only "approximatelly" such as
# in the case of int to float conversions.
#
# We try to follow these rules:
#     1) Numerical types which differ only by bit width should be converted to
#        highest bit width
#     2) Signed integers with unsigned integers should be converted to signed
#        integers of the highest bitwidth
#     3) Floats and integers are always converted to floats
#     4) Reals and complexes are always converted to complexes
#

#
# Conversion rules
#
set_converter_function(int, float, float)
set_converter_function(int, complex, complex)
set_converter_function(float, complex, complex)

#
# Promotion rules
#
set_promotion_rule(int, float, float)
set_promotion_rule(int, complex, complex)
set_promotion_rule(float, complex, complex)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
