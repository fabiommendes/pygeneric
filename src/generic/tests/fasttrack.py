'''
Fast track your code to the best implementation!
================================================

The `fasttrack` library is based on the idea that a module can have multiple
implementations of the same function and the best one will be choosen at
runtime depending on which libraries are available on the host system.

It also provide some utilities for doing crude benchmarks and for testing for
performance regressions across different implementations.

Some typical usages are:
    * You have a function that can be accelerated by some python library
      (e.g. numpy), but you want to provide a fallback implementation;
    * You want to fiddle with one of the many JITs available for Python. Most
      users won't have all of them installed, so you may use a common
      interface and maybe also provide a fallback Python implementation;
    * Maybe the most efficient Python code you have is great for CPython, but
      sucks for other implementations and vice-versa;
    * You are optimizing code, but you want to keep some old implementions
      around in case your new blazing fast ones end up having some corner case
      unsolvable bugs;
    * You want to easily compare different optimizations for the same function,
      and to check if newer representations present regressions in speed or
      if they have the same outputs;
    * You want to quickly test the speed of some code in the Python shell to
      see if other implementations provide viable performance;


Usage
=====

Let us implement a function using both numpy and regular python as fallback.
First, as a convenience, we use the try_import() function. It returns the
desired module if it exists and None otherwise.

>>> np = try_import('numpy')

Now we are ready to implement both functions:

>>> @numpy
... def sum_of_sum(a, b):
...     return (np.asarray(a) + b).sum()

And a pure-Python fallback

>>> @fallback
... def sum_of_sum(a, b):
...     return sum(x + y for (x, y) in zip(a, b))

Now, if the user has numpy installed, it will use the first implementation,
otherwise, sum_of_sum() will fallback to the second.


'''
import contextlib
import time
import importlib
import weakref
import imp
import os

__all__ = ['try_import', 'timeit', 'numpy', 'fallback']

PYTHON_IMPLEMENTATIONS = ['python2', 'python3', 'cpython', 'pypy', 'ironpython', 'jython', 'asmjs', 'nacl']
CURRENT_IMPLEMENTATION = None  # later binding
DEFAULT_ORDER = ['jit', 'numpy', 'fallback']
DEFAULT_FALLBACK = None  # later binding
USEWEAKREF = True
JOB = None

#==============================================================================
# Check python implementation
#==============================================================================
def which_python():
    '''Returns a list of strings describing which python implementations are
    compatible with the host system.'''

    pythons = []
    for python in PYTHON_IMPLEMENTATIONS:
        poll = getattr(MultiFunction, '_accepts_' + python)
        if poll():
            pythons.append(python)

    if not (set(pythons) - set(['python2', 'python3'])):
        pythons.append('unknown_python')
    return pythons

def fix_implementations():
    '''Fix the DEFAULT_FALLBACK constant to prioritize the running
    implementation'''

    global DEFAULT_FALLBACK, CURRENT_IMPLEMENTATION

    CURRENT_IMPLEMENTATION = which_python()
    L = DEFAULT_FALLBACK = CURRENT_IMPLEMENTATION + ['fallback', 'python']
    for x in PYTHON_IMPLEMENTATIONS:
        if x not in L:
            L.append(x)

#==============================================================================
# Function MultiFunction
#==============================================================================
class MultiFunction(object):
    '''Controls which implementation for some function will be used.

    It must be fed with some alternatives and it keeps the _chosen one in the
    _chosen attribute.'''

    _instances = weakref.WeakSet()

    def __init__(self, name, keepref=True, order=()):
        self.name = name
        self._valid = weakref.WeakValueDictionary()
        self._all_keys = set()
        self._chosen = self._fallback_function
        self._order = list(order) or None
        self._chosen_descr = None
        self._instances.add(self)
        self._refs = None if not keepref else []

    # Properties --------------------------------------------------------------
    @property
    def order(self):
        if self._order is not None:
            return self._order
        else:
            return DEFAULT_ORDER[:]

    # API functions -----------------------------------------------------------
    def feed(self, descr, func):
        '''Feeds a new function that may or may not be _chosen given the
        description'''

        # Tests for each condition and choose de
        if self.accepts(descr):
            if self._refs is not None:
                self._refs.append(func)

            if self._chosen_descr is None or self.is_better(descr, self._chosen_descr):
                self._chosen = func
                self.chosen_descr = descr

            self._valid[descr] = func

    def register(self, func=None, descr=None):
        '''Decorator used to register new functions in a given MultiFunction'''

        # When func=None, it is being called in the decorator form
        if func is None:
            def decorator(func):
                self.feed(descr, func)
                return self._decorated()
            return decorator

        self.feed(descr, func)

    def is_better(self, descr1, descr2):
        '''Return True if descr1 has a higher or equal priority than descr2'''

        if descr1 in DEFAULT_FALLBACK:
            return False
        elif descr2 in DEFAULT_FALLBACK:
            return True

        order = self.order

        def _get_index(x):
            try:
                return order.index(x)
            except TypeError:
                try:
                    if ' ' in x:
                        return order.index(x.partition(' ')[0])
                except ValueError:
                    pass
            return len(order)

        idx1, idx2 = map(_get_index, [descr1, descr2])
        return idx1 <= idx2

    def accepts(self, descr):
        '''Return True if the module is supported by the system'''

        descr = descr.partition(' ')[0]
        if descr in DEFAULT_FALLBACK:
            return True

        try:
            imp.find_module(descr.partition(' ')[0])
            return True
        except ImportError:
            return False

    # Implementss special tests -----------------------------------------------
    @classmethod
    def _accepts_python2(cls):
        '''Tests if it is running in python2'''

        pass

    @classmethod
    def _accepts_python3(cls):
        '''Tests if it is running in python3'''

        pass

    @classmethod
    def _accepts_asmjs(cls):
        '''Tests if it is running the asm.js compilation of CPython'''

        pass

    @classmethod
    def _accepts_nacl(cls):
        '''Tests if it is running Google's NaCL compilation of CPython'''

        pass

    @classmethod
    def _accepts_pypy(cls):
        '''Tests if it is running in PyPy'''

        pass

    @classmethod
    def _accepts_ironpython(cls):
        '''Tests if it is running in IronPython'''

        pass

    @classmethod
    def _accepts_jython(cls):
        '''Tests if it is running in Jython'''

        pass

    @classmethod
    def _accepts_cpython(cls):
        '''Tests if it is running in CPython'''

        pass

    # Magic methods and other private functions
    def __call__(self, *args, **kwds):
        '''Makes job work as a decorator'''

        return self.current(*args, **kwds)

    def _fallback_function(self, *args, **kwds):
        raise RuntimeError('no acceptable implementation was found for your '
                           'system.\nPlease define a fallback function')

    def _decorated(self):
        '''The return of this function is passed as the result of all
        decorated functions'''

        return self._chosen


class TimedMultiFunction(MultiFunction):
    '''Executes all implementations at the same time and keeps track of the
    time spent in each one of them separately.

    Example
    -------

    Let us define a naive and a smart implementation of the same problem of
    summing the first numbers from 1 to N.

    >>> timed = TimedMultiFunction('sum_numbers')
    >>>
    >>> @timed.register(descr='python (naive)')
    ... def sum_numbers(N):
    ...     return sum(range(1, N + 1))
    >>>
    >>> @timed.register(descr='python (smart)')
    ... def sum_numbers(N):
    ...     return int(N * (N + 1) / 2)

    Everything is transparent to the user. Under the hood, it is calling both
    implementations and saving the time taken to run each.

    >>> sum_numbers(4)  # 10, our prefered triangular number
    10

    Now we can run the function a few times and see how well it performs in
    each implementation

    >>> for i in range(0, 1000):
    ...     res = sum_numbers(i)
    >>> sum_numbers.report(sort_by='time')                     # doctest: +SKIP
    Performance test for sum_numbers()
    ----------------------------------
    <BLANKLINE>
        python (smart): 0.0028 sec
        python (naive): 0.0142 sec
    '''

    def __init__(self, name, order=(), eqfunc=None):
        super(TimedMultiFunction, self).__init__(name, True, order)
        self._timings = {}
        self._nruns = 0
        self._valid = {}
        self._eqfunc = eqfunc

    def __call__(self, *args, **kwds):
        if not self._valid:
            self._fallback_function()

        timings = self._timings
        results = []

        for descr, func in self._valid.items():
            with timeit() as delta_t:
                res = func(*args, **kwds)
            timings[descr] = timings.get(descr, 0) + delta_t.value
        self._nruns += 1

        # Check if results are all equal
        self.assure_equal(results)
        return res

    def assure_equal(self, values):
        pass

    def _decorated(self):
        return self

    def get_timings(self, reset=True):
        return self._timings

    def report(self, reset=True, sort_by='priority'):
        # Sort contents
        if sort_by == 'time':
            L = sorted(self._timings.items(), key=lambda x: x[1])
        else:
            raise ValueError('invalid sort method: %r' % sort_by)

        # Print it
        msg = 'Performance test for %s()' % self.name
        print(msg + '\n' + '-' * len(msg), '\n')
        for name, time in L:
            print('    %s: %s sec' % (name, time))

#==============================================================================
# Special decorators
#==============================================================================
def haslib(libname, func=None, descr=None):
    '''Used to mark a implementation that depends on the existence of a given
    python library.

    Example
    -------

    First we import our libraries

    >>> exotic_math = try_import('exotic_math')
    >>> math = try_import('math')
    >>> # (of course try_import here is silly: all pythons have the math library!)

    Then define our functions

    >>> @haslib('math')
    ... def func(x):
    ...     print('using regular math')
    ...     return math.sqrt(2 * x)

    >>> @haslib('exotic_math')
    ... def func(x):
    ...     print('using exotic math')
    ...     return exotic_math.exotic_sqrt(2 * x)

    Of course, since we don't have tha second library, the "math"
    implementation was used

    >>> func(2)
    using regular math
    2.0

    `fasttrack` prioritizes implementations in the order::

        compiled > jit-based > numpy > other python libraries > fallback

    Since "math" and "exotic_math" falls in the last category, the last
    implementation which is acceptable has priority. A system that has the
    "exotic_math" library would use the second implementation. If we define
    another supported implementation it will have priority over "math"::

    >>> cmath = try_import('cmath')
    >>> @haslib('cmath')
    ... def func(x):
    ...     print('using complex math')
    ...     return cmath.sqrt(2 * x)
    >>> func(2)
    using complex math
    (2+0j)
    '''
    if descr:
        libname = '%s (%s)' % (libname, descr)

    def decorator(func):
        global JOB
        name = func.__name__
        if JOB is None or JOB.name != name:
            JOB = MultiFunction(name)
        JOB.feed(libname, func)
        return JOB._decorated()

    if func is None:
        return decorator
    else:
        decorator(func)

def numpy(func=None, **kwds):
    '''Marks that a function requires the numpy library'''

    return haslib('numpy', **kwds)(func)

def fallback(func=None, **kwds):
    '''Marks the fallback implementation of a function'''

    return haslib('fallback', **kwds)(func)

def python2(func=None, **kwds):
    '''Marks a implementation that is only valid in python 2

    (Obviously this decorator can't handle the syntax differences).'''

    return haslib('python2', **kwds)(func)

def python3(func=None, **kwds):
    '''Marks a implementation that is only valid in python 3

    (Obviously this decorator can't handle the syntax differences).'''

    return haslib('python2', **kwds)(func)

def cpython(func=None, **kwds):
    '''Marks the default fallback for CPython'''

    return haslib('cpython', **kwds)(func)

def pypy(func=None, **kwds):
    '''Marks the default fallback for PyPy'''

    return haslib('pypy', **kwds)(func)

def ironpython(func=None, **kwds):
    '''Marks the default fallback for IronPython'''

    return haslib('ironpython', **kwds)(func)

def jython(func=None, **kwds):
    '''Marks the default fallback for Jython'''

    return haslib('jython', **kwds)(func)

def asmjs(func=None, **kwds):
    '''Marks the default fallback for the asm.js compilation of CPython'''

    return haslib('asmjs', **kwds)(func)

def nacl(func=None, **kwds):
    '''Marks the default fallback for CPython compilation in Google's NaCl
    platform '''

    return haslib('nacl', **kwds)(func)

#==============================================================================
# Import mechanisms
#==============================================================================
def try_import(*args, **kwargs):
    '''It returns the first module that can be imported from the list. If no
    modules are found, it returns None.

    If the optional `raises=True` than it raises an ImportError upon failure.

    Examples
    --------

    >>> print(try_import('math')) # doctest: +ELLIPSIS
    <module 'math' from '...'>

    >>> print(try_import('module_that_does_not_exists'))
    None
    '''

    # Process arguments
    raises = False
    if not kwargs:
        pass
    elif len(kwargs) != 1:
        raise TypeError('invalid number of keyword arguments')
    elif 'raises' in kwargs:
        raises = kwargs['raises']
    else:
        raise TypeError('invalid keyword argument: %s' % kwargs.popitem()[0])

    # Import modules in sequence
    for module in args:
        try:
            return importlib.import_module(module)
        except ImportError:
            pass
    else:
        if raises:
            raise ImportError

#==============================================================================
# Timeit operations
#==============================================================================
class HasValue(object):
    '''Holds a simple .value attribute that can be used to store anything'''

    __slots__ = ['value']
    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)

@contextlib.contextmanager
def timeit(title=None):
    '''An easy way to test the speed of some code using with statements.

    Example
    -------

    >>> with timeit('simple loop') as dt:                      # doctest: +SKIP
    ...     S = 0
    ...     for i in range(1000000):
    ...         S += i
    simple loop: 0.201 sec

    The execution time is saved in the dt.value attribute:

    >>> dt.value                                               # doctest: +SKIP
    0.20119047164916992

    '''

    gettime = time.time
    out = HasValue(None)
    t0 = gettime()
    yield out
    delta = gettime() - t0
    out.value = delta
    if title is not None:
        delta_st = str(delta)
        print('%s: %s sec' % (title, delta))

#==============================================================================
# Late binding
#==============================================================================
fix_implementations()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
