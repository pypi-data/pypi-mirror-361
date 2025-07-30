import unittest
from objxp import ox

class TestClass:
    """A test class for demonstrating ox functionality"""
    
    def __init__(self):
        self.x = 1
        self.y = "test"
        self._private = "hidden"
        self.__very_private = "very hidden"
    
    def method(self):
        """A test method"""
        pass
    
    def _private_method(self):
        pass
    
    def __very_private_method(self):
        pass
    
    @property
    def prop(self):
        return self.x
    
    def __str__(self):
        return f"TestClass(x={self.x}, y={self.y})"

class TestOx(unittest.TestCase):
    def setUp(self):
        self.test_obj = TestClass()
    
    def test_basic_output(self):
        """测试基本输出功能"""
        result = ox(self.test_obj, ifprint=False)
        self.assertIsInstance(result, str)
        self.assertIn("TestClass", result)
    
    def test_show_inner_members_none(self):
        """测试不显示内部成员"""
        result = ox(self.test_obj, ifprint=False, show_inner_members='none')
        self.assertNotIn("_private", result)
        self.assertNotIn("__very_private", result)
    
    def test_show_inner_members_single(self):
        """测试显示单下划线成员"""
        result = ox(self.test_obj, ifprint=False, show_inner_members='_')
        self.assertIn("_private", result)
        # Python名称修饰会将__very_private转换为_TestClass__very_private
        self.assertNotIn("_TestClass__very_private", result)
    
    def test_show_inner_members_double(self):
        """测试显示双下划线成员"""
        result = ox(self.test_obj, ifprint=False, show_inner_members='__')
        self.assertNotIn("_private", result)
        # Python名称修饰会将__very_private转换为_TestClass__very_private
        self.assertIn("_TestClass__very_private", result)
    
    def test_show_inner_members_both(self):
        """测试显示所有内部成员"""
        result = ox(self.test_obj, ifprint=False, show_inner_members='both')
        self.assertIn("_private", result)
        self.assertIn("__very_private", result)
    
    def test_special_methods(self):
        """测试特殊方法的分类"""
        result = ox(self.test_obj, ifprint=False, show_inner_members='both')
        self.assertIn("__str__", result)
        self.assertIn("__init__", result)
    
    def test_property(self):
        """测试属性的分类"""
        result = ox(self.test_obj, ifprint=False)
        self.assertIn("prop", result)
        self.assertIn("property", result.lower())

if __name__ == '__main__':
    unittest.main()