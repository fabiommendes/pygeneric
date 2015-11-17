import pytest
from generic.parametric import Parametric, ParametricMeta

    
@pytest.fixture
def A():
    class A(Parametric):
        __abstract__ = True
        __parameters__ = [int, type]
    return A

@pytest.fixture
def B():
    class B(Parametric):
        __parameters__ = [int, type]
    return B


def test_abstract_parameters(A, B):
    assert A.__parameters__ == (int, type)
    assert B.__parameters__ == (int, type)
    assert B[2, float].__parameters__  == (2, float)        


def test_abstract(A):
    assert A.__abstract__ == True
    assert A.__origin__ == None
    assert isinstance(A.__subtypes__, dict)
    
    
def test_sub_abstract(A):
    T = A[2, float]
    assert T.__abstract__ == True
    assert T.__origin__ == A
    assert T.__subtypes__ == None
    
    
def test_origin(B):
    assert B.__abstract__ == False
    assert B.__origin__ == None
    assert isinstance(B.__subtypes__, dict)


def test_concrete_not_abstract(B):
    assert B[2, float].__abstract__ == False
    
    
def test_concrete_origin(B):
    assert B[2, float].__origin__ == B
    assert B[2, float].__subtypes__ == None

    
def test_partial_parameters(B):
    assert Parametric.__parameters__ == None
    assert B.__parameters__ == (int, type)
    assert B[2].__parameters__ == (2, type)


def test_no_concrete_parametrization(B):
    with pytest.raises(TypeError):
        B[2, float][2, int]

    
def test_origin_parametrization(B):
    assert B[2, float] is B[2, float]
    
    
def test_abstract_parametrization(A):
    assert A[2, float] is A[2, float]


def test_no_abstract_instantiation(A):
    with pytest.raises(TypeError):
        A(1, 2)


def test_no_parametric_abstract_instantiation(A):
    with pytest.raises(TypeError):
        A[2, float](1, 2)


def test_correct_metatypes(A, B):
    assert type(A) == ParametricMeta
    assert type(B) == ParametricMeta
    assert type(B[2, float]) == ParametricMeta

    
def test_concrete_params(A, B):
    assert B[2, float].__parameters__ == (2, float)
    assert A[2, float].__parameters__ == (2, float)


def test_partial_params(B):
    assert B[2].__parameters__ == (2, type)
    assert B[2, None] == B[2]
    assert B[2, ...] == B[2]


def test_abstract_from_origin(B):
    assert B[2].__abstract__ == True
    assert B[2, None].__abstract__ == True

    
def test_abstract_ellipsis(B):
    assert B[2, ...].__abstract__ == True
    assert B[..., float].__abstract__ == True

    
def test_concrete_subclass_is_concrete(B):
    class B2(B[2, float]):
        pass
    assert B2.__concrete__ == True
    assert B2.__subtypes__ == None


if __name__ == '__main__':
    import os
    os.system('py.test test_parametric.py -q')