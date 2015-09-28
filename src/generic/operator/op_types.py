'''
Base types for objects that delegate implementations to generic functions
'''

from .operators import (
    add_safe, sub_safe, mul_safe, truediv_safe,
    eq_safe, le_safe, lt_safe, ge_safe, gt_safe
)


class GenericArithmetic(object):

    '''Base class for types that dispatch the arithmetic operations to the
    add, sub, mul, etc functions defined in this module. These fuctions can be
    overriden by subclasses, but subclass authors must be carefull to keep the
    same semantics as if the magic functions would only dispatch to the
    corresponding generic. '''

    __slots__ = ()

    def __add__(self, other):
        if isinstance(other, type(self)):
            return self.__add_similar__(other)
        else:
            try:
                return add_safe(self, other)
            except TypeError:
                return NotImplemented

    def __add_similar__(self, other):
        return add_safe(self, other)

    def __radd(self, other):
        return add_safe(other, self)

    def __sub__(self, other):
        if isinstance(other, type(self)):
            return self.__sub_similar__(other)
        else:
            try:
                return sub_safe(self, other)
            except TypeError:
                return NotImplemented

    def __sub_similar__(self, other):
        return sub_safe(self, other)

    def __rsub(self, other):
        return sub_safe(other, self)

    def __mul__(self, other):
        if isinstance(other, type(self)):
            return self.__mul_similar__(other)
        else:
            try:
                return mul_safe(self, other)
            except TypeError:
                return NotImplemented

    def __mul_similar__(self, other):
        return mul_safe(self, other)

    def __rmul(self, other):
        return mul_safe(other, self)

    def __truediv__(self, other):
        if isinstance(other, type(self)):
            return self.__div_similar__(other)
        else:
            try:
                return truediv_safe(self, other)
            except TypeError:
                return NotImplemented

    def __truediv_similar__(self, other):
        return truediv_safe(self, other)

    def __rtruediv__(self, other):
        return truediv_safe(other, self)


class GenericRelational(object):

    '''Base class for types that dispatch the arithmetic operations to the
    add, sub, mul, etc functions defined in this module. These fuctions can be
    overriden by subclasses, but subclass authors must be carefull to keep the
    same semantics as if the magic functions would only dispatch to the
    corresponding generic. '''

    __slots__ = ()

    def __gt__(self, other):
        if isinstance(other, type(self)):
            return self.__gt_similar__(other)
        return gt_safe(self, other)

    def __ge__(self, other):
        if isinstance(other, type(self)):
            return self.__ge_similar__(other)
        return ge_safe(self, other)

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.__lt_similar__(other)
        return lt_safe(self, other)

    def __le__(self, other):
        if isinstance(other, type(self)):
            return self.__lt_similar__(other)
        return le_safe(self, other)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.__eq_similar__(other)
        return eq_safe(self, other)


class GenericObject(GenericRelational, GenericArithmetic):

    '''
    Class that all suitable magic metthods are delegated to the corresponding
    operator generic functions in this module.
    '''

    __slots__ = ()
