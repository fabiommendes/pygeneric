import pytest
from generic import convert, get_conversion, set_conversion, InexactError
from generic import promote, promote_type, set_promotion, set_promotion_rule


@pytest.fixture
def T1():
    class T1:
        def __init__(self, data):
            self.data = data

        def __eq__(self, other):
            if type(other) == type(self):
                return self.data == other.data
            return NotImplemented

        def __repr__(self):
            return 'T1(%r)' % self.data

    return T1


@pytest.fixture
def T2():
    class T2:
        def __init__(self, data):
            self.data = data

        def __eq__(self, other):
            if type(other) == type(self):
                return self.data == other.data
            return NotImplemented

        def __repr__(self):
            return 'T2(%r)' % self.data

    return T2


#
# Conversions
#
def test_successfull_conversions_of_base_types():
    # Same types
    assert convert(1, int) == 1
    assert type(convert(1, int)) is int
    assert convert(1.0, float) == 1.0
    assert type(convert(1.0, float)) is float

    # Mixing types
    assert convert(1, float) == 1.0
    assert type(convert(1, float)) is float
    assert convert(1.0, int) == 1
    assert type(convert(1.0, int)) is int
    assert convert(1, bool) is True
    assert convert(0, bool) is False
    assert convert(True, float) == 1.0
    assert type(convert(True, float)) is float
    assert convert(True, int) == 1
    assert type(convert(True, int)) is int


def test_failed_conversions_of_base_types():
    with pytest.raises(InexactError):
        convert(1.5, int)

    with pytest.raises(InexactError):
        convert(2, bool)

    with pytest.raises(InexactError):
        convert(1.5, bool)

    with pytest.raises(TypeError):
        convert("42", int)


def test_same_type_and_subtypes_conversion():
    class A: pass
    class B(A): pass
    class C(int): pass
    a, b, c = A(), B(), C()

    assert convert(a, A) is a
    assert convert(b, B) is b
    assert convert(c, C) is c
    assert convert(b, A) is b


def test_conversion_failures():
    class A: pass
    class B: pass
    a, b = A(), B()

    with pytest.raises(TypeError):
        convert(a, B)
    with pytest.raises(TypeError):
        convert(b, A)
    with pytest.raises(TypeError):
        get_conversion(A, B)
    with pytest.raises(ValueError):
        get_conversion(a, b)


def test_set_conversions(T1, T2):
    set_conversion(T1, T2, lambda x: T2(x.data))
    a, b = T1(1), T2(1)

    assert a != b
    assert convert(a, T2) == b

    with pytest.raises(TypeError):
        convert(b, T1)

#
# Promotions
#
def assert_allsame(x, y):
    for a, b in zip(x, y):
        assert a == b
        assert type(a) is type(b)

def test_successfull_promotions_of_base_types():
    assert_allsame(promote(1, 2), (1, 2))
    assert_allsame(promote(1.0, 2.0), (1.0, 2.0))
    assert_allsame(promote(True, 2), (1, 2))
    assert_allsame(promote(2, True), (2, 1))
    assert_allsame(promote(True, 2, 3.0), (1.0, 2.0, 3.0))


def test_successfull_type_promotions_of_base_types():
    assert promote_type(int, float) is float
    assert promote_type(bool, complex) is complex


def test_custom_promotions(T1, T2):
    a, b = T1(1), T2(2)

    # Prepare conversions
    set_conversion(T2, T1, lambda x: T1(x.data))
    set_promotion_rule(T1, T2, T1)

    @set_promotion(T1, int, restype=int)
    @set_promotion(T2, int, restype=int)
    def promote_to_int(x, y):
        return convert(x.data, int), y

    # Create examples and test
    assert_allsame(promote(a, b), (a, T1(2)))
    assert_allsame(promote(a, 2), (1, 2))
    assert_allsame(promote(a, b, 3), (1, 2, 3))
    assert_allsame(promote(3, b, a), (3, 2, 1))


def test_automatic_promotions():
    class A: pass
    class B(A): pass
    a, b = A(), B()

    assert_allsame(promote(a, b), (a, b))
    assert_allsame(promote(a, a), (a, a))
    assert promote_type(A, B) is A
    assert promote_type(B, A) is A


def test_failed_promotions():
    with pytest.raises(TypeError):
        promote("42", 42)

    with pytest.raises(RuntimeError):
        set_promotion_rule(float, int, int)

    with pytest.raises(RuntimeError):
        set_promotion_rule(int, float, int)

    with pytest.raises(RuntimeError):
        set_promotion(int, float, function=int)

    with pytest.raises(RuntimeError):
        set_promotion(float, int, function=int)

    with pytest.raises(RuntimeError):
        set_promotion_rule(str, str, str)

    with pytest.raises(RuntimeError):
        set_promotion(str, str, function=str)

if __name__ == '__main__':
    pytest.main('test_conversions.py -q')
