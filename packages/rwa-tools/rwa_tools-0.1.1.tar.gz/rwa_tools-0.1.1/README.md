# RWA-Tools

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rwa-tools)](https://pypi.python.org/pypi/rwa-tools/)
[![PyPI - Package Version](https://img.shields.io/pypi/v/rwa-tools)](https://pypi.python.org/pypi/rwa-tools/)

A Python package for working with quantum Hamiltonians in the Rotating Wave Approximation (RWA) frame.

## Overview

RWA-Tools provides a set of utilities for symbolic manipulation of quantum Hamiltonians, particularly focusing on applying the Rotating Wave Approximation to simplify time-dependent quantum systems. This package leverages SymPy for symbolic mathematics to represent and transform Hamiltonians.

## Installation

```bash
pip install rwa-tools
```

For development installation:

```bash
git clone https://github.com/ograsdijk/rwa-tools.git
cd rwa-tools
pip install -e .
```

## Features

- Symbolic representation of quantum Hamiltonians
- Application of the Rotating Wave Approximation (RWA)
- Unitary transformations to rotating frames
- Handling of multi-level quantum systems
- Simplification of time-dependent Hamiltonians

## Usage Examples

### Creating a Symbolic Hamiltonian

```python
import matplotlib.pyplot as plt
import networkx as nx
import sympy as smp

from rwa_tools import (
    create_coupling_graph,
    create_hamiltonian_symbolic,
    create_hamiltonian_rwa,
)
from rwa_tools.graph_transform import create_transform_matrix

# Define your quantum system
nstates = 5
couplings = [[(0, 4), (1, 4)], [(2, 4), (3, 4)], [(1, 3)], [(0, 4), (1, 4)]]

# Create the Hamiltonian and coupling graph
hamiltonian = create_hamiltonian_symbolic(couplings, nstates)
coupling_graph = create_coupling_graph(couplings, nstates=nstates)

# Visualize the coupling graph
fig, ax = plt.subplots()
nx.draw(coupling_graph)
```

### Applying RWA Transformation

```python
from rwa_tools import (
    create_coupling_graph,
    create_hamiltonian_symbolic,
    create_hamiltonian_rwa,
)
from rwa_tools.graph_transform import create_transform_matrix

# Define your quantum system
nstates = 5
couplings = [[(0, 4), (1, 4)], [(2, 4), (3, 4)], [(1, 3)], [(0, 4), (1, 4)]]
hamiltonian = create_hamiltonian_symbolic(couplings, nstates)
coupling_graph = create_coupling_graph(couplings, nstates=nstates)

# Create transformation matrix from coupling graph
T = create_transform_matrix(coupling_graph, hamiltonian.coupling_symbol_paths)

# Apply RWA transformation
hamiltonian_rwa = create_hamiltonian_rwa(hamiltonian, T)

# Print the resulting RWA Hamiltonian
print(hamiltonian_rwa.hamiltonian)
```

### Working with Independent Subsystems

```python
from rwa_tools import (
    create_coupling_graph,
    split_into_independent_components,
    create_hamiltonian_symbolic,
    split_hamiltonian_by_components,
)

# Define a system with independent components
nstates = 7
couplings = [[(0, 2), (1, 2)], [(3, 5), (4, 5)]]
hamiltonian = create_hamiltonian_symbolic(couplings, nstates)
coupling_graph = create_coupling_graph(couplings, nstates=nstates)

# Split into independent components
independent_graphs = split_into_independent_components(coupling_graph)

# Split the Hamiltonian by components
independent_hamiltonians = split_hamiltonian_by_components(
    hamiltonian, independent_graphs
)

# Access individual subsystem Hamiltonians
print(independent_hamiltonians[0].total)
print(independent_hamiltonians[1].total)
```

## API Documentation

### Core Classes

- **HamiltonianSymbolic**: Represents a symbolic quantum Hamiltonian in the lab frame
- **HamiltonianRWA**: Represents a quantum Hamiltonian in the rotating wave approximation frame

### Key Functions

- **create_hamiltonian_symbolic**: Create a symbolic representation of a quantum Hamiltonian
- **create_coupling_graph**: Create a graph representing couplings between quantum states
- **create_hamiltonian_rwa**: Generate a Hamiltonian in the RWA frame from a lab-frame Hamiltonian and unitary transformation
- **create_transform_matrix**: Create a transformation matrix based on the coupling graph
- **split_into_independent_components**: Split a graph into independent connected components
- **split_hamiltonian_by_components**: Split a Hamiltonian into independent subsystems

## Mathematical Background

The Rotating Wave Approximation is a technique used in quantum optics and quantum mechanics to simplify the treatment of time-dependent systems. The transformed Hamiltonian is calculated using:

$H_{RWA} = U^{\dagger}HU - i\hbar U^{\dagger}(\partial U/\partial t)$

Where $U$ is the unitary transformation matrix and $H$ is the original Hamiltonian.


## License

This project is licensed under the MIT License - see the LICENSE file for details.
