import pytest
import six
from generic import generic


@pytest.fixture
def addfunc():
    @generic
    def addfunc(x, y):
        return x + y
    
    @addfunc.register(int, int)
    def addfunc(x, y):
        return x + y + 1
    
    @addfunc.register(float, float)
    def addfunc(x, y):
        return x + y + 1.5
    
    return addfunc
    

#
# Test functionality
#
def test_overloads(addfunc):
    assert addfunc(1, 1) == 3
    assert addfunc(1.0, 1.0) == 3.5
    assert addfunc(1, 1.0) == 2
    assert addfunc(1.0, 1) == 2


def test_singledispatch_interface(addfunc):
    assert set(addfunc.registry()) == {(object, object), (int, int), (float, float)}
    assert addfunc.dispatch(float, int) == addfunc[float, int]
    assert addfunc.dispatch(int, int) == addfunc[int, int]
    
    
def test_mapping_interface(addfunc):
    assert addfunc[int, int](1, 2) == addfunc(1, 2)
    assert (int, int) in addfunc
    assert set(list(addfunc)) == {(object, object), (int, int), (float, float)}
    assert len(addfunc) == 3
    
    
def test_which(addfunc):
    assert addfunc.which(1, 2) is addfunc[int, int]
    assert addfunc.which(1, 2.0) is addfunc[int, float]
    
    
def test_register(addfunc):
    addfunc.register(int, float, func=lambda x, y: x + y + 1.25)  
    assert addfunc(1, 2) == 4
    assert addfunc(1, 2.0) == 4.25
    assert addfunc(1.0, 2.0) == 4.5
    

def test_register_decorator(addfunc):
    old = addfunc
    
    @addfunc.register(int, float)
    def addfunc(x, y): 
        return x + y + 1.25

    assert addfunc is old 

    @addfunc.register(float, int)
    def addfloatint(x, y): 
        return x + y + 1.25

    assert addfunc(1, 2) == 4
    assert addfunc(1, 2.0) == 4.25
    assert addfunc(2.0, 1) == 4.25
    assert addfunc(1.0, 2.0) == 4.5
    assert addfloatint(1, 2) == 4.25

    
def test_overload_explicit(addfunc):
    old = addfunc
    
    @addfunc.overload((int, float), float)
    def addfunc(x, y): 
        return x + y + 1.25

    assert addfunc is old 

    @addfunc.overload((float, int), float)
    def addfloatint(x, y): 
        return x + y + 1.25

    assert addfunc(1, 2) == 4
    assert addfunc(1, 2.0) == 4.25
    assert addfunc(2.0, 1) == 4.25
    assert addfunc(1.0, 2.0) == 4.5
    assert addfloatint(1, 2) == 4.25


if six.PY3:
    def test_overload_implicit(addfunc):
        old = addfunc
        
        @addfunc.overload
        def addfunc(x: int, y: float) -> float: 
            return x + y + 1.25
    
        assert addfunc is old 
    
        @addfunc.overload
        def addfloatint(x: float, y: int) -> float: 
            return x + y + 1.25
    
        assert addfunc(1, 2) == 4
        assert addfunc(1, 2.0) == 4.25
        assert addfunc(2.0, 1) == 4.25
        assert addfunc(1.0, 2.0) == 4.5
        assert addfloatint(1, 2) == 4.25


def test_factory(addfunc):
    @addfunc.register(int, int, object, factory=True)
    def factory(argtypes, restype):
        delta = 0.5 if argtypes[-1] is float else 0
        def func(x, y, z):
            return x + y + z + delta
        return func
    
    assert (int, int) in addfunc
    assert (int, int, object) in addfunc
    assert (int, int, object, object) not in addfunc
    assert addfunc(1, 2, 3) == 6
    assert addfunc(1, 2, 3.0) == 6.5
    
    
#
# Regressions
#
def test_memory_leaks(addfunc):
    # (sometimes they appear due to bugs in the cython code...)
     
    import psutil
    import gc
    process = psutil.Process()
    
    # Hit the cache
    gc.collect()
    for _ in range(2):
        addfunc(1, 2)
        addfunc(1.0, 2.0)
        addfunc(1, 2.0)
    
    # Hammer CPU    
    mem0 = process.memory_info()
    N = 500
    for _ in range(N):
        addfunc(1, 2)
        addfunc(1.0, 2.0)
        addfunc(1, 2.0)
        
    mem1 = process.memory_info()
    delta = mem1.rss - mem0.rss
    assert delta == 0