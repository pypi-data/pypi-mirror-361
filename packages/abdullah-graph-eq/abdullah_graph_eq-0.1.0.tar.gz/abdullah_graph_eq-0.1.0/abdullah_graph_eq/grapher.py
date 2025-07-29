"""
Graph plotting module for mathematical equations.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, Optional, Union
from .parser import EquationParser


class EquationGrapher:
    """Grapher for mathematical equations."""
    
    def __init__(self):
        self.parser = EquationParser()
    
    def plot(self, 
             equation_str: str, 
             x_range: Tuple[float, float] = (-10, 10),
             num_points: int = 1000,
             title: Optional[str] = None,
             xlabel: str = "x",
             ylabel: str = "y",
             grid: bool = True,
             figsize: Tuple[float, float] = (10, 6),
             save_path: Optional[str] = None,
             show: bool = True) -> plt.Figure:
        """
        Plot a mathematical equation.
        
        Args:
            equation_str (str): The equation as a string
            x_range (Tuple[float, float]): Range of x values (min, max)
            num_points (int): Number of points to plot
            title (Optional[str]): Plot title
            xlabel (str): X-axis label
            ylabel (str): Y-axis label
            grid (bool): Whether to show grid
            figsize (Tuple[float, float]): Figure size (width, height)
            save_path (Optional[str]): Path to save the plot
            show (bool): Whether to display the plot
            
        Returns:
            plt.Figure: The matplotlib figure object
        """
        try:
            # Parse the equation
            expr = self.parser.parse(equation_str)
            
            # Convert to numpy function
            func = self.parser.to_numpy_function(expr)
            
            # Generate x values
            x = np.linspace(x_range[0], x_range[1], num_points)
            
            # Calculate y values
            y = func(x)
            
            # Create the plot
            fig, ax = plt.subplots(figsize=figsize)
            ax.plot(x, y, 'b-', linewidth=2, label=f'y = {equation_str}')
            
            # Customize the plot
            if title is None:
                title = f'Graph of y = {equation_str}'
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            
            if grid:
                ax.grid(True, alpha=0.3)
            
            # Add axes through origin
            ax.axhline(y=0, color='k', linewidth=0.5)
            ax.axvline(x=0, color='k', linewidth=0.5)
            
            # Add legend
            ax.legend(fontsize=10)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save if requested
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Plot saved to: {save_path}")
            
            # Show if requested
            if show:
                plt.show()
            
            return fig
            
        except Exception as e:
            raise RuntimeError(f"Error plotting equation '{equation_str}': {str(e)}")
    
    def plot_multiple(self,
                     equations: list,
                     x_range: Tuple[float, float] = (-10, 10),
                     num_points: int = 1000,
                     title: Optional[str] = None,
                     xlabel: str = "x",
                     ylabel: str = "y",
                     grid: bool = True,
                     figsize: Tuple[float, float] = (10, 6),
                     save_path: Optional[str] = None,
                     show: bool = True) -> plt.Figure:
        """
        Plot multiple equations on the same graph.
        
        Args:
            equations (list): List of equation strings
            x_range (Tuple[float, float]): Range of x values (min, max)
            num_points (int): Number of points to plot
            title (Optional[str]): Plot title
            xlabel (str): X-axis label
            ylabel (str): Y-axis label
            grid (bool): Whether to show grid
            figsize (Tuple[float, float]): Figure size (width, height)
            save_path (Optional[str]): Path to save the plot
            show (bool): Whether to display the plot
            
        Returns:
            plt.Figure: The matplotlib figure object
        """
        try:
            # Generate x values
            x = np.linspace(x_range[0], x_range[1], num_points)
            
            # Create the plot
            fig, ax = plt.subplots(figsize=figsize)
            
            colors = plt.cm.tab10(np.linspace(0, 1, len(equations)))
            
            for i, equation_str in enumerate(equations):
                # Parse and plot each equation
                expr = self.parser.parse(equation_str)
                func = self.parser.to_numpy_function(expr)
                y = func(x)
                
                ax.plot(x, y, color=colors[i], linewidth=2, 
                       label=f'y = {equation_str}')
            
            # Customize the plot
            if title is None:
                title = 'Multiple Equations'
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            
            if grid:
                ax.grid(True, alpha=0.3)
            
            # Add axes through origin
            ax.axhline(y=0, color='k', linewidth=0.5)
            ax.axvline(x=0, color='k', linewidth=0.5)
            
            # Add legend
            ax.legend(fontsize=10)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save if requested
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Plot saved to: {save_path}")
            
            # Show if requested
            if show:
                plt.show()
            
            return fig
            
        except Exception as e:
            raise RuntimeError(f"Error plotting multiple equations: {str(e)}")


def graph_equation(equation_str: str, 
                  x_range: Tuple[float, float] = (-10, 10),
                  num_points: int = 1000,
                  title: Optional[str] = None,
                  save_path: Optional[str] = None,
                  show: bool = True) -> plt.Figure:
    """
    Convenience function to graph a single equation.
    
    Args:
        equation_str (str): The equation as a string
        x_range (Tuple[float, float]): Range of x values (min, max)
        num_points (int): Number of points to plot
        title (Optional[str]): Plot title
        save_path (Optional[str]): Path to save the plot
        show (bool): Whether to display the plot
        
    Returns:
        plt.Figure: The matplotlib figure object
    """
    grapher = EquationGrapher()
    return grapher.plot(equation_str, x_range, num_points, title, 
                       save_path=save_path, show=show)
