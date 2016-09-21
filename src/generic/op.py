"""
Base types for objects that delegate implementations of operations and 
relations to generic functions.
"""
import abc
from generic.core import generic
from generic.errors import raise_no_methods, raise_unordered


__all__ = [
    'Object', 
    
    # Arithmetic
    'add', 'sub', 'mul', 'truediv', 'div', 'floordiv',

    # Relations
    'eq', 'ne', 'gt', 'lt', 'ge', 'le',
]


class Object(object):

    """Base class for types that dispatch all special operations such as 
    arithmetic operations, comparisons, etc to the functions defined in this 
    module. These functions can be overridden by subclasses, but subclass
    authors must be careful to keep the same semantics as if the magic functions
    would only dispatch to the corresponding generic."""

    __slots__ = ()

    #
    # Arithmetic
    #
    def __add__(self, other):
        return add(self, other)

    def __radd__(self, other):
        return add(other, self)

    def __sub__(self, other):
        return sub(self, other)

    def __rsub__(self, other):
        return sub(other, self)
    
    def __mul__(self, other):
        return mul(self, other)

    def __rmul__(self, other):
        return mul(other, self)
    
    def __truediv__(self, other):
        return truediv(self, other)

    def __rtruediv__(self, other):
        return truediv(other, self)
    
    def __floordiv__(self, other):
        return floordiv(self, other)

    def __rfloordiv__(self, other):
        return floordiv(other, self)

    def __mod__(self, other):
        return mod(self, other)

    def __rmod__(self, other):
        return mod(other, self)

    def __divmod__(self, other):
        return divmod(self, other)

    def __rdivmod__(self, other):
        return divmod(other, self)

    def __matmul__(self, other):
        return matmul(self, other)

    def __rmatmul__(self, other):
        return matmul(other, self)

    def __pow__(self, other, mod=None):
        if mod is None:
            return pow(self, other)
        else:
            return pow(self, other, mod)

    def __rpow__(self, other, mod=None):
        if mod is None:
            return pow(other, self)
        else:
            return pow(other, self, mod)

    #
    # Bitwise
    #
    def __and__(self, other):
        return and_(self, other)

    def __rand__(self, other):
        return and_(other, self)

    def __or__(self, other):
        return or_(self, other)

    def __ror__(self, other):
        return or_(other, self)

    def __rshift__(self, other):
        return rshift(self, other)

    def __rrshift__(self, other):
        return rshift(other, self)

    def __lshift__(self, other):
        return lshift(self, other)

    def __rlshift__(self, other):
        return lshift(other, self)

    #
    # Relational operators
    #
    def __eq__(self, other):
        return eq(self, other)
    
    def __gt__(self, other):
        return gt(self, other)
    
    def __lt__(self, other):
        return gt(other, self)

    def __ge__(self, other):
        return gt(self, other)

    def __le__(self, other):
        return gt(other, self)

    #
    # Maybe implement other python protocols
    #
    #... in the future ...
    

class TotalOrdered(metaclass=abc.ABCMeta):
    """Abstract class for all types that obbey a total ordering relation.

    Can register objects a posteriori or inherit from this in order to enable
    a total ordering for the gt, lt, le, ge operators. It is recommended that
    TotalOrdered subclasses implement only the eq and gt relations."""

TotalOrdered.register(int)
TotalOrdered.register(float)


#
# Utility functions (maybe some of them are useful enough to go to 
# pygeneric.util)
#
def _opsame_meta_factory(opname):
    """Returns a factory tha can be used to test if the object implements a 
    __<opname>same__() method"""
    
    samemethod = '__%ssame__' % opname

    def factory(argtypes, restype):
        T1, T2 = argtypes
        if T1 is T2:
            try:
                return getattr(T1, samemethod)
            except AttributeError:
                pass 
        return NotImplemented
        
    return factory


#
# We use a common factory for all arithmetic operators since implementation is 
# really similar.
#
def _arithmetic_op_factory(opname):
    """Creates a generic arithmetic operator with the given name"""

    method = '__%s__' % opname
    rmethod = '__r%s__' % opname
    not_implemented = lambda y: NotImplemented

    @generic
    def op(x, y):
        out = getattr(x, method, not_implemented)(y)
        if out is NotImplemented:
            try:
                return getattr(y, rmethod)(x)
            except AttributeError:
                raise_no_methods(op, args=(x, y))
        return out

    @op.register(Object, object)
    def op_first(x, y):
        try:
            method = getattr(y, rmethod)
        except AttributeError:
            raise_no_methods(op, args=(x, y))
        else:
            return method(x)

    @op.register(object, Object)
    def op_second(x, y):
        out = getattr(x, method, not_implemented)(y)
        if out is NotImplemented:
            raise_no_methods(op, args=(x, y))
        return out

    op.register(Object, Object, func=_opsame_meta_factory(opname), factory=True)
    op.__name__ = opname
    return op

