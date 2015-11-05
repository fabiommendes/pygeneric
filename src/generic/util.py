#
# Error functions
#
def get_no_methods_error(func, args=None, types=None):
    '''Format and return a TypeError for the given func when called with the 
    given arguments'''

    if args:
        types = [type(x) for x in args]

    name = func if isinstance(func, str) else getattr(func, '__name__', func)
        
    if types is None:
        return TypeError('invalid call to %s()' % func)
    else:
        data = ', '.join(T.__name__ for T in types)
        return TypeError('no method found for %s(%s)' % (name, data))
    
    
def raise_no_methods(func, args=None, types=None):
    '''Format and raises a TypeError for the given func when called with the 
    given arguments'''
    
    raise get_no_methods_error(func, args, types)
        

def raise_unordered_types(T1, T2):
    '''Format and raises a TypeError saying that types T1 and T2 are not 
    orderable'''
    
    raise get_unordered_types_error(T1, T2) 
    

def get_unordered_types_error(T1, T2):
    '''Format and returns a TypeError saying that types T1 and T2 are not 
    orderable'''
    
    names = T1.__name__, T2.__name__
    return TypeError('there is no order relation for %s and %s.' % names) 


def raise_unordered(x, y):
    '''Format and raises a TypeError saying that the types for x and y are not 
    orderable'''

    raise get_unordered_types_error(type(x), type(y))


#
# Pretty-printers
#
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

def tname(x):
    '''A shortcut to the object's type name'''
    
    return type(x).__name__