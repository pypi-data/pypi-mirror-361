# Abdullah Graph Equation

A Python package for graphing mathematical equations from string input.

## Installation

```bash
pip install abdullah_graph_eq
```

## Usage

```python
from abdullah_graph_eq import graph_equation

# Graph a simple quadratic equation
graph_equation("x**2 + 2*x + 1")

# Graph a trigonometric function
graph_equation("sin(x)")

# Graph with custom range
graph_equation("x**3 - 2*x**2 + x - 1", x_range=(-5, 5))

# Save the plot
graph_equation("cos(x) + sin(2*x)", save_path="my_graph.png")
```

## Features

- Parse mathematical equations from strings
- Support for common mathematical functions (sin, cos, tan, log, exp, etc.)
- Customizable plotting range
- Save plots to files
- Support for multiple equation formats

## Supported Functions

- Basic arithmetic: `+`, `-`, `*`, `/`, `**` (power)
- Trigonometric: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`
- Exponential/Logarithmic: `exp`, `log`, `ln`, `log10`
- Other: `sqrt`, `abs`

## Examples

### Linear Function

```python
graph_equation("2*x + 3")
```

### Quadratic Function

```python
graph_equation("x**2 - 4*x + 3")
```

### Trigonometric Function

```python
graph_equation("sin(x) + cos(2*x)")
```

### Complex Function

```python
graph_equation("exp(-x**2) * sin(5*x)")
```

## Requirements

- Python 3.7+
- matplotlib
- numpy
- sympy

## License

MIT License
