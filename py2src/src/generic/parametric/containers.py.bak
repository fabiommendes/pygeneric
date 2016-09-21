from generic.parametric.base import Parametric

__all__ = ['List', 'Dict']


class List(Parametric, list):
    """A parametric list with values of uniform type.

    List[T] objects are neither covariant nor contravariant, i.e., List[T] is
    neither a subclass nor a superclass of List[S] even when T and S share a
    subclass relation."""

    __parameters__ = (type,)

    @staticmethod
    def __finalizetype__(cls):
        cls.dtype = cls.__parameters__[0]
        return cls

    @classmethod
    def __abstract_new__(cls, data=()):
        # TODO: implement correctly. maybe move some functions from smallvectors
        # to "here
        data = list(data)
        types = set(type(x) for x in data)
        if len(types) != 1:
            raise NotImplementedError
        else:
            return cls[types.pop()](data)

    def __init__(self, data=()):
        T = self.dtype
        if all(isinstance(x, T) for x in data):
            super().__init__(data)
        else:
            raise TypeError('contain non-%s elements' % T.__name__)

    def __setitem__(self, item, value):
        T = self.dtype
        if isinstance(item, int) and not isinstance(value, T):
            self.__raise_value_insertion_error(value)
        elif isinstance(item, slice):
            data = list(value)
            invalid = [x for x in data if not isinstance(x, T)]
            if invalid:
                self.__raise_value_insertion_error(invalid[0])
        super().__setitem__(item, value)

    def insert(self, idx, value):
        if isinstance(value, self.dtype):
            super().insert(idx, value)
        else:
            self.__raise_value_insertion_error(value)

    def append(self, value):
        if isinstance(value, self.dtype):
            super().append(value)
        else:
            self.__raise_value_insertion_error(value)

    def __raise_value_insertion_error(self, value):
        fmt = type(value).__name__, type(self).__name__
        raise TypeError('cannot insert %s values on %s' % fmt)


class Dict(Parametric, dict):
    """A parametric dictionary with values of uniform key, value types.

    Dict[T1, T2] objects are neither covariant nor contravariant, i.e.,
    Dict[T1, T2] is neither a subclass nor a superclass of Dict[S1, S2] even
    when each T and S share a subclass relation."""

    __parameters__ = (type, type)

    @staticmethod
    def __finalizetype__(cls):
        cls.keytype, cls.valuetype = cls.__parameters__
        return cls

    @classmethod
    def __abstract_new__(cls, data=(), **kwds):
        # TODO: implement correctly. maybe move some functions from smallvectors
        # to "here

        D = dict(data, **kwds)

        # Get data types
        keys = list(D.keys())
        types = set(type(x) for x in keys)
        if len(types) != 1:
            raise NotImplementedError
        else:
            ktype = types.pop()

        values = list(D.values())
        types = set(type(x) for x in values)
        if len(types) != 1:
            raise NotImplementedError
        else:
            vtype = types.pop()

        return cls[ktype, vtype](D)

    def __init__(self, data=(), **kwds):
        super().__init__(data, **kwds)
        self.__assert_dict(self)

    def __setitem__(self, key, value):
        kT, vT = self.__parameters__
        if not isinstance(key, kT) or not isinstance(value, vT):
            raise TypeError('invalid key-value pair')
        super().__setitem__(key, value)

    def update(self, data=(), **kwds):
        D = dict(data, **kwds)
        self.__assert_dict(D)
        super().update(D)

    def __assert_dict(self, D):
        kT, vT = self.__parameters__
        is_good_type = (isinstance(k, kT) and isinstance(v, vT)
                        for (k, v) in D.items())
        if not all(is_good_type):
            raise TypeError('contain invalid key-value pairs')


class _Set(Parametric, set):
    """A parametric set object with values of uniform type.

    Set[T] objects are neither covariant nor contravariant, i.e., Set[T] is
    neither a subclass nor a superclass of Set[S] even when T and S share a
    subclass relation."""

    # TODO: implement this!
    @classmethod
    def __abstract_new__(cls, *args, **kwds):
        raise NotImplementedError


class _Tuple(Parametric, tuple):
    """A parametric tuple object with values of uniform type.

    Set[T] objects are neither covariant nor contravariant, i.e., Set[T] is
    neither a subclass nor a superclass of Set[S] even when T and S share a
    subclass relation."""

    # TODO: implement this!
    @classmethod
    def __abstract_new__(cls, *args, **kwds):
        raise NotImplementedError


if __name__ == '__main__':
    x = List([1, 2])
    # x.append(3.0)
    print(x[0])
    print(x)

    d = Dict(foo=1, bar=2)
    print(d)
    print(type(d))
    d['foobar'] = 3
    print(d)
    d['ham'] = 42.0
