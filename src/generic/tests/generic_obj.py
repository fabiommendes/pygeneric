'''
Created on 23/09/2015

@author: chips
'''

from generic.operator import *


class MyInt(GenericObject):

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
