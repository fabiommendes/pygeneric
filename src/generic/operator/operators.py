'''
Generic functions implementing mathematical operators.
'''

import operator as op
from .. import generic, promote


def safe_operator(op):
    '''Factory function that creates a <op>_safe version of the given
    operator.

    The safe versions should always be used in the implementation of magic
    methods, otherwise an infinite recursion can occur.'''

    cache = {}

    def safe_op(x, y):
        '''Safe version of %s(x, y) that is userful in class implementations.

        Differently from %s(x, y), this function does not fallback the
        standard python path and immediately raises an error if no methods
        are found.

        This prevents an infinite recursion in which, for instance,
        ``Foo.__add__(x, y)`` calls ``add(x, y)``, which falls back to ``x +
        y`` which in turn calls ``Foo.__add__(x, y)`` again. The magic
        methods should always call the safe_operator versions of the
        arithmetic operators.
        '''

        # Fetch object types
        T1 = type(x)
        T2 = type(y)

        # Try happy ending: getting objects from cache
        try:
            method = cache[T1, T2]
        except KeyError:
            pass
        else:
            return method(x, y)

        # Update cache using the original generic function cache
        method = op[T1, T2]
        default = op[object, object]
        if method is default:
            fmt = name, type(x).__name__, type(y).__name__
            raise TypeError('no methods found for %s(%s, %s)' % fmt)
        else:
            cache[T1, T2] = method
            return method(x, y)

    # Update docstring
    name = op.__name__
    safe_op.__doc__ = safe_op.__doc__ % (name, name)
    return safe_op


def generic_operator(func):
    '''Creates a generic operator from function in the operator module'''

    name = func.__name__
    fmt = name, name, name

    @generic
    def operator(x, y):
        try:
            return func(x, y)
        except:
            if not isinstance(x, type(y)):
                new_x, new_y = promote(x, y)
                if not (new_x is x) and (new_y is y):
                    return operator(new_x, new_y)
            raise TypeError(type(x), type(y))

    operator.__name__ = name
    operator.__doc__ = func.__doc__ + (
        '\n\n'
        'Note to class implementators: use %s_safe() instead of %s() as\n'
        'the fallback method inside the __%s__ magic method.') % fmt

    return operator


#
# Create operators
#

# Arithmetic functions
add = generic_operator(op.add)
add_safe = safe_operator(add)
sub = generic_operator(op.sub)
sub_safe = safe_operator(sub)
mul = generic_operator(op.mul)
mul_safe = safe_operator(mul)
truediv = generic_operator(op.truediv)
truediv_safe = safe_operator(truediv)

# Comparison
eq = generic_operator(op.eq)
eq_safe = safe_operator(eq)
ne = generic_operator(op.ne)
ne_safe = safe_operator(ne)
gt = generic_operator(op.gt)
gt_safe = safe_operator(gt)
ge = generic_operator(op.ge)
ge_safe = safe_operator(ge)
lt = generic_operator(op.lt)
lt_safe = safe_operator(lt)
le = generic_operator(op.le)
le_safe = safe_operator(le)


# Clean namespace
del op, generic, generic_operator, safe_operator, promote
