# Grey Wolf Optimizer

A high-performance Python implementation of the Grey Wolf Optimizer (GWO) algorithm with modern features and easy-to-use interface.

## Overview

The Grey Wolf Optimizer is a nature-inspired metaheuristic optimization algorithm that mimics the leadership hierarchy and hunting mechanism of grey wolves in nature. This implementation features:

- **Simple Interface**: Easy `.fit()` method for optimization
- **Optional MPI Parallelization**: Distributed fitness evaluation across multiple processes
- **Flexible Configuration**: Support for different bounds, population sizes, and verbosity levels
- **Clean Architecture**: Well-documented, PEP 8 compliant code with full type hints
- **Performance Optimized**: Efficient numpy operations and memory management

## Quick Start

```python
import numpy as np
from gwo import GreyWolfOptimizer

# Define your objective function to minimize
def objective_function(x):
    return np.sum(x ** 2)  # Sphere function

# Create and run optimizer
optimizer = GreyWolfOptimizer(n_wolves=30, max_iter=200, verbose=1)
result = optimizer.fit(objective_function, dimensions=10)

print(f"Best solution: {result.x}")
print(f"Best fitness: {result.fun}")
```

## Installation

### Basic Installation
```bash
pip install numpy>=1.21.0
```

### With MPI Support (Optional)
```bash
pip install numpy>=1.21.0 mpi4py>=3.1.0
```

## Algorithm Details

The GWO algorithm maintains a social hierarchy among wolves:
- **Alpha (α)**: Best solution found (pack leader)
- **Beta (β)**: Second best solution (subordinate)
- **Delta (δ)**: Third best solution (subordinate)
- **Omega (ω)**: Remaining solutions (followers)

Each iteration involves:
1. Evaluating fitness of all wolves (optionally parallelized across MPI processes)
2. Updating the three pack leaders based on fitness
3. Updating positions of all wolves based on leaders' guidance
4. Applying boundary constraints to keep wolves within search space

## Configuration Options

### Basic Parameters
```python
optimizer = GreyWolfOptimizer(
    n_wolves=30,          # Population size (20-100 recommended)
    max_iter=500,         # Maximum iterations
    bounds=(-10, 10),     # Search bounds for all dimensions
    random_state=42,      # For reproducible results
    verbose=1             # 0=silent, 1=basic, 2=detailed
)
```

### Custom Bounds Per Dimension
```python
# Different bounds for each dimension
bounds = np.array([
    [-5, 5],     # Dimension 1: [-5, 5]
    [-10, 10],   # Dimension 2: [-10, 10]
    [-1, 1],     # Dimension 3: [-1, 1]
])
optimizer = GreyWolfOptimizer(bounds=bounds)
```

### MPI Parallelization
```python
# Enable MPI support (requires mpi4py)
optimizer = GreyWolfOptimizer(n_wolves=100, use_mpi=True)

# Run with multiple processes:
# mpiexec -n 4 python your_script.py
```

## Verbosity Levels

- **0**: Silent mode (no output)
- **1**: Basic progress (every 50 iterations + summary)
- **2**: Detailed progress (every iteration + leader info)

## Example: Different Test Functions

```python
# Sphere function (unimodal)
def sphere(x):
    return np.sum(x ** 2)

# Rastrigin function (multimodal)
def rastrigin(x):
    A = 10
    n = len(x)
    return A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x))

# Run optimization
optimizer = GreyWolfOptimizer(n_wolves=50, max_iter=300, verbose=1)
result = optimizer.fit(rastrigin, dimensions=5)
```

## Performance Tips

- **Population Size**: 20-30 for small problems, 50-100 for complex ones
- **Iterations**: 100-200 for quick runs, 500+ for thorough optimization
- **MPI**: Use when population > 50 and you have multiple cores
- **Bounds**: Tight bounds improve convergence speed

## Running Examples

```bash
# Basic example
python gwo.py

# Full demo with multiple functions
python gwo.py --demo

# With MPI (if installed)
mpiexec -n 4 python gwo.py
```

## API Reference

**Main Methods:**
- `fit(objective_function, dimensions)`: Run optimization
- `get_params()` / `set_params()`: Parameter management

**Result Object:**
- `result.x`: Best solution found
- `result.fun`: Best fitness value
- `result.nit`: Number of iterations
- `result.nfev`: Function evaluations
- `result.success`: Success flag

## License

This implementation is provided for educational and research purposes.