add = _arithmetic_op_factory('add')
sub = _arithmetic_op_factory('sub')
mul = _arithmetic_op_factory('mul')
div = truediv = _arithmetic_op_factory('truediv')
floordiv = _arithmetic_op_factory('floordiv')
mod = _arithmetic_op_factory('mod')
matmul = _arithmetic_op_factory('matmul')
pow = _arithmetic_op_factory('pow')
and_ = _arithmetic_op_factory('and')
or_ = _arithmetic_op_factory('or')
rshift = _arithmetic_op_factory('rshift')
lshift = _arithmetic_op_factory('lshift')


#
# Binary relations
#
def _relational_op_factory(opname, ropname):
    """Creates a generic arithmetic operator with the given name"""

    method = '__%s__' % opname
    rmethod = '__%s__' % ropname

    @generic
    def op(x, y):
        out = getattr(x, method, lambda y: NotImplemented)(y)
        if out is NotImplemented:
            try:
                return getattr(y, rmethod)(x)
            except AttributeError:
                raise_unordered(op, args=(x, y))
        raise_no_methods(op, args=(x, y))

    @op.register(Object, object)
    def op_first(x, y):
        try:
            method = getattr(y, rmethod)
        except AttributeError:
            raise_unordered(op, args=(x, y))
        else:
            return method(x)

    @op.register(object, Object)
    def op_second(x, y):
        out = getattr(x, method, lambda y: NotImplemented)(y)
        if out is NotImplemented:
            raise_unordered(x, y)
        return out

    op.register(Object, Object, func=_opsame_meta_factory(opname), factory=True)
    op.__name__ = opname
    return op

gt = _relational_op_factory('gt', 'lt')
ge = _relational_op_factory('ge', 'le')
lt = _relational_op_factory('lt', 'gt')
le = _relational_op_factory('le', 'ge')


@generic
def eq(x, y):
    # Python 2 does not guarantee that __eq__ operator exists!
    try:
        out = x.__eq__(y)
    except AttributeError:
        out = NotImplemented

    if out is NotImplemented:
        try:
            out = y.__eq__(x)
        except AttributeError:
            out = NotImplemented

    if out is NotImplemented:
        out = x is y
    return out


@eq.register(Object, Object, factory=True)
def _eq_factory(argtypes, restype):
    T1, T2 = argtypes

    # Try subclass relations
    if issubclass(T1, T2):
        try:
            return T2.__eqsame__
        except AttributeError:
            pass
    elif issubclass(T2, T1):
        try:
            return T1.__eqsame__
        except AttributeError:
            pass

    # If we reach here, there are no overloads for (T1, T2), use the default
    # test for object equality
    return lambda x, y: x is y


@eq.register(Object, object)
def eq(x, y):
    out = y.__eq__(x)
    return False if out is NotImplemented else out


@eq.register(object, Object)
def eq(x, y):
    return False


@generic
def ne(x, y):
    # Python 2 does not guarantee that __ne__ operator exists!
    try:
        out = x.__ne__(y)
    except AttributeError:
        out = NotImplemented

    if out is NotImplemented:
        try:
            out = y.__ne__(x)
        except AttributeError:
            out = NotImplemented

    if out is NotImplemented:
        out = not (x == y)
    return out


@ne.register(Object, Object, factory=True)
def _ne_factory(argtypes, restype):
    T1, T2 = argtypes

    # Try subclass relations
    if issubclass(T1, T2):
        try:
            return T2.__nesame__
        except AttributeError:
            pass
    elif issubclass(T2, T1):
        try:
            return T1.__nesame__
        except AttributeError:
            pass

    # If we reach here, there are no overloads for (T1, T2), use the default
    # test for object equality
    return lambda x, y: not (x == y)


@ne.register(Object, object)
def ne(x, y):
    out = y.__ne__(x)
    return not (x == y) if out is NotImplemented else out


@ne.register(object, Object)
def ne(x, y):
    return not (x == y)


#
# Total ordering relations
#
@gt.register(TotalOrdered, TotalOrdered)
def gt(x, y):
    # Python 2 may implement relations using the __cmp__ method.  This is true
    # for builtins, for instance. We have to check all failure points to see
    # if a __cmp__ function is implemented.
    try:
        out = x.__gt__(y)
    except AttributeError:
        if hasattr(x, '__cmp__'):
            return x.__cmp__(y) == 1
        raise RuntimeError('TotalOrdered object does not implement a __gt__ relation')
    if out is NotImplemented:
        try:
            out = y.__lt__(x)
        except AttributeError:
            if hasattr(x, '__cmp__'):
                return y.__cmp__(x) == -1
            out = NotImplemented
    if out is NotImplemented:
        raise_unordered(x, y)
    return out


@lt.register(TotalOrdered, TotalOrdered)
def lt(x, y):
    return (not x > y) and x != y


@ge.register(TotalOrdered, TotalOrdered)
def ge(x, y):
    return x > y or x == y


@le.register(TotalOrdered, TotalOrdered)
def le(x, y):
    return x < y or x == y
