'''
==========================
Conversions and Promotions
==========================

This module introduces a system for converting objects to different types
and for promoting arguments of mathematical operations to a common type that is
similar to the same concepts in the Julia language.


Conversions
===========

The :func:`convert` function implements a generic interface for converting
objects between different types. The convert function is called as
``convert(obj, type)`` and attempts to convert ``obj`` to the given type
``type``.

    >>> convert(42, float)
    42.0

    >>> convert(42, complex)
    (42+0j)

The conversion is not guaranteed to succeed. The user may give an argument and
a type for which there are no known conversions and even when there is a known
conversion for some specific type it may fail for specific values.

    >>> convert('42', float)
    Traceback (most recent call last):
    ...
    TypeError: cannot convert 'str' to 'float'

    >>> convert(1.5, int)
    Traceback (most recent call last):
    ...
    generic.errors.InexactError: 1.5


The user may specify custom conversions using the :func:`set_conversion`
decorator. This function is designed to be used with user defined types and one
cannot override an existing conversion.

Similarly, the :func:`get_conversion(T1, T2)` function returns the conversion
function registered for the two given types (or raises a TypeError, if the
conversion does not exist).


Promotion
=========

Many mathematical functions of two or more arguments implicitly expect that the
arguments are of the same type. When one asks for something such as ``41 +
1.0``, the first argument is converted under the hood to float before doing the
summation. In most cases, Python makes these conversions automatically.
However, when dealing with multiple dispatch function, one often has to perform
then explicitly.

The promotion mechanism provides a way automate most of these conversions by
trying to find a suitable common type for a tuple of mixed types. Take the
add(x, y) function for instance. It has a fallback implementation similar to
the one bellow::

    def add_fallback(x, y):
        return add(*promote(x, y))

This tries to convert x and y to a common type that should support additions.
The real implementation is slightly more complicated since it has to prevent
an infinite recursion when the fallback does not exist.

The rationale behind type promotions is that two numeric types should always
try to promote to a common type able to represent most of the values from both
types. This may happen only "approximatelly" such as in the case of int to
float conversions or may be strictly guaranteed for, e.g., promotions of
integer types with different bit widths.

We try to follow these rules:
    1) Numerical types which differ only by bitwidth should be converted to
       highest bitwidth
    2) Signed integers with unsigned integers should be converted to signed
       integers of the highest bitwidth
    3) Floats and integers are always converted to floats
    4) Reals and complexes are always converted to complexes


Defining custom promotions
--------------------------

Promotion rules for basic Python types are already defined. The user can define
promotions for its custom types using the :func:`set_promotion_rule` and
:func:`set_promotion` functions. The first is the most convenient for defining
simple promotions in which arguments of types T1 and T2 are simply converted
to type T3. A simple example is

    >>> set_promotion_rule(float, int, float)                  # doctest: +SKIP

Notice that the reciprocal (int, float) --> float does not need to be
explicitly defined.

The :func:`set_promotion` may be required for more complicated promotions which
involves operations more complicated than simple conversions. The previous
rule could be re-written as

    >>> @set_promotion(float, int, outtype=float)              # doctest: +SKIP
    ... def promote_float_int(x, y):
    ...     # do something complicated
    ...     return x, float(y)

Here we can assume that the argument types will appear in the given order and
the promotion mechanism automatically creates the function with swapped
arguments.

'''

from .conversion import *
from .promotion import *
from . import rules as _rules
