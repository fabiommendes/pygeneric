=======================================
Generic functions and multiple dispatch
=======================================

The basic functionality implemented by ``pygeneric`` is a generic function with
multiple dispatch. We usually construct these functions using the ``@generic``
decorator, but they can also be build by an explicit instantiation of the
:class:`Generic` class.

.. code-block:: python

    from generic import generic

    @generic
    def func(x, y):
        print('Got %r and %r' % (x, y))

``func`` is now a :class:`Generic` instance. Overloading is done by using one
of the ``@func.overload`` or ``@func.register``
decorators:

.. code-block:: python

    from collections import Sequence
    from numbers import Number

    @func.overload
    def func(x: Number, y: Number):
        print('Got two numbers: %r and %r' % (x, y))

    @func.register(Sequence, Sequence)
    def func(x, y):
        print('Got two sequences: %r and %r' % (x, y))

These define the type dispatch rules for the function: two numbers are
handled by the first function, two sequences execute the second and anything
else is redirected to the placeholder implementation used to create the generic
function.


Generic instances as mappings
=============================

In some sense, we can think of generic functions as a mapping between
types to implementations. Indeed, :class:`Generic` instances have a mapping
interface that do exactly that:

>>> number_func = func[Number, Number]
>>> number_func(1, 2)
Got two numbers: 1 and 2

It has all methods one would expect from a dictionary. The main difference,
perhaps, is that it create default values for tuples of arguments that were
not explicitly defined using the dispatch algorithm:

>>> placeholder_func = func[object, object]
>>> placeholder_func(1, 2)
Got 1 and 2

One can access keys, iterate, and do most operations that are possible with a
regular dictionary. This includes setting items as a (not encouraged)
alternative to overloading:

.. code-block:: python

    def func_str(x, y):
        print('Got two strings: %r and %r' % (x, y))
    func[str, str] = func_str


An useful idiom is to use indexing to call a generic implementation from a more
specialized one:

.. code-block:: python

    @func.overload
    def func(x: float, y:float):
        func[Number, Number](x, y)
        print('But beware floats are not associative')


It can also be used to inspect the generic function for the number and types
of methods implemented.


Factory functions
=================

Generic functions can create methods on-the-fly using factory functions:
instead of providing an implementation for a specific set of argument types,
a factory method is a function that return other functions when called.

This is acomplished using the ``factory=True`` attribute of the
``@func.register`` decorator:

.. code-block:: python

    from collections import Mapping

    @func.register(Mapping, Mapping, factory=True)
    def factory(T1, T2):
        # This function will return the implementation for types T1 and T2.
        # If it return NotImplemented, the next method in the dispatch priority
        # list will be chosen.
        if T1 is T2 and T1 is dict:
            return NotImplemented
        elif T1 is T2:
            def implementation1(x, y):
                print('Got two mappings of the same type')
            return implementation1
        else:
            def implementation2(x, y):
                print('Got two mappings of different types')
            return implementation2


The factory above produces 3 different functions depending on the types of input
arguments. If both objects are instances of ``dict``, it returns
``NotImplementedError``, which tells the dispatcher to pick the next
implementation in the dispatch list. If both types are equal (but different from
dict) it dispatches to :func:`implementation1`, otherwise, :func:`implementation2`
is chosen. These implementations are kept in cache, but are not inserted in the
Generic function dictionary. Thus one can later specialize to any subtype (e.g.,
func(dict, dict)) without conflicts.

Factory functions are useful to emulate what in other languages can be
accomplished with parametrization on function definitions. In Julia, for
instance, it is possible to define complex dispatch such as:

.. code-block:: julia

    function func{T<:Number}(L::Array{T}, x::T)
        println("Got a sequence of numbers and an extra element")
    end


This rule is only used if L is an array of numbers of type T and
x is of the same type. If ``L = [1, 2, 3]`` and ``x = 1.0``, the method will not
be used. This kind of behavior is very difficult to support using Python's
comparatively limited type system. Factory functions can implement a similar
functionality albeit not as elegantly:

.. code-block:: python

    from generic.parametric import parameters, List

    @func.register(List, Number, factory=True)
    def factory(TL, Tx):
        if parameters(TL)[0] is Tx:
            def matched(L, x):
                print('Got a sequence of numbers and an extra element')
        else:
            return NotImplemented


In the above example, we are using the List type defined in ``generic.parametric``.
It consists in a parametric type representing a list of objects with uniform
type.


Corner cases and gotchas
========================

The introduction of Abstract Base Classes in PEP3119, and more specifically the
possibility of overloading :func:`isinstance` and :func:`issubclass` made
Python's type system very flexible at the cost of some predictability. It is
possible, for instance, to define classes that
``isinstance(x, C) != issubclass(type(x), C)``.

Pygeneric always tests subclassing using :func:`issubclass`, and never uses
:func:`isinstance`. Although one can expect that both functions will almost
always yield the same results, there is no guarantee. To cite the PEP:

.. quote::

    Like all other things in Python, these promises are in the nature of a
    gentlemen's agreement, which in this case means that while the language
    does enforce some of the promises made in the ABC, it is up to the
    implementer of the concrete class to insure that the remaining ones are
    kept.

Take a "Prime" class for instance. We can define it so ``isinstance(7, Prime) == True``.
However, we don't know what to make of ``issubclass(int, Prime)``: some integers
are primes, and some are not. Pygeneric cannot understand this.

.. ignore-next-block
.. code-block:: python

    @func.overload
    def func(x: Prime, y: Prime):
        print('Got two primes!')

    func(2, 3)  # we don't know what to do!


If we interpret the ``issubclass(A, B)`` relation as true iff all instances of
A are instances of B, then it is safe to say that ``issubclass(int, Prime) == False``.
In this case, func(2, 3) would dispatch to func(int, int) -> func(Number, Number),
even though the two arguments are primes. If Prime is also a concrete subclass
of int that only accept prime values, we would obtain the expected behavior
by calling func(Prime(2), Prime(3)).

Although this examples with primes might be a little artificial, the exact same
situation might appear when using the parametric container types from
``generic.parametric``.


API Documentation
=================

.. automodule::generic.generic
    :members: generic, overload, Generic