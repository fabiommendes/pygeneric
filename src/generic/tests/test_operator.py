import pytest
from generic import generic
from generic.operator import * 

#
# Fixtures
#
@pytest.fixture
def T():
    class T(Object):
        def __init__(self, x):
            self.data = x
            
        def __addsame__(self, other):
            return T(self.data + other.data)
        
        def __repr__(self):
            return 'T(%s)' % self.data
        
        def __eqsame__(self, other):
            print(self, other)
            return self.data == other.data
        
    @add.overload
    def add1(x: int, y: T):
        return T(x + y.data) 
    
    @add.overload
    def add2(y: T, x: int):
        return T(x + y.data)
    
    return T

#
# Test functionality -- arithmetic operations
#
def test_simple_add(T):
    a = T(1)
    b = T(2)
    c = T(3)
    assert a + b == c
    assert a + 2 == c
    assert 1 + b == c
    

def test_overloaded_add(T):
    add.register(T, float, func=add[T, int])
    add.register(float, T, func=add[int, T])
    a = T(1)
    b = T(2)
    c = T(3)
    assert a + b == c
    assert a + 2.0 == c
    assert 1.0 + b == c


def test_fails_for_no_methods(T):
    a = T(1)
    with pytest.raises(TypeError):
        a + 1.0
    with pytest.raises(TypeError):
        1.0 + a
        
        
def test_generic_operators_work_for_non_generic_types(T):
    assert add(1, 1) == 2
    assert add(1.0, 1) == 2
    assert sub(1, 1) == 0
    assert sub(1.0, 1) == 0
    assert mul(1, 1) == 1
    assert mul(1.0, 1) == 1
    assert div(1, 1) == 1
    assert div(1.0, 1) == 1

    
#
# Test functionality -- relations
#
def test_overload_eq(T):
    eq.register(T, int, func=lambda x, y: x.data == y)
    eq.register(int, T, func=lambda x, y: y.data == x)
    assert T(1) == 1
    assert not (T(1) == 2)
    assert T(1) != 2


def test_overload_ordering(T):
    gt.register(T, int, func=lambda x, y: x.data > y)
    gt.register(int, T, func=lambda x, y: x > y.data)
    assert T(2) > 1
    assert not (T(1) > 2)
    assert T(1) < 2


def test_generic_relations_work_for_non_generic_types(T):
    assert eq(1, 1) and not ne(1, 1)
    assert le(1, 1) and lt(1, 2)
    assert ge(1, 1) and gt(2, 1)
    assert ne(1, 2) and not eq(2, 1)

#
# Regressions
#
if __name__ == '__main__':
    pytest.main('test_operator.py -q --tb=native')
    #pytest.main('test_operator.py -q')