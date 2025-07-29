"""
Equation parser module for converting string equations to mathematical expressions.
"""

import sympy as sp
import numpy as np
from typing import Optional, Callable


class EquationParser:
    """Parser for mathematical equations from string input."""
    
    def __init__(self):
        self.x = sp.Symbol('x')
        self.allowed_functions = {
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'asin': sp.asin,
            'acos': sp.acos,
            'atan': sp.atan,
            'exp': sp.exp,
            'log': sp.log,
            'ln': sp.log,
            'log10': lambda x: sp.log(x, 10),
            'sqrt': sp.sqrt,
            'abs': sp.Abs,
            'pi': sp.pi,
            'e': sp.E,
        }
    
    def parse(self, equation_str: str) -> sp.Expr:
        """
        Parse a string equation into a SymPy expression.
        
        Args:
            equation_str (str): The equation as a string (e.g., "x**2 + 2*x + 1")
            
        Returns:
            sp.Expr: SymPy expression object
            
        Raises:
            ValueError: If the equation cannot be parsed
        """
        try:
            # Replace common mathematical notation
            equation_str = equation_str.replace('^', '**')  # Power notation
            equation_str = equation_str.replace('ln(', 'log(')  # Natural log
            
            # Create local namespace with allowed functions and symbols
            local_namespace = {
                'x': self.x,
                **self.allowed_functions
            }
            
            # Parse the expression
            expr = sp.sympify(equation_str, locals=local_namespace)
            
            # Check for undefined functions (functions not in our allowed list)
            self._validate_expression(expr, equation_str)
            
            return expr
            
        except Exception as e:
            raise ValueError(f"Could not parse equation '{equation_str}': {str(e)}")
    
    def _validate_expression(self, expr: sp.Expr, equation_str: str):
        """
        Validate that the expression only contains allowed functions.
        
        Args:
            expr (sp.Expr): The parsed expression
            equation_str (str): Original equation string for error reporting
            
        Raises:
            ValueError: If expression contains undefined functions
        """
        # Get all functions used in the expression
        functions_in_expr = expr.atoms(sp.Function)
        
        for func in functions_in_expr:
            func_name = str(func.func)
            if func_name not in self.allowed_functions:
                raise ValueError(f"Undefined function '{func_name}' in equation '{equation_str}'")
    
    def to_numpy_function(self, expr: sp.Expr) -> Callable[[np.ndarray], np.ndarray]:
        """
        Convert SymPy expression to numpy function for plotting.
        
        Args:
            expr (sp.Expr): SymPy expression
            
        Returns:
            Callable: Function that takes numpy array and returns numpy array
        """
        return sp.lambdify(self.x, expr, 'numpy')


def parse_equation(equation_str: str) -> sp.Expr:
    """
    Convenience function to parse an equation string.
    
    Args:
        equation_str (str): The equation as a string
        
    Returns:
        sp.Expr: SymPy expression object
    """
    parser = EquationParser()
    return parser.parse(equation_str)
