import unittest
from generic.parametric import Parametric, ParametricMeta

    
class ParametricTestCase(unittest.TestCase):
    def setUp(self):
        class A(Parametric):
            __abstract__ = True
            __parameters__ = [int, type]
            
        class B(A):
            pass
        
        self.A = A
        self.B = B

    def test_abstract_parameters(self):
        self.assertEqual(self.A.__parameters__ , (int, type))
    
    def test_origin_parameters(self):
        self.assertEqual(self.B.__parameters__ , (int, type))
        
    def test_concrete_parameters(self):
        self.assertEqual(self.B[2, float].__parameters__ , (2, float))        
    
    def test_abstract(self):
        self.assertEqual(self.A.__abstract__, True)
        self.assertEqual(self.A.__origin__, None)
        assert isinstance(self.A.__subtypes__, dict)
        
    def test_sub_abstract(self):
        T = self.A[2, float]
        self.assertEqual(T.__abstract__, True)
        self.assertEqual(T.__origin__, self.A)
        self.assertEqual(T.__subtypes__, None)
        
    def test_origin(self):
        self.assertEqual(self.B.__abstract__, False)
        self.assertEqual(self.B.__origin__, None)
        assert isinstance(self.B.__subtypes__, dict)
    
    def test_concrete_not_abstract(self):
        self.assertEqual(self.B[2, float].__abstract__, False)
        
    def test_concrete_origin(self):
        self.assertEqual(self.B[2, float].__origin__, self.B)
        self.assertEqual(self.B[2, float].__subtypes__, None)
        
    def test_partial_parameters(self):
        self.assertEqual(Parametric.__parameters__, None)
        self.assertEqual(self.B.__parameters__, (int, type))
        self.assertEqual(self.B[2].__parameters__, (2, type))

    def test_no_concrete_parametrization(self):
        def test():
            self.B[2, float][2, int]
        self.assertRaises(TypeError, test)
        
    def test_origin_parametrization(self):
        assert self.B[2, float] is self.B[2, float]
        
    def test_abstract_parametrization(self):
        assert self.A[2, float] is self.A[2, float]

    def test_no_abstract_instantiation(self):
        def test():
            self.A(1, 2)
        self.assertRaises(TypeError, test)

    def test_no_parametric_abstract_instantiation(self):
        def test():
            self.A[2, float](1, 2)
        self.assertRaises(TypeError, test)

    def test_correct_metatypes(self):
        self.assertEqual(type(self.A), ParametricMeta)
        self.assertEqual(type(self.B), ParametricMeta)
        self.assertEqual(type(self.B[2, float]), ParametricMeta)
        
    def test_concrete_params(self):
        self.assertEqual(self.B[2, float].__parameters__, (2, float))
        self.assertEqual(self.A[2, float].__parameters__, (2, float))

    def test_partial_params(self):
        self.assertEqual(self.B[2].__parameters__, (2, type))
        self.assertEqual(self.B[2, None], self.B[2])
        self.assertEqual(self.B[2, ...], self.B[2])

    def test_abstract_from_origin(self):
        self.assertEqual(self.B[2].__abstract__, True)
        self.assertEqual(self.B[2, None].__abstract__, True)
        
    def test_abstract_ellipsis(self):
        self.assertEqual(self.B[2, ...].__abstract__, True)
        self.assertEqual(self.B[..., float].__abstract__, True)
        
    def test_concrete_subclass_is_concrete(self):
        class B2(self.B[2, float]):
            pass
        self.assertEqual(B2.__concrete__, True)
        self.assertEqual(B2.__subtypes__, None)


if __name__ == '__main__':
    unittest.main()