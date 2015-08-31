'''
Created on 13/08/2015

@author: chips
'''
import operator as op
from generic.core import generic


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
    operator = generic(func)
    operator.__doc__ += (
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


#
# Classes
#
class ArithmeticGeneric(object):

    '''Base class for types that dispatch the arithmetic operations to the
    add, sub, mul, etc functions defined in this module. These fuctions can be
    overriden by subclasses, but subclass authors must be carefull to keep the
    same semantics as if the magic functions would only dispatch to the
    corresponding generic. '''

    def __add__(self, other):
        return add_safe(self, other)

    def __radd(self, other):
        return add_safe(other, self)

    def __sub__(self, other):
        return sub_safe(self, other)

    def __rsub(self, other):
        return sub_safe(other, self)

    def __mul__(self, other):
        return mul_safe(self, other)

    def __rmul(self, other):
        return mul_safe(other, self)

    def __div__(self, other):
        return truediv_safe(self, other)

    def __rdiv(self, other):
        return truediv_safe(other, self)


class RelationalGeneric(object):

    '''Base class for types that dispatch the arithmetic operations to the
    add, sub, mul, etc functions defined in this module. These fuctions can be
    overriden by subclasses, but subclass authors must be carefull to keep the
    same semantics as if the magic functions would only dispatch to the
    corresponding generic. '''

    def __gt__(self, other):
        return gt_safe(self, other)

    def __ge__(self, other):
        return ge_safe(self, other)

    def __lt__(self, other):
        return lt_safe(self, other)

    def __le__(self, other):
        return le_safe(self, other)

    def __eq__(self, other):
        return eq_safe(self, other)


class GenericOperators(RelationalGeneric, ArithmeticGeneric):

    '''
    Class that all suitable magic metthods are delegated to the corresponding
    operator generic functions in this module.
    '''

#
# Clean namespace
#
del op, generic, generic_operator, safe_operator


###############################################################################
# Testing: move it to a proper place!
###############################################################################
if __name__ == '__main__':
    class MyInt(ArithmeticGeneric):

        def __init__(self, x):
            self._data = x

        def __eq__(self, other):
            return self._data == other._data

        def __mul__(self, other):
            if isinstance(other, MyInt):
                return MyInt(self._data * other._data)
            else:
                return mul_safe(self, other)

    @add.overload
    def add(x: MyInt, y: MyInt):
        return MyInt(int(x._data + y._data))

    @add.overload
    def add(x: MyInt, y: int):
        return MyInt(int(x._data + y))

    @add.overload
    def add(x: int, y: MyInt):
        return MyInt(int(y._data + x))

    @mul.overload
    def mul(x: MyInt, y: int):
        return MyInt(x._data * y)

    u = MyInt(1)
    v = MyInt(2)
    assert u + v == MyInt(3)
    assert u * v == MyInt(2)
    assert u * 2 == MyInt(2)
    print(u * 2)
