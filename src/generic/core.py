'''
=======================================
Generic functions and multiple dispatch
=======================================

Example
-------

>>> @generic
... def f(x, y):
...     return x + y + 3.14


>>> @overload(f)
... def f(x:int, y:int):
...     return x + y + 3

>>> f(0, 0)
3
>>> f(0.0, 0.0)
3.14



'''
import sys
from generic.tree import PosetMap
from collections import MutableMapping

__all__ = ['Generic', 'generic', 'overload']

try:
    from generic.core_fast import FastCache as _FastCache

    class Base(_FastCache, MutableMapping):
        pass

except ImportError:
    Base = MutableMapping


class Generic(Base):

    '''A generic function is a collection of different implementations or
    "methods" under the same name, usually sharing a similar interface. When
    the generic function object is called, the concrete method is choosen at
    runtime from the types of the arguments passed to the generic function
    object.

    Dictionary interface
    --------------------

    The collection of different methods under the same generic function is
    exposed as a mapping between a tuples of types to python functions.


    '''

    def __init__(self, name, doc=None):
        super(Generic, self).__init__()
        self.name = name
        self.doc = doc
        self._cache = {}
        self._data = PosetMap(subclasses, {None: None})
        self._last_func = None

    # Generic magic methods ###################################################
    def __call__(self, *args, **kwds):
        types = tuple(map(type, args))
        try:
            method = self._cache[types]
        except KeyError:
            try:
                method = self[types]
            except KeyError:
                msg = 'no methods found for %s' % print_signature(self, types)
                raise TypeError(msg)
        if method is None:
            raise TypeError('no fallback defined for %s()' % self.__name__)
        return method(*args, **kwds)

    def __repr__(self):
        name = self.name
        size = len(self)
        return '<generic function %(name)s() with %(size)s methods>' % locals()

    def __get__(self, instance, cls=None):
        '''Implements the descriptor interface in order to work as method'''

        raise NotImplementedError

    # Function properties #####################################################
    @property
    def __annotations__(self):
        return {}

    @property
    def __closure__(self):
        return None

    @property
    def __code__(self):
        return None

    @property
    def __defaults__(self):
        return None

    @property
    def __globals__(self):
        return sys._getframe(1).f_locals

    @property
    def __name__(self):
        return self.name

    @__name__.setter
    def __name__(self, value):
        self.name = value

    @property
    def __doc__(self):
        return self.doc

    @__doc__.setter
    def __doc__(self, value):
        self.doc = value

    @property
    def cache(self):
        return dict(self._cache)

    # API #####################################################################
    def overload(self, *args, **kwds):
        '''Decorator used to register method overloads'''

        # Finds the implementation and signature
        arg_types = None
        ret_type = None
        if len(args) == 0:
            pass
        elif len(args) == 1:
            arg_types = args[0]
        elif len(args) == 2:
            arg_types, ret_type = args
        else:
            raise TypeError('expect between 0 and 2 positional arguments')

        # Maybe it is a decorator
        if len(args) == 1 and len(kwds) == 0 and callable(arg_types):
            return self.overload()(args[0])

        def decorator(func):
            nonlocal arg_types, ret_type

            # Accept stacked overload decorators
            if func is self:
                func = self._last_func
            self._last_func = func

            # Get signature from function
            # (currently the return type is simply ignored)
            if arg_types is None and ret_type is None:
                arg_types = self._inspect_signature(func)

            # Check if function is has a fallback signature
            if self._is_fallback_signature(func):
                arg_types = None

            # Save in cache and return
            self[arg_types] = func
            if func.__name__ == self.name:
                return self
            else:
                return func

        return decorator

    def which(self, *args, **kwds):
        '''Instead of calling the generic function with the given arguments,
        it returns the concrete method that would be used for the call.'''

        types = tuple(map(type, args))
        try:
            return self[types]
        except KeyError:
            raise ValueError('no methods for %s' % types)

    # Helper functions. Can be overloaded by sub-classes ######################
    def _is_fallback_signature(self, func):
        '''Inspect function arguments and return True if it should be
        considered a fallback implementation.'''

        # Todo: signatures that have *args are fallback
        return False

    def _inspect_signature(self, func):
        '''Return dispatch conditions from func's argument annotations'''

        try:
            D = func.__annotations__
            n_args = func.__code__.co_argcount - len(func.__defaults__ or ())
            varnames = func.__code__.co_varnames[:n_args]
            return tuple(D.get(name, object) for name in varnames)

        # Does not have annotations, maybe it is a builtin function. Try
        # looking at the docstring
        except AttributeError:
            body, sep1, _tail = func.__doc__.partition(')')
            name, sep2, args = body.partition('(')

            # Fail conditions
            fail = (sep1 == '') or (sep2 == '')
            if '[' in args:
                fail = True

            if fail:
                print([body, sep1, sep2, name, args])
                print(func)
                print(func.__doc__)
                raise ValueError(
                    'could not inspect signature. '
                    'Try giving the signature explicitly')

            varnames = [x.strip() for x in args.split(',')]
            return tuple(object for name in varnames)

    def _wrap_method(self, method, argtypes, restype):
        '''Wraps a callable implementation of some given signature. The wrapped
        version is stored internally and may store metadata or implement
        some special behavior.

        The default implementation does nothing and simply return method.
        '''

        return method

    def _unwrap_method(self, method, argtypes):
        '''Unwraps a method wrapped with `_wrap_method()` and specialize it
        to the given argtypes.

        Must return a python callable. This return object is than stored into
        cache for faster access.'''

        return method

    def _cache_update(self):
        '''Call whenever cache is changed'''

        pass

    # Dictionary interface ####################################################
    def __contains__(self, obj):
        try:
            self[obj]
        except KeyError:
            return False
        else:
            return True

    def __setitem__(self, argtypes, func):
        # Normalize inputs
        if argtypes is None:
            restype = None
        elif isinstance(argtypes, type):
            argtypes, restype = (argtypes,), None
        if argtypes is not None:
            if len(argtypes) == 2 and not isinstance(argtypes[0], type):
                argtypes, restype = argtypes
            else:
                restype = None
            argtypes = tuple(argtypes)

        # Check for invalid inputs
        if argtypes is not None:
            if not all(isinstance(T, type) for T in argtypes):
                argtypes = str(argtypes)
                raise ValueError('must be a tuple of types, got %s' % argtypes)
        if not isinstance(restype, (type, type(None))):
            tname = type(restype).__name__
            raise ValueError('return type must be a type, got %s' % tname)

        # Prevent overwriting old values
        if argtypes in self._data:
            types_repr = ', '.join(T.__name__ for T in argtypes)
            name = self.name
            msg = 'method %s(%s) is already defined' % (name, types_repr)
            raise TypeError(msg)

        # Add keys and update cache
        wrapped_method = self._wrap_method(func, argtypes, restype)
        self._data[argtypes] = wrapped_method
        subkeys = list(self._data.subkeys(argtypes))
        for k in list(self._cache):
            if subclasses(k, argtypes):
                if not any(subclasses(k, K) for K in subkeys):
                    del self._cache[k]
        self._cache_update()

        # Update documentation, if empty
        if not self.__doc__:
            self.__doc__ = getattr(func, '__doc__', '')

    def __getitem__(self, types):
        try:
            return self._cache[types]
        except KeyError:
            method = self._data[types]

            # The None root is always present. It is assigned to None if no
            # fallback function is available
            if method is None:
                raise KeyError(types)

            func = self._cache[types] = self._unwrap_method(method, types)
            self._cache_update()
            return func

    def __delitem__(self, types):
        raise NotImplementedError
        del self._data[types]
        if len(self._cache) == len(self._data) + 1:
            del self._cache[types]  # Cache has the same items as self._data
        else:
            self._cache.clear()
            self._cache.update(self._data)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        if None in self._cache:
            for key in self._data:
                yield key
        else:
            # None is the root fallback method. If no method is assigned to
            # None, it should not be in the list of keys
            for key in self._data:
                if key is not None:
                    yield key


#
# Uses the fast version of the __call__ method if available from C class
#
try:
    if 'FastCache' in [cls.__name__ for cls in Generic.mro()]:
        del Generic.__call__
        del Generic._cache_update
except AttributeError:
    pass

###############################################################################
#                            Utility functions
###############################################################################


def subclasses(types1, types2):
    '''Return True if all types in the sequence types1 are subclasses of the
    respective types in the sequence types2.

    The special value of None is considered to be the root type of all type
    sequences.

    Example
    -------

    >>> import numbers
    >>> subclasses((int, int), (object, numbers.Integral))
    True

    >>> subclasses((int, int), None)
    True
    '''

    if types2 is None:
        return True
    elif types1 is None:
        return False

    if len(types1) != len(types2):
        return False
    else:
        return all(issubclass(T1, T2) for (T1, T2) in zip(types1, types2))


def print_signature(func, types):
    '''Return a pretty-printed version of an abstract call to some arguments
    of the given sequence of types.


    Example
    -------

    >>> print_signature(int, (str, int))
    'int(str, int)'
    '''

    fname = func.__name__
    args = ', '.join(T.__name__ for T in types)
    return '%s(%s)' % (fname, args)


def generic(func=None, **kwds):
    '''Decorator used to define a generic function'''

    # Transforms to decorator
    if func is None and kwds:
        def decorator(func):
            return generic(func, **kwds)
        return decorator

    # Finds the approriate base class and return the generic function
    generic = Generic(func.__name__)
    generic.overload()(func)
    return generic


def overload(genericfunc, *args, **kwds):
    '''Decorator used to define an overload for a generic function.

    Example
    -------

    Consider the generic function

    >>> @generic
    ... def foo(x, y):
    ...    return x + y

    The overload decorator must be called with the generic function as first
    argument

    >>> @overload(foo)
    ... def foo(x:int, y:int):
    ...    return x + y + 1

    Now we dispatch to different implementations depending on the types of the
    arguments

    >>> foo(1.0, 1.0)
    2.0
    >>> foo(1,1)
    3

    Optionally, the overload decorator can specify a type signature which can
    be useful for directing different signatures to the same implementation

    >>> @overload(foo, (float, int))         # no return type here.
    ... @overload(foo, (int, float), float)  # this has a return type!
    ... def foo(x, y):
    ...    return x + y + 0.5

    >>> foo(1, 1.0), foo(1.0, 1)
    (2.5, 2.5)
    '''

    if not isinstance(genericfunc, Generic):
        raise TypeError('callable must be created with the @generic '
                        'decorator first')

    def decorator(func):
        return genericfunc.overload(*args, **kwds)(func)
    return decorator


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    ##########################################################################
    # Move to real unit tests!
    ##########################################################################

    @generic
    def f(x, y):
        return x + y + 3.14

    @overload(f)
    def f(x: int, y: int):
        return x + y + 3

    assert f(0, 0) == 3
    assert f(0.0, 0.0) == 3.14

    @overload(f, (int, float))
    @overload(f, (float, int))
    def f(x, y):
        return x + y + 3.07

    assert f(0.0, 0) == 3.07
    assert f(0, 0.0) == 3.07
