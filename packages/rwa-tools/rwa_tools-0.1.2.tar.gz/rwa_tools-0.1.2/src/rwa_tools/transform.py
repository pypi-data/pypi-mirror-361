from dataclasses import dataclass
from typing import Sequence

import sympy as smp

from .hamiltonian_symbolic import HamiltonianSymbolic, subtract_common_diag_symbols


@dataclass
class HamiltonianRWA:
    """Representation of a quantum Hamiltonian in the rotating wave approximation (RWA) frame.

    This class stores the components of a quantum Hamiltonian after applying
    the rotating wave approximation transformation, which eliminates
    rapidly oscillating terms and simplifies the dynamics.

    Attributes:
        nstates: Number of energy states in the system.
        hamiltonian: Matrix representing the Hamiltonian in the RWA frame.
        coupling_symbols: Symbolic variables representing field frequencies (ω0, ω1, etc.).
        detuning_symbols: Symbolic variables representing frequency detunings (Δ0, Δ1, etc.).
        rabi_symbols: Symbolic variables representing Rabi frequencies (Ω0, Ω1, etc.).
        energy_symbols: Symbolic variables representing energy levels (E0, E1, etc.).
        coupling_identifiers: List of lists of coupling identifiers (a0, a1, etc. for each coupling).
    """

    nstates: int
    hamiltonian: smp.Matrix
    detuning_symbols: Sequence[smp.Symbol]
    rabi_symbols: Sequence[smp.Symbol]
    energy_symbols: Sequence[smp.Symbol]
    coupling_identifiers: list[list[smp.Symbol]]


def create_hamiltonian_rwa(
    hamiltonian: HamiltonianSymbolic, transform: smp.Matrix
) -> HamiltonianRWA:
    """Generate a Hamiltonian in the rotating wave approximation (RWA) frame.

    This function applies a unitary transformation to convert a time-dependent
    Hamiltonian into the rotating frame, where the RWA can be applied. The
    transformation eliminates rapidly oscillating terms, simplifying the system
    dynamics while preserving the essential physics.

    The transformed Hamiltonian is calculated using:
    H_RWA = U†HU - iℏU†(∂U/∂t)

    Where U is the unitary transformation matrix and H is the original Hamiltonian.

    Args:
        hamiltonian: An instance of HamiltonianSymbolic containing the quantum
            system's symbolic representation in the lab frame.
        transform: A unitary transformation matrix (typically diagonal with
            time-dependent exponential elements) that defines the rotating frame.

    Returns:
        An instance of HamiltonianRWA with the Hamiltonian in the rotating frame
        and associated symbolic parameters.

    Raises:
        AttributeError: If required attributes are missing from the hamiltonian object.
        ValueError: If dimensions of transform matrix don't match the Hamiltonian.
    """
    # Input validation
    if transform.rows != hamiltonian.nstates or transform.cols != hamiltonian.nstates:
        raise ValueError(
            f"Transform matrix dimensions ({transform.rows}x{transform.cols}) "
            f"don't match Hamiltonian dimensions ({hamiltonian.nstates}x{hamiltonian.nstates})"
        )

    # Define time symbol for differentiation
    t = smp.Symbol("t", real=True)

    # Calculate the transformed Hamiltonian using the unitary transformation formula:
    # H_RWA = U†HU - iℏU†(∂U/∂t)
    try:
        # First part: U†HU (similarity transformation)
        similarity_term = transform.adjoint() @ hamiltonian.total @ transform

        # Second part: -iℏU†(∂U/∂t) (time-derivative correction)
        # Note: ℏ=1 in natural units
        derivative_term = smp.I * transform.adjoint() @ smp.diff(transform, t)

        # Complete RWA Hamiltonian
        hamiltonian_rwa = similarity_term - derivative_term

        # Apply frequency substitutions
        if (
            hasattr(hamiltonian, "omega_substitutions")
            and hamiltonian.omega_substitutions
        ):
            hamiltonian_rwa = hamiltonian_rwa.subs(hamiltonian.omega_substitutions)

        # Multi-step simplification process
        try:
            hamiltonian_rwa = subtract_common_diag_symbols(hamiltonian_rwa)
            # First expand to separate terms
            hamiltonian_rwa = hamiltonian_rwa.expand()
            # Then collect terms with time dependence
            hamiltonian_rwa.applyfunc(lambda x: x.collect(t))
            # Finally apply general simplification
            hamiltonian_rwa.simplify()
        except Exception as e:
            # Log but continue if simplification fails
            print(f"Warning: Matrix simplification partially failed: {e}")

    except Exception as e:
        raise RuntimeError(f"Failed to calculate RWA Hamiltonian: {e}") from e

    # Create and return the RWA Hamiltonian object
    return HamiltonianRWA(
        nstates=hamiltonian.nstates,
        hamiltonian=hamiltonian_rwa,
        detuning_symbols=hamiltonian.detuning_symbols,
        rabi_symbols=hamiltonian.rabi_symbols,
        energy_symbols=hamiltonian.energy_symbols,
        coupling_identifiers=hamiltonian.coupling_identifiers,
    )
