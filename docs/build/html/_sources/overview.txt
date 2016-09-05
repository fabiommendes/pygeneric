========
Overview
========

What is pygeneric?
==================

`pygeneric` implements generic functions based on type dispatch in Python. A generic
function groups different implementations (or methods) under the same name.
The actual implementation is then chosen at runtime depending on the type of
each function argument.

The implementation is loosely inspired in the Julia language. We also shamelessly
steal some other features of Julia and adapted them to Python:

* Parametric types.
* A type conversion/promotion system integrated with arithmetic operations.
* A generic Object base class that delegates all binary operations to the
  corresponding generic functions (i.e., instead of implementing
  Object.__add__, we overload ``generic.op.add(Object, Object))``.

This package works with Python 3 and Python 2, but it is getting increasingly
more difficult to keep Python 2 support as we implement more advanced features.
Not all functionality works in Python 2, and sometimes extra precautions
are necessary. Pygeneric cannot handle old style classes and sometimes we are
limited by lack of some Python 3 only syntax. Python 2 also have some quirks
that we do not try to emulate (e.g., broken comparison operators), keeping an
uniform Python 3 semantics.


Basic usage
===========

Most of the functionality present in this package works around the type dispatch
in generic functions. We declare a generic function using the syntax

.. code-block:: python

    from generic import generic, Number, Sequence

    @generic
    def func(x, y):
        print('Got %r and %r' % (x, y))


Type dispatch can be defined in Python 3 as

.. code-block:: python

    @func.overload
    def func(x: Number, y: Number):
        print('Got two numbers: %r and %r' % (x, y))


The Python 2-friendly syntax (which can also be useful in Python 3) is:

.. code-block:: python

     @func.register(Sequence, Sequence)
     def func(x, y):
         print('Got two sequences: %r and %r' % (x, y))


Depending on the types of each argument, the dispatcher will choose either one
of these three implementations

>>> func(42, 0.0)
Got two numbers: 42 and 0.0
>>> func([1, 2], (3, 4))
Got two sequences: [1, 2] and (3, 4)
>>> func("foo", "bar")
Got two sequences: 'foo' and 'bar'


The type dispatch always chooses the most specialized method for the given
argument types.

Consider the two specialized dispatches

.. code-block:: python

    from numbers import Integral

    @func.overload
    def func(x: Integral, y: Number):
        print('Got one integer: %r and %s' % (x, y))

    @func.overload
    def func(x: Integral, y: Integral):
       print('Got two integers: %r and %s' % (x, y))


``func`` knows what to do

>>> func(1, 2)
Got two integers: 1 and 2
>>> func(1, 2.0)
Got one integer: 1 and 2.0
>>> func(2.0, 1)
Got two numbers: 2.0 and 1


Further information
===================

Did you find this feature useful? Then start using pygeneric now!
Check the documentation__ for additional information.

.. __documentation:: http://pythonhosted.org/pygeneric/