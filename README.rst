========
Overview
========

What is pygeneric?
==================

`pygeneric` implements generic functions with type dispatch in Python. A generic
function groups different implementations (or methods) under the same name.
The actual implementation is then chosen at runtime depending on the function
arguments.

The implementation is loosely inspired in the Julia language. We also shamelessly
steal some other features of Julia and adapted them to Python:

* Parametric types.
* A type conversion/promotion system integrated with arithmetic operations.
* A generic Object base class that delegates all binary operations to the
  corresponding generic functions (i.e., instead of implementing
  Object.__add__, we overload add(Object, Object)).

This package works with Python 3 and Python 2, but it is getting increasingly
more difficult to keep Python 2 support as we implement more advanced features.
Not all functionality works in Python 2, and sometimes some extra precautions
are necessary. Pygeneric cannot handle old style classes properly, no never
throw "instance" objects at it! In the small places in which Python 2 and Python
3 behavior diverges, sometimes we have to replicate Python 3 behavior even when
executing in the Python 2 interpreter.


Basic usage
===========

Most of the functionality present in this package works around the type dispatch
in generic functions. We declare a generic function using the syntax::

    from generic import generic, Number, Sequence

    @generic
    def func(x, y):
        print('Got %r and %y' % (x, y))

Type dispatch can be defined in Python 3 as::

    @func.dispatch
    def func(x: Number, y: Number):
        print('Got two numbers: %r and %y' % (x, y))

The Python 2-friendly syntax (which can also be useful in Python 3) is::

     @func.register(Sequence, Sequence)
     def func(x, y):
         print('Got two sequences: %r and %y' % (x, y))

Depending on the types of each argument, the dispatcher will choose either one
of these three implementations::

    >>> func(42, 0.0)
    Got two numbers: 42 and 0.0

    >>> func([1, 2], (3, 4))
    Got two sequences: [1, 2] and (3, 4)

    >>> func("foo", "bar")
    Got "foo" and "bar"

The type dispatch always chooses the most specialized method for the given
argument types.

Consider the two specialized dispatches

::

    @func.dispatch
    def func(x: Integral, y: Number):
        print('Got one integer: %r and %y' % (x, y))

    @func.dispatch
    def func(x: Integral, y: Integral):
       print('Got two integers: %r and %y' % (x, y))

``pygeneric`` knows what to do::

    >>> func(1, 2)
    Got two integers: 1 and 2

    >>> func(1, 2.0)
    Got one integer: 1 and 2.0

    >>> func(2.0, 1)
    Got two numbers: 2.0 and 1


Further information
===================

Did you find this feature useful? Then start using pygeneric now!
Check the __documentation for additional information.

.. __documentation:: http://pythonhosted.org/pygeneric/