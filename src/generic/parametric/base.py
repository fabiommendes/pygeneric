"""
These module implement parametric types for Python.

We want to integrate with Python's typing module in the future. That's why 
there is pytyping.py and a typeparams.py in this folder. They are not currently 
used. 
"""

import abc

__all__ = [
    # Types
    'ParametricMeta', 'Parametric', 'ABC', 'Immutable', 'Mutable', 'Any',
    
    # Functions
    'sameorigin', 'parameters',
]


# Import symbols with default implementations
# (this has to be done like this because 3to2 do not understand class
# definitions inside try/except blocks.
class ABC(metaclass=abc.ABCMeta):
    __slots__ = ()


try:
    from typing import Any
except ImportError:
    class Any(ABC):
        """Has basic functionality of typing.Any."""


class ParametricMeta(abc.ABCMeta):
    """
    Meta class for Parametric types.
.

    It overrides __getitem__ to implement type parametrization and __call__
    to prevent creating instances of the abstract type and in order to find a
    suitable concrete subtype from the type of the arguments.
    """

    def __new__(cls, name, bases, ns, *, 
                abstract=False, 
                origin=None,
                parameters=None,
                finalize=True):
        # There are three types of classes: concrete, origin and abstract. Only
        # the first can have instances. Origin classes do not have direct 
        # instances, but generate concrete subclasses via parametrization. 
        # Pure abstract classes exist only to share functionality between
        # different origins and for subclass checking. They do not have 
        # instances and produce other abstract classes via parametrization. 
        
        # Set default values for abstract and origin attributes
        is_abstract = ns.get('__abstract__', abstract)  
        for B in bases:
            if isinstance(B, ParametricMeta) and B.__concrete__:
                origin = B.__origin__
                is_abstract = False
                break
        subtypes = {} if origin is None else None
        
        # Fetch parameters from an attribute or from a base class
        parameters = ns.get('__parameters__', parameters)
        if parameters is None:
            for B in bases:
                parameters = getattr(B, '__parameters__', None)
                if parameters is not None:
                    break
        parameters = _normalize_params(None, parameters)

        # Create new type
        new = abc.ABCMeta.__new__(cls, name, bases, ns)        
        new.__parameters__ = parameters
        new.__abstract__ = is_abstract
        new.__subtypes__ = subtypes
        new.__origin__ = origin
        new.__concrete__ = subtypes is None and not is_abstract
        
        if finalize:        
            try:
                finalizer = new.__finalizetype__
            except AttributeError:
                pass
            else:
                finalizer(new)
        return new
    
    def __init__(self, *args, **kwds):
        pass

    def __call__(self, *args, **kwds):
        if self.__abstract__:
            raise TypeError('cannot instantiate %s' % self.__name__)
        elif self.__origin__ is None:
            new = self.__abstract_new__(*args, **kwds)
            if new.__class__ is self:
                raise TypeError('cannot instantiate %s' % self.__name__)
            return new
        else:
            return super(ParametricMeta, self).__call__(*args, **kwds)

    def __getitem__(self, params):
        try:
            return self.__subtypes__[params]
        except TypeError:
            raise TypeError('%s cannot be parametrized' % self.__name__)
        except KeyError:
            pass

        # Normalize parameters before continue
        #_check_parameters(self, params)
        newparams = _normalize_params(self, params)
        if newparams != params:
            new = self.__subtypes__[params] = self[newparams]
            return new
        else:
            params = newparams

        # Create name, bases and namespace for the new parametrized type
        basesgetter = getattr(self, '__preparebases__', lambda params: (self,))
        nsgetter = getattr(self, '__preparenamespace__', lambda params: {})
        name = _subtype_name(self, params)
        bases = basesgetter(params)
        ns = nsgetter(params)
        ns.setdefault('__slots__', ())
        
        # Decide if it is abstract and has an origin
        is_abstract = self.__abstract__ or not _is_concrete_params(self, params) 
        new = type(self)(name, bases, ns, 
                         abstract=is_abstract, 
                         origin=self,
                         parameters=params,
                         finalize=False)
        self[params] = new
        
        # Finalize type
        try:
            finalizer = new.__finalizetype__
        except AttributeError:
            pass
        else:
            finalizer(new)
        return new

    def __setitem__(self, params, T):
        #_check_parameters(self, params)
        params = _normalize_params(self, params)
        
        if self.__subtypes__ is None:
            raise TypeError('cannot assign subtypes to %s' % self.__name__)
        if params in self.__subtypes__:
            raise KeyError('cannot override to an existing type')
        
        T.__origin__ = self
        T.__parameters__ = params
        self.__subtypes__[params] = T
        if not issubclass(T, self):
            self.register(T)


#
# Auxiliary functions
#
def _check_parameters(origin, params):
    """Check if the given parameters are consistent with origin 
    specification"""
    
    abstract_params = origin.__parameters__
    params = list(params)
    
    while len(params) < len(abstract_params):
        params.append(None)
        
    if len(params) > len(abstract_params):
        raise ValueError('too many parameters')
    
    for x, y in zip(abstract_params, params):
        if y is not None or y is not Ellipsis:
            if not isinstance(y, x):
                tname = x.__name__
                raise ValueError('expected a %s instance, got %r' % (tname, y))


def _normalize_params(origin, params):
    """Convert all parameters to a standard form: return value is always a
    tuple of the same length as origin.__parameters__. All ellipsis are 
    replaced by None"""
    
    if origin is None:
        if params is None:
            return None
        else:
            return tuple(params)
    
    if params is None:
        return params 
    
    if not isinstance(params, tuple):
        params = (params,)

    # Change ellipisis to None
    params = [None if x is Ellipsis else x for x in params]
    
    if origin.__parameters__ is not None:
        # Fill incomplete parameters with None's
        while len(params) < len(origin.__parameters__):
            params.append(None)
        
        # Fill abstract parameteres in the place of None's
        for i, x in enumerate(origin.__parameters__):
            if params[i] is None:
                params[i] = x
        
    return tuple(params)


def _is_concrete_params(origin, params):
    """Test if the given parameter sequence can represent the parameters of
    a concrete type"""
    
    if origin.__parameters__ is None:
        return False
    return all(x != y for (x, y) in zip(params, origin.__parameters__))


def _isconcrete(x):
    """Return true if type is concrete"""
    
    if issubclass(type(x), ParametricMeta):
        return x.__origin__ is not None and not x.__abstract__
    return False


def _subtype_name(origin, params):
    """Compute the subtype's name from its origin class and parameters."""
    
    out = []
    params = list(params)
    for x in params:
        if x is None:
            out.append('...')
        elif isinstance(x, type):
            out.append(x.__name__ )
        else:
            out.append(repr(x))
    
    if origin.__parameters__ is not None:
        while len(params) < len(origin.__parameters__):
            params.append(None)
            out.append('...')
    else:
        out.append('?')
    
    return '%s[%s]'  % (origin.__name__,  ', '.join(out))


class Parametric(ABC, metaclass=ParametricMeta):
    """
    Base class for parametric types.
    """
    __slots__ = ()


class Mutable(ABC):
    """Base class for all mutable types"""

    __slots__ = ()


class Immutable(ABC):
    """Base class for all immutable types"""

    __slots__ = ()


#
# Utility functions
#
def sameorigin(T1, T2):
    """Return True if the two types share the same origin"""
    
    if T1 is T2:
        return True
    try:
        return T1.__origin__ is T2.__origin__
    except AttributeError:
        return False


def parameters(obj):
    """parameters(obj) <==> obj.__parameters__.

    Return the class parameters for some class or instance."""

    return obj.__parameters__
