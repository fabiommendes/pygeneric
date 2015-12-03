==========================
Conversions and Promotions
==========================

This module introduces a system for converting objects to different types
and for promoting arguments of mathematical operations to a common type that is
similar to the same concepts found in the Julia language.


Conversions
===========

The :func:`convert` function implements a generic interface for converting
objects between different types. The convert function is called as
``convert(obj, type)`` and attempts to convert ``obj`` to the given type
``type``.


>>> from generic import convert
>>> convert(42, float)
42.0

>>> convert(42, complex)
(42+0j)


The conversion is not guaranteed to succeed. The user may give an argument and
a type for which there are no known conversions. Even when there is a known
conversion for some specific type, it may fail for specific values.


>>> convert('42', float)
Traceback (most recent call last):
...
TypeError: cannot convert 'str' to 'float'

>>> convert(1.5, int)                   # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
...
InexactError: 1.5


It is possible to define custom conversions using the :func:`set_conversion`
decorator. This function is designed to be used with user defined types and one
cannot override existing conversions.

Similarly, :func:`get_conversion(T1, T2)` returns the conversion function
registered for the two types (or raises a TypeError, if the conversion
does not exist).

.. code-block:: python

    from generic import set_conversion

    class MyNum(int):
        pass

    @set_conversion(MyNum, int)
    def conversion(x):
        return int(x) + 1

Now we can call

>>> convert(MyNum(41), int)
42


Promotion
=========

Many mathematical functions of two or more arguments implicitly expect the
arguments to be  of the same type. When one asks for something such as ``41 +
1.0``, the first argument is converted to float before doing the actual
summation in the CPU. In most cases, Python makes these conversions
automatically. However, when dealing with multiple dispatch functions, one often
has to be more explicit.

The promotion mechanism provides a way automate most of these conversions by
trying to find a suitable common type for a tuple of mixed types. Take the
add(x, y) function, for instance. It has a fallback implementation similar to
the one bellow:

.. code-block:: python

    def add_fallback(x, y):
        return add(*promote(x, y))

This tries to convert x and y to a common type that should support additions.
The real implementation is slightly more complicated since it has to prevent
an infinite recursion when the fallback does not exist.

The rationale behind type promotions is that two numeric types should always
try to promote to a common type that is able to represent most values from both
types. This may happen only "optimistically/approximately" such as in
the case of int to float conversions or promotions of integer types with
different bit widths.

We try to follow these rules:
    1) Numerical types which differ only by bitwidth should be converted to
       highest bitwidth. (This is not an issue with Python's builtin numerical
       types, since int's have arbitrary precision).
    2) Signed integers with unsigned integers should be converted to signed
       integers and use the highest bitwidth. Some unsigned values can result in
       failed promotions.
    3) Floats and integers are always promoted to floats.
    4) Reals and complexes are always promoted to complexes.


Defining custom promotions
--------------------------

Promotion rules for basic Python types are already defined. The user can define
promotions for its custom types using the :func:`set_promotion_rule` and
:func:`set_promotion` functions. The first is the most convenient for defining
simple promotions in which arguments of types T1 and T2 are simply converted
to type T3. A simple example is


>>> set_promotion_rule(float, int, float)                       # doctest: +SKIP


Notice that the reciprocal (int, float) --> float is automatically defined.

The :func:`set_promotion` may be required for more complicated promotions which
involves operations other than simple conversions. The previous rule could be
re-written as


>>> @set_promotion(float, int, restype=float)                   # doctest: +SKIP
... def promote_float_int(x, y):
...     # do something complicated
...     return x, float(y)


Here we can assume that the argument types will appear in the given order and
the promotion mechanism automatically creates the function with swapped
arguments.


API Documentation
=================

.. automodule:: generic.conversion
:members: