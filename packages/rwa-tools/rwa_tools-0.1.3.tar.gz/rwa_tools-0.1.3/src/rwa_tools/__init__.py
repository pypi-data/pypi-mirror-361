"""Rotating Wave Approximation Tools for Quantum Systems.

This package provides tools for applying the rotating wave approximation (RWA)
to multi-level quantum systems driven by one or more external fields. It enables
symbolic representation, manipulation, and transformation of quantum Hamiltonians
to simplify their analysis and numerical implementation.

The package offers:
- Creation of symbolic Hamiltonians with arbitrary energy levels and couplings
- Graph-based representation of quantum state couplings
- Transformation into rotating frames to apply the RWA
- Utilities for simplifying and manipulating the resulting Hamiltonians

Core functionality is exposed at the package level for convenient import.

Example:
    A simple three-level system with two driving fields can be created with:

    >>> from rwa_tools import create_hamiltonian_symbolic, create_coupling_graph, create_hamiltonian_rwa
    >>> nstates = 3
    >>> couplings = [[(0, 1)], [(1, 2)]]  # Two fields coupling adjacent states
    >>> hamiltonian = create_hamiltonian_symbolic(couplings, nstates)
    >>> coupling_graph = create_coupling_graph(couplings, nstates)
    >>> from rwa_tools.graph_transform import create_transform_matrix
    >>> transform = create_transform_matrix(coupling_graph)
    >>> hamiltonian_rwa = create_hamiltonian_rwa(hamiltonian, transform)
"""

__version__ = "0.1.0"  # Add proper version

from . import graph_transform, hamiltonian_symbolic, transform

# Explicit imports from modules to make them available at package level
from .graph_transform import (
    create_coupling_graph,
    create_transform_matrix,
    split_into_independent_components,
)
from .hamiltonian_symbolic import (
    create_hamiltonian_symbolic,
    split_hamiltonian_by_components,
)
from .transform import create_hamiltonian_rwa

# Define public API
__all__: list[str] = [
    "create_coupling_graph",
    "split_into_independent_components",
    "create_hamiltonian_symbolic",
    "split_hamiltonian_by_components",
    "create_hamiltonian_rwa",
    "graph_transform",
    "hamiltonian_symbolic",
    "transform",
    "create_transform_matrix",
]
