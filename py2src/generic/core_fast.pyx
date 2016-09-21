import cython
from cpython cimport PyObject, PyTuple_GET_SIZE, PyObject_Call
from cpython cimport Py_INCREF, Py_XINCREF, Py_DECREF, Py_XDECREF, Py_CLEAR

cdef extern from "Python.h":
    int PyDict_Size(PyObject*)
    PyObject* PyTuple_New(int)
    PyObject* PyTuple_GET_ITEM(PyObject*, int)
    void PyTuple_SET_ITEM(PyObject*, int, PyObject*)
    PyObject* PyDict_GetItem(PyObject* , PyObject*)

cdef class FastCache(object):

    '''Implements a multi argument dispatch function.'''

    cdef int __last_arglen
    cdef void* __last_argtypes[5]
    cdef object __last_function
    cdef dict __cache

    def __init__(self):
        self.__cache = {}
        self._cache_update()

    @cython.nonecheck(False)
    def __call__(self, *args, **kwargs):
        "Resolve and dispatch to best method."

        cdef int N = PyTuple_GET_SIZE(args)
        cdef PyObject* types = NULL
        cdef PyObject* item
        cdef int i, is_dirty = 1

        # Check if args repeats the last call types
        if self.__last_arglen == N:
            is_dirty = 0
            for i in range(N):
                T = <void*> PyTuple_GET_ITEM(<PyObject*> args, i).ob_type
                if T != self.__last_argtypes[i]:
                    is_dirty = 1
                    break

        # Not in the last call cache, try the dictionary cache instead
        if is_dirty == 1:
            # Create type tuple
            types = PyTuple_New(N)
            for i in range(N):
                item = PyTuple_GET_ITEM(<PyObject*> args, i)
                item = <PyObject*> (item.ob_type)
                Py_XINCREF(item)
                PyTuple_SET_ITEM(types, i, item)

            # Get value from cache dictionary
            item = PyDict_GetItem(<PyObject*> self.__cache, types)
            if item == NULL:
                self.__last_function = self.dispatch(*(<object> types))
            else:
                self.__last_function = <object> item

            # Save cache for next execution
            for i in range(N):
                self.__last_argtypes[i] = <void*> PyTuple_GET_ITEM(types, i)
            self.__last_arglen = N
            Py_CLEAR(types)

        # Execute the imlementation function with proper arguments
        return PyObject_Call(self.__last_function, args, kwargs)

    property _cache:
        def __get__(self):
            return self.__cache

        def __set__(self, value):
            self.__cache.update(value)

    cpdef _cache_update(self):
        self.__last_arglen = -1

cdef inline int tuples_eq(tuple t1, tuple t2, int N):
    for i in range(N):
        if t1[i] is not t2[i]:
            return False
    return True
