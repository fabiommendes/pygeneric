import typing
from typing import GenericMeta, Generic, Any, TypingMeta, TypeVar, Union
from typing import _type_check, _type_repr


class TypeParam:
    """Type parameter.

    Usage::

      N = TypeParam('N', int)
      T = TypeVar('T')
      
      class Vector(Parametric[N, T]):
          ...

    Type parameters define unknowns in an abstract type that should be assigned
    to values in a concrete type. 
    
    
    Type variables can be introspected. e.g.:

      N.__name__ == 'N'
      N.__constraints__ == (int,)
    """

    def __init__(self, name, *constraints):
        self.__name__ = name
        msg = "TypeVar(name, constraint, ...): constraints must be types."
        self.__constraints__ = tuple(_type_check(t, msg) for t in constraints)

    def _has_type_var(self):
        return False

    def __repr__(self):
        return self.__name__

    def __subclasscheck__(self, cls):
        if cls is self:
            return True
        if cls is Any:
            return True
        if self.__constraints__:
            return issubclass(cls, self.__constraints__)
        return True

def _has_type_param(self):
    if self.__parameters__:
        for t in self.__parameters__:
            if _has_type_param(t):
                return True
    return False

#
# Extend typing.Generic to accept TypeParam parameters. 
#
class GenericMeta(GenericMeta):
    def __new__(cls, name, bases, namespace,
            parameters=None, origin=None, extra=None):
        
        if parameters is None:
            # Extract parameters from direct base classes.  Only
            # direct bases are considered and only those that are
            # themselves generic, and parameterized with type
            # variables.  Don't use bases like Any, Union, Tuple,
            # Callable or type variables.
            params = None
            for base in bases:
                if isinstance(base, TypingMeta):
                    if not isinstance(base, typing.GenericMeta):
                        raise TypeError(
                            "You cannot inherit from magic class %s" %
                            repr(base))
                    if base.__parameters__ is None:
                        continue  # The base is unparameterized.
                    for bp in base.__parameters__:
                        if _has_type_param(bp) and not isinstance(bp, TypeVar):
                            raise TypeError(
                                "Cannot inherit from a generic class "
                                "parameterized with "
                                "non-type-variable %s" % bp)
                        if params is None:
                            params = []
                        if bp not in params:
                            params.append(bp)
            if params is not None:
                parameters = tuple(params)
        self = TypingMeta.__new__(cls, name, bases, namespace, _root=True)
        self.__parameters__ = parameters
        if extra is not None:
            self.__extra__ = extra
        # Else __extra__ is inherited, eventually from the
        # (meta-)class default above.
        self.__origin__ = origin
        return self
    
    def __getitem__(self, params):
        if not isinstance(params, tuple):
            params = (params,)
        if not params:
            raise TypeError("Cannot have empty parameter list")
        params = tuple(params)
        if self.__parameters__ is None:
            for p in params:
                if not isinstance(p, (TypeVar, TypeParam)):
                    raise TypeError("Initial parameters must be "
                                    "type variables; got %s" % p)
            if len(set(params)) != len(params):
                raise TypeError(
                    "All type variables in Generic[...] must be distinct.")
        else:
            if len(params) != len(self.__parameters__):
                raise TypeError("Cannot change parameter count from %d to %d" %
                                (len(self.__parameters__), len(params)))
            for new, old in zip(params, self.__parameters__):
                if isinstance(old, TypeVar):
                    if not old.__constraints__:
                        # Substituting for an unconstrained TypeVar is OK.
                        continue
                    if issubclass(new, Union[old.__constraints__]):
                        # Specializing a constrained type variable is OK.
                        continue
                if not issubclass(new, old):
                    raise TypeError(
                        "Cannot substitute %s for %s in %s" %
                        (_type_repr(new), _type_repr(old), self))

        return self.__class__(self.__name__, self.__bases__,
                              dict(self.__dict__),
                              parameters=params,
                              origin=self,
                              extra=self.__extra__)


class Generic(Generic, metaclass=GenericMeta):
    pass


    
class ParametricMeta(GenericMeta):
    def __getitem__(self, params):
        if _is_concrete(params):
            return self.__origin__.__new_type__(params)
        else:
            return super().__        

class Parametric(Generic, metaclass=ParametricMeta):
    pass


N = TypeParam('N', int)
F = TypeParam('F', float)
S = TypeParam('S', str)

if __name__ == '__main__':
    from typing import T
    
    print(Generic[T])
    print(Generic[N, T])
    
    class Vector(Generic[N, T]):
        pass
    
    print(Vector[2, int])
    
