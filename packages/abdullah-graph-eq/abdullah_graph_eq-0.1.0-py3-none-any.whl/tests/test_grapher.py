"""
Tests for the grapher module.
"""

import unittest
import matplotlib.pyplot as plt
import tempfile
import os
from abdullah_graph_eq.grapher import EquationGrapher, graph_equation


class TestEquationGrapher(unittest.TestCase):
    """Test cases for EquationGrapher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.grapher = EquationGrapher()
        plt.ioff()  # Turn off interactive mode for testing
    
    def tearDown(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_simple_plot(self):
        """Test plotting a simple equation."""
        fig = self.grapher.plot("x**2", show=False)
        self.assertIsInstance(fig, plt.Figure)
    
    def test_trigonometric_plot(self):
        """Test plotting trigonometric functions."""
        fig = self.grapher.plot("sin(x)", show=False)
        self.assertIsInstance(fig, plt.Figure)
    
    def test_custom_range(self):
        """Test plotting with custom x range."""
        fig = self.grapher.plot("x**2", x_range=(-5, 5), show=False)
        self.assertIsInstance(fig, plt.Figure)
    
    def test_save_plot(self):
        """Test saving plot to file."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            fig = self.grapher.plot("x**2", save_path=tmp_path, show=False)
            self.assertTrue(os.path.exists(tmp_path))
            self.assertIsInstance(fig, plt.Figure)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_multiple_equations(self):
        """Test plotting multiple equations."""
        equations = ["x**2", "x**3", "sin(x)"]
        fig = self.grapher.plot_multiple(equations, show=False)
        self.assertIsInstance(fig, plt.Figure)
    
    def test_convenience_function(self):
        """Test the convenience graph_equation function."""
        fig = graph_equation("x**2 + 1", show=False)
        self.assertIsInstance(fig, plt.Figure)
    
    def test_invalid_equation(self):
        """Test handling of invalid equations."""
        with self.assertRaises(RuntimeError):
            self.grapher.plot("invalid_function(x)", show=False)


if __name__ == '__main__':
    unittest.main()
