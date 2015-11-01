from generic import generic
import unittest
import psutil

class BasePyGenericTestCase(unittest.TestCase):
    def setUp(self):
        @generic
        def add(x, y):
            return x + y
        
        @add.overload
        def add(x: int, y: int):
            return x + y + 1
        
        @add.overload
        def add(x: float, y: float):
            return x + y + 1.5
    
        self.add = add
        self.process = psutil.Process()
        
    def test_memory_leaks(self):
        mem0 = self.process.memory_info()
        add = self.add
        
        # Hammer CPU
        for _ in range(1000000):
            add(1, 2)
            add(1.0, 2.0)
            add(1, 2.0)
            
        mem1 = self.process.memory_info()
        self.assertEqual(mem0, mem1)
            
    
if __name__ == '__main__':
    unittest.main()