"""RWA Tools - Rotating Wave Approximation Tools for Quantum Systems."""

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
