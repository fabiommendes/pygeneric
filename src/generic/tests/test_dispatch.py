import pytest
from generic import generic

def mk(out):
    '''Make a generic function to test dispatch'''
    
    def teller(*args):
        return out
    return teller

def register(generic,  *types):
    out = types if len(types) != 1 else types[0]
    generic.register(*types, func=mk(out))


def test_linear_single_dispatch():
    class A(int): pass
    class B(A): pass
    
    f = generic(lambda: None)
    register(f, object)
    register(f, int)
    register(f, A)

    x = object()
    assert f(x) == object
    assert f(0) == int 
    assert f(A(0)) == A
    assert f(B(0)) == A
    assert f(0.0) == object
            
    
def test_linear_multiple_dispatch():
    class A(int): pass
    class B(A): pass
    
    f = generic(lambda: None)
    register(f, object, object)
    register(f, int, int)
    register(f, int, A)
    register(f, A, A)

    x = object()
    assert f(x, x) == (object, object)
    assert f(0, 0) == (int, int) 
    assert f(0, A(0)) == (int, A)
    assert f(0, B(0)) == (int, A)
    assert f(A(0), 0) == (int, int)
    assert f(A(0), B(0)) == (A, A)
    assert f(0, x) == (object, object)

    
if __name__ == '__main__':
    #pytest.main('test_dispatch.py -q --tb=native')
    pytest.main('test_dispatch.py -q')