from generic import generic, overload
import multimethod
import multimethods
from fasttrack import timeit

N = 200000


def force(x, y):
    return x + y


def func(*args, **kwds):
    return args[0] + args[1]


@generic
def md_func(x, y):
    return x + y


@overload(md_func, (float, float))
@overload(md_func, (float, int))
@overload(md_func, (int, int))
def md_func(x, y):
    return x + y

for T in (str, list, tuple, float, complex, int):
    md_func[T] = func


@multimethod.multimethod(float, int)
@multimethod.multimethod(float, float)
@multimethod.multimethod(int, int)
def mm_func(x, y):
    return x + y


@multimethods.multimethod(int, int)
def mms_func(x, y):
    return x + y


@multimethods.multimethod(float, float)
def mms_func(x, y):
    return x + y


@multimethods.multimethod(float, int)
def mms_func(x, y):
    return x + y

with timeit('generic-different'):
    for i in range(N):
        md_func(1, 2)
        md_func(1.0, 2.0)

with timeit('generic'):
    for i in range(N):
        md_func(1, 2)

with timeit('generic-same'):
    for i in range(N):
        md_func(1, 2)
        md_func(1, 2)


def manual(x, y):
    if isinstance(x, float):
        return x + y
    elif isinstance(x, int) and isinstance(y, int):
        return x + y
    else:
        return x + y

with timeit('manual'):
    for i in range(N):
        manual(1, 2)

with timeit('simple'):
    for i in range(N):
        func(1, 2)

with timeit('multimethod'):
    for i in range(N):
        mm_func(1, 2)

with timeit('multimethods'):
    for i in range(N):
        mms_func(1, 2)
