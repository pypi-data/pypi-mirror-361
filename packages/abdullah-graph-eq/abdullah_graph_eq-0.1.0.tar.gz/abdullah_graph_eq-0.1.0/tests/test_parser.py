"""
Tests for the parser module.
"""

import unittest
import sympy as sp
from abdullah_graph_eq.parser import EquationParser, parse_equation


class TestEquationParser(unittest.TestCase):
    """Test cases for EquationParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = EquationParser()
    
    def test_simple_polynomial(self):
        """Test parsing simple polynomial equations."""
        expr = self.parser.parse("x**2 + 2*x + 1")
        self.assertIsInstance(expr, sp.Expr)
        
        # Test evaluation
        func = self.parser.to_numpy_function(expr)
        result = func(1)
        self.assertEqual(result, 4)  # 1 + 2 + 1 = 4
    
    def test_trigonometric_functions(self):
        """Test parsing trigonometric functions."""
        expr = self.parser.parse("sin(x)")
        self.assertIsInstance(expr, sp.Expr)
        
        expr = self.parser.parse("cos(x) + sin(2*x)")
        self.assertIsInstance(expr, sp.Expr)
    
    def test_exponential_functions(self):
        """Test parsing exponential and logarithmic functions."""
        expr = self.parser.parse("exp(x)")
        self.assertIsInstance(expr, sp.Expr)
        
        expr = self.parser.parse("log(x)")
        self.assertIsInstance(expr, sp.Expr)
    
    def test_complex_expression(self):
        """Test parsing complex mathematical expressions."""
        expr = self.parser.parse("exp(-x**2) * sin(3*x) + cos(x/2)")
        self.assertIsInstance(expr, sp.Expr)
    
    def test_invalid_expression(self):
        """Test handling of invalid expressions."""
        with self.assertRaises(ValueError):
            self.parser.parse("invalid_function(x)")
    
    def test_convenience_function(self):
        """Test the convenience parse_equation function."""
        expr = parse_equation("x**2 + 1")
        self.assertIsInstance(expr, sp.Expr)


if __name__ == '__main__':
    unittest.main()
