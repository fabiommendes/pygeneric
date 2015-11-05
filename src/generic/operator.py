'''
Base types for objects that delegate implementations of operations and 
relations to generic functions.
'''
from __future__ import absolute_import # Avoid conflict with operator module in Py2
import operator
from . import generic
from .util import raise_no_methods, get_no_methods_error, raise_unordered


class Object(object):

    '''Base class for types that dispatch all special operations such as 
    arithmetic operations, comparisons, etc to the functions defined in this 
    module. These fuctions can be overriden by subclasses, but subclass authors 
    must be carefull to keep the same semantics as if the magic functions 
    would only dispatch to the corresponding generic.'''

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
    
    #
    # Relational operators
    #
    def __eq__(self, other):
        return eq(self, other)
    
    def __eqsame__(self, other):
        return self is other
    
    def __gt__(self, other):
        return gt(self, other)
    
    def __lt__(self, other):
        return gt(other, self)

    # Fallback methods for ordering relations. The user must defined them
    # to specify a concrete ordering between types
    def __gtsame__(self, other):
        raise_unordered(self, other)

    #
    # Maybe implement other python protocols
    #
    #... in the future ...
    
    
#
# Utility functions (maybe some of them are useful enough to go to 
# pygeneric.util)
#
def _not_implemented_factory(generic, argtypes):
    '''Return a function that raises a TypeError when called'''

    error = get_no_methods_error(generic, types=argtypes)    
    
    def not_implemented_method(*args, **kwds):
        raise error
    
    not_implemented_method.implemented = False
    return not_implemented_method


def _opsame_not_implemented_factory(name, argtypes):
    '''Return a function that raises a TypeError when called'''
    
    T = argtypes[0]
        
    def not_implemented_method(*args, **kwds):
        raise TypeError('please implement __%ssame__() on %r in order to support this operation' % (name, T.__name__))
    
    not_implemented_method.implemented = False
    return not_implemented_method


def _opsame_meta_factory(opname):
    '''Returns a factory tha can be used to test if the object implements a 
    __<opname>same__() method'''
    
    samemethod = '__%ssame__' % opname

    def factory(argtypes, restype):
        print(argtypes)
        T1, T2 = argtypes
        if T1 is T2:
            try:
                return getattr(T1, samemethod)
            except AttributeError:
                return _opsame_not_implemented_factory(opname, argtypes) 
        else:
            return _not_implemented_factory(add, (T1, T2))
    
    return factory


#
# We use a common factory for all arithmetic operators since implementation is 
# really similar.
#
def _arithmetic_op_factory(opname):
    '''Creates a generic arithmetic operator with the given name'''
    
    method = '__%s__' % opname
    rmethod = '__r%s__' % opname
    
    @generic
    def op(x, y):
        if isinstance(x, Object):
            raise_no_methods(op, args=(x, y))
        
        # Try the direct x.__op__(y) method. If it succeeds, we return. 
        # It could fail with an AttributeError or returning NotImplemented.
        out =  getattr(x, method, lambda y: NotImplemented)(y)
        if out is not NotImplemented:
            return out
        
        # If the direct call fails, try y.__rop__(x)
        if isinstance(y, Object):
            raise_no_methods(op, args=(x, y))
        try:
            return getattr(y, rmethod)(x)
        except AttributeError:
            raise_no_methods(op, args=(x, y))
    
    
    op.factory(Object, Object, func=_opsame_meta_factory(opname))
    op.__name__ = opname 
    return op

add = _arithmetic_op_factory('add')
sub = _arithmetic_op_factory('sub')
mul = _arithmetic_op_factory('mul')
div = truediv = _arithmetic_op_factory('truediv')
floordiv = _arithmetic_op_factory('floordiv')


#
# Binary relations are simple enough that we do not need an specialized factory
#
# We start with a baseline
eq = generic(operator.eq)
gt = generic(operator.gt)

# Non-overloadables: in the future we should add a freeze() method to generic
# functions and create a frozen operator in order to keep the API consistent
# Ideally there should be an error message telling which operator should be
# overriden.  
ne = operator.ne
ge = operator.ge
le = operator.le
lt = operator.lt 

# Make overrides for (Object, Object) calls
eq.factory(Object, Object, func=_opsame_meta_factory('eq'))
gt.factory(Object, Object, func=_opsame_meta_factory('gt'))