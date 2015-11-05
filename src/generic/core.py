'''
=======================================
Generic functions and multiple dispatch
=======================================

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

'''
import sys
import six
import inspect
import functools
from generic.tree import PosetMap
from collections import MutableMapping, Mapping
from .util import raise_no_methods

__all__ = ['Generic', 'generic', 'overload']


try:
    from generic.core_fast import FastCache as _FastCache
    _generic_bases = (_FastCache, MutableMapping)
except ImportError:
    _generic_bases = (MutableMapping,)
    import warnings
    warnings.warn('no ctypes found: using slow version of generic type dispatch')


class Generic(*_generic_bases):

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

    def __init__(self, name, doc=None, validate=False):
        super(Generic, self).__init__()
        self.name = name
        self.doc = doc
        self._cache = {}
        self._data = PosetMap(subclasses, {None: None})
        self._factories = {}
        self._last_func = None
        self._validate = validate or None

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
        '''Makes it work as a method'''

        raise NotImplementedError

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

        self.register(*argtypes, func=func, restype=restype)

        
    def __getitem__(self, types):
        try:
            return self._cache[types]
        except KeyError:
            try:
                return self.dispatch(*types)
            except TypeError:
                raise KeyError(types)
            
    def __delitem__(self, types):
        raise NotImplementedError
        del self._data[types]
        if len(self._cache) == len(self._data) + 1:
            del self._cache[types]  # Cache has the same items as self._data
        else:
            self._cache.clear()
            self._cache.update(self._data)

    def __len__(self):
        if self._data[None] is None:
            return len(self._data) - 1 # exclude the None root fallback
        else:
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
    # API
    #
    def cache(self):
        '''Return a mapping proxy for the type cache'''
        
        return mappingproxy(self._cache)
    
    def registry(self):
        '''Return a proxy with all types explicitly registered for the generic
        function'''
        
        #TODO: make single dispatch also map from single type to implementation
        # as in singledispatch 
        return mappingproxy(self)
    
    def dispatch(self, *types):
        '''Runs the dispatch algorithm to return the best available 
        implementation for the given types registered on the generic function.
        
        Raises a TypeError if no suitable implementation is found.'''
        
        wrapped = self._data[types]

        # The None root is always present. It is assigned to None if no
        # fallback function is available
        if wrapped is None:
            raise_no_methods(self, types=types)

        factory, restype = wrapped
        implementation = factory(types, restype)

        func = self._cache[types] = implementation
        self._cache_update()
        return func

    def which(self, *args):
        '''Returns the concrete method that would be used if called with the
        given positional arguments.'''

        types = tuple(map(type, args))
        try:
            return self[types]
        except KeyError:
            raise TypeError('no methods for %s' % types)
    
    def register(self, *argtypes, func=None, restype=None):
        '''Register a new implementation for the given sequence of input
        types.
        '''
        
        # We don't use the restype for now. Maybe in the future? Ideas?
        if func is None:
            def decorator(func):
                self.register(*argtypes, func=func)
                return _generic_or_func(self, func)
            return decorator
        
        # Register factory in the internal dictionary
        wrapped = functools.partial(_simple_factory, func) 
        self.factory(*argtypes, func=wrapped, restype=restype)
        
        # Update documentation, if empty
        if not self.__doc__:
            self.__doc__ = getattr(func, '__doc__', '')

    def overload(self, *args, **kwds):
        '''Decorator used to register method overloads'''

        # Decorator form: function is not the first argument
        if len(args) == 0 or not callable(args[0]):
            def decorator(func):
                self.overload(func, *args, **kwds)
                return _generic_or_func(self, func)
            return decorator

        # Non decorator form of method call
        func, args = args[0], args[1:]

        # No types given: inspect arguments
        _restype = object
        if len(args) == 0:
            if self._is_fallback_signature(func):
                argtypes = None
            elif six.PY2:
                func_args = inspect.getargs(func.func_code).args
                argtypes = [object] * len(func_args)
            else:
                argtypes, _restype = self._inspect_signature(func)

        # Input types given
        if len(args) >= 1:
            argtypes = tuple(args[0])

        # Input and output types given
        if len(args) == 2:
            _restype = args[1]

        if len(args) > 2:
            raise TypeError('expect between 0 and 3 positional arguments')

        # Accept stacked overload decorators
        if func is self:
            func = self._last_func
        self._last_func = func

        # Save in the internal dictionary
        self[argtypes] = func

        # Return the correct value.
        if func.__name__ == self.name:
            return self
        else:
            return func

    def factory(self, *argtypes, func=None, restype=None):
        '''Register a method factory.
        
        Everytime that the dispatcher reaches a method factory, it calls
        ``factory(argtypes, restype)`` and expects to receive a function. This
        function is then registered in cache and is used in subsequent calls 
        to handle the given input types.
        '''
        
        # Call function in decorator form
        if func is None:
            def decorator(func):
                self.factory(*argtypes, func=func, restype=restype)
                return func
            return decorator
        
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
        if self._validate is not None:
            self._validate(argtypes, restype)
        
        self._data[argtypes] = (func, restype)
        subkeys = list(self._data.subkeys(argtypes))
        for k in list(self._cache):
            if subclasses(k, argtypes):
                if not any(subclasses(k, K) for K in subkeys):
                    del self._cache[k]
        self._cache_update()

    #
    # Helper functions. Can be overloaded by sub-classes
    #
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
            return tuple(D.get(name, object) for name in varnames), object

        # Does not have annotations, maybe it is a builtin function. Try
        # looking at the docstring
        except AttributeError:
            body, sep1, _tail = getattr(func, '__doc__', '').partition(')')
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
            return tuple(object for name in varnames), object

    def _cache_update(self):
        '''Call whenever cache is changed'''

        pass


#
# Uses the fast version of the __call__ method if available from C class
#
try:
    if 'FastCache' in [cls.__name__ for cls in Generic.mro()]:
        del Generic.__call__
        del Generic._cache_update
except AttributeError:
    pass


#
# Utility functions
#
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
    generic.overload(func)
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

    >>> @overload(foo)                                         # doctest: +SKIP
    ... def foo(x:int, y:int):
    ...    return x + y + 1

    One can specify the input types with the alternate syntax bellow, which
    is also valid in Python 2.

    >>> @overload(foo, [int, int])
    ... def foo(x, y):
    ...    return x + y + 1

    This syntax is also helpful when declaring many different input signatures
    that are associated with the same implementation.

    >>> @overload(foo, [float, int])
    ... @overload(foo, [int, float])
    ... def foo(x, y):
    ...    return x + y + 0.5

    Now we dispatch to different implementations depending on the types of the
    arguments

    >>> foo(1.0, 1.0)
    2.0
    >>> foo(1, 1)
    3
    >>> foo(1, 1.0), foo(1.0, 1)
    (2.5, 2.5)
    '''

    if not isinstance(genericfunc, Generic):
        raise TypeError('callable must be created with the @generic '
                        'decorator first')

    def decorator(func):
        return genericfunc.overload(func, *args, **kwds)
    return decorator


class mappingproxy(Mapping):
    '''A read-only proxy to a mapping'''
    
    def __init__(self, mapping):
        self.__mapping = mapping
        
    def __len__(self):
        return len(self.__mapping)
    
    def __iter__(self):
        return iter(self.__mapping)
    
    def __getitem__(self, key):
        return self.__mapping[key]
    
    
def _generic_or_func(generic, func):
    '''Return generic if new defined function is shadowing the generic name
    or the function otherwise. Used in decorators'''
    
    # Maybe use inspect for a more robust solution? Is it portable across 
    # python implementations 
    if generic.__name__ == func.__name__:
        return generic
    else:
        return func


def _tname(x):
    '''A shortcut to the object's type name'''
    
    return type(x).__name__


def _simple_factory(func, argtypes, restype):
    '''The most simple builder: return the function unchanged'''
    
    return func


def _restype_checker_factory(func, argtypes, restype):
    '''Simply check if the return type is correct'''

    if restype is None:
        return func
        
    @functools.wraps
    def checked(*args, **kwds):
        out = func(*args, **kwds)
        if not isinstance(out, restype):
            raise TypeError('wrong return type: %s' % _tname(out))
        return out
                 
    return checked

    
def _strict_check_factory(func, argtypes, restype):
    '''Check if all input/output types are *exactly* the same as declared.
    
    Raise type errors with subclasses.'''
    
    return _instance_check_factory(func, argtypes, restype, 
                                   instancecheck=lambda x, y: x is y) 


def _instance_check_factory(func, argtypes, restype, instancecheck=isinstance):
    '''Check if all input/output types are the same as declared.
    
    Subclasses are also allowed.'''
    
    N = len(argtypes)
    
    @functools.wraps
    def checked(*args, **kwds):
        if len(args) == N:
            raise TypeError('wrong number of arguments')
        for i, (x, T) in enumerate(zip(x, T)):
            if instancecheck(x, T):
                fmt = i, _tname(x), T.__name__
                msg = 'error: %-th argument should be %s, got %s' % fmt
                raise TypeError(msg)
        
        if restype is None:
            return func(*args, **kwds)
        else:
            out = func(*args, **kwds)
            if not instancecheck(out, restype):
                raise TypeError('wrong return type: %s' % _tname(out))
            return out
                 
    return checked

