import pytest
from generic.op import Object, add, sub, mul, div, eq, ne, gt, lt, ge, le 


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
            return self.data == other.data
        
    @add.register(int, T)
    def add1(x, y):
        return T(x + y.data) 
    
    @add.register(T, int)
    def add2(y, x):
        return T(x + y.data)
    
    return T

#
# Test arithmetic operations
#
def test_simple_add(T):
    a = T(1)
    b = T(2)
    c = T(3)
    assert a + b == c
    assert a + 2 == c
    assert 1 + b == c
    

def test_overloaded_add(T):
    add.register(T, float, func=lambda x, y: T(x.data + y))
    add.register(float, T, func=lambda x, y: T(x + y.data))
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
        

def test_arithmetic_works_with_third_type(T):
    class B:
        def __add__(self, other):
            return 1 + other

        def __radd__(self, other):
            return other + 1

    a = T(2)
    b = B()
    assert a + b == T(3)
    assert b + a == T(3)


def test_equality_comparisons_works_with_third_type(T):
    class B:
        def __eq__(self, other):
            return other == T(1)

    a = T(1)
    c = T(2)
    b = B()
    assert a == b
    assert b == a
    assert c != b
    assert b != c


#
# Test relations
#
def test_overload_eq(T):
    eq.register(T, object, func=lambda x, y: x.data == y)
    eq.register(object, T, func=lambda x, y: y.data == x)
    assert T(1) == 1
    assert not (T(1) == 2)
    assert T(1) != 2


def test_overload_ordering(T):
    gt.register(T, int, func=lambda x, y: x.data > y)
    gt.register(int, T, func=lambda x, y: x > y.data)
    assert T(2) > 1
    assert not (T(1) > 2)
    assert T(1) < 2


#
# Generic operators
#
def test_generic_operators_work_for_non_generic_types():
    assert add(1, 1) == 2
    assert add(1.0, 1) == 2
    assert sub(1, 1) == 0
    assert sub(1.0, 1) == 0
    assert mul(1, 1) == 1
    assert mul(1.0, 1) == 1
    assert div(1, 1) == 1
    assert div(1.0, 1) == 1


def test_generic_relations_work_for_non_generic_types():
    assert eq(1, 1) and not ne(1, 1)
    assert le(1, 1) and lt(1, 2)
    assert ge(1, 1) and gt(2, 1)
    assert ne(1, 2) and not eq(2, 1)




if __name__ == '__main__':
    #pytest.main('test_operator.py -q --tb=native')
    pytest.main('test_operator.py -q')
    #pytest.main('test_operator.py -q')