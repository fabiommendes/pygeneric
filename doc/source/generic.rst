=======================================
Generic functions and multiple dispatch
=======================================

Generic functions
=================


Example
-------

>>> @generic
... def f(x, y):
...     return x + y + 3.14

Python 3

>>> @overload(f)                                               # doctest: +SKIP
... def f(x:int, y:int):
...     return x + y + 3


Python 2 and 3

>>> @f.overload([int, int])
... def f(x, y):
...     return x + y + 3


>>> f(0, 0)
3
>>> f(0.0, 0.0)
3.14


API Documentation
=================

.. automodule::generic.generic
    :members: generic, overload, Generic