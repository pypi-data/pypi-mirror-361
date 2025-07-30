from dataclasses import dataclass
from typing import Sequence

import networkx as nx
import sympy as smp


@dataclass
class HamiltonianSymbolic:
    """Symbolic representation of a quantum Hamiltonian.

    This class stores the components of a quantum Hamiltonian in symbolic form,
    including energy levels, coupling terms, and their relationships.

    Attributes:
        nstates: Number of energy states in the system.
        hamiltonian: Diagonal matrix representing the unperturbed energy levels.
        coupling_matrix: Off-diagonal matrix representing field interactions.
        total: Complete Hamiltonian (hamiltonian + coupling_matrix).
        coupling_phase: Matrix storing the phase factors for each coupling.
        couplings: List of state pairs coupled by each driving field.
        energy_symbols: Symbolic variables representing energy levels (E0, E1, etc.).
        coupling_symbols: Symbolic variables representing field frequencies (ω0, ω1, etc.).
        rabi_symbols: Symbolic variables representing Rabi frequencies (Ω0, Ω1, etc.).
        omega_energy: Dictionary mapping field frequencies to corresponding energy differences.
    """

    nstates: int
    hamiltonian: smp.Matrix
    coupling_matrix: smp.Matrix
    total: smp.Matrix
    coupling_symbol_paths: dict[tuple[int, int], list[smp.Symbol]]
    couplings: Sequence[Sequence[tuple[int, int]]]
    energy_symbols: Sequence[smp.Symbol]
    coupling_symbols: Sequence[smp.Symbol]
    detuning_symbols: Sequence[smp.Symbol]
    rabi_symbols: Sequence[smp.Symbol]
    omega_substitutions: dict[smp.Symbol, smp.Symbol]


def create_hamiltonian_symbolic(
    couplings: Sequence[Sequence[tuple[int, int]]], nstates: int
) -> HamiltonianSymbolic:
    """Generates a symbolic representation of a quantum Hamiltonian.

    This function constructs the time-dependent Hamiltonian for a multi-level
    quantum system driven by one or more external fields. The Hamiltonian is
    represented using the `sympy` library for symbolic mathematics.

    The total Hamiltonian is H = H_0 + V(t), where:
    - H_0 is the diagonal matrix of unperturbed energy levels (E0, E1, ...).
    - V(t) is the coupling matrix representing the interaction with external
      fields. Each field is assumed to have an exponential time dependence,
      V(t) = Ω * exp(iωt)/2 + h.c.

    Args:
        couplings: A sequence of driving field configurations. Each element is
            a sequence of (state1, state2) tuples that are coupled by a
            common field. For example, `[[(0, 1)], [(1, 2)]]` defines two
            separate fields, one coupling states 0 and 1, and another
            coupling states 1 and 2.
        nstates: The total number of energy states in the system.

    Returns:
        A `HamiltonianSymbolic` object containing:
        - The diagonal energy matrix (hamiltonian)
        - The off-diagonal coupling matrix (coupling_matrix)
        - The total Hamiltonian (total)
        - A matrix of coupling phase factors (coupling_phase)
        - The coupling configuration (couplings)
        - Symbolic representations of energies, frequencies, and couplings
        - A mapping between driving frequencies and energy differences (omega_energy)
    """
    # Validate inputs
    if nstates <= 0:
        raise ValueError("Number of states must be positive")
    if not couplings:
        raise ValueError("At least one coupling must be provided")

    # Create symbolic parameters
    energy_symbols = smp.symbols(f"E0:{nstates}", real=True)
    coupling_symbols = smp.symbols(f"ω0:{len(couplings)}", real=True)
    detuning_symbols = smp.symbols(f"δ0:{len(couplings)}", real=True)
    rabi_symbols = smp.symbols(f"Ω0:{len(couplings)}", real=False)

    # Create the diagonal Hamiltonian matrix (H_0)
    hamiltonian = smp.diag(*energy_symbols)

    # Create the coupling matrix and phase dictionary
    coupling_matrix, coupling_phase, omega_substitutions = _create_coupling_matrix(
        nstates,
        couplings,
        energy_symbols,
        coupling_symbols,
        detuning_symbols,
        rabi_symbols,
    )

    # Create the complete Hamiltonian
    total_hamiltonian = hamiltonian + coupling_matrix

    return HamiltonianSymbolic(
        nstates=nstates,
        hamiltonian=hamiltonian,
        coupling_matrix=coupling_matrix,
        total=total_hamiltonian,
        coupling_symbol_paths=coupling_phase,
        couplings=couplings,
        energy_symbols=energy_symbols,
        coupling_symbols=coupling_symbols,
        detuning_symbols=detuning_symbols,
        rabi_symbols=rabi_symbols,
        omega_substitutions=omega_substitutions,
    )


def _create_coupling_matrix(
    nstates: int,
    couplings: Sequence[Sequence[tuple[int, int]]],
    energy_symbols: Sequence[smp.Symbol],
    coupling_symbols: Sequence[smp.Symbol],
    detuning_symbols: Sequence[smp.Symbol],
    rabi_symbols: Sequence[smp.Symbol],
) -> tuple[
    smp.Matrix, dict[tuple[int, int], list[smp.Symbol]], dict[smp.Symbol, smp.Symbol]
]:
    """Create the coupling matrix representing field interactions.

    Args:
        nstates: Number of energy states
        couplings: Sequence of coupling configurations
        energy_symbols: Symbolic energy level variables
        coupling_symbols: Symbolic coupling frequency variables
        detuning_symbols: Symbolic detuning frequency variables
        rabi_symbols: Symbolic Rabi frequency variables

    Returns:
        Tuple containing:
        - Coupling matrix
        - Dictionary mapping state pairs to coupling phases
        - Dictionary mapping coupling frequencies to energy differences
    """
    coupling_matrix = smp.zeros(nstates, nstates, complex=True)
    coupling_phase = dict()
    omega_substitutions = dict()

    t = smp.Symbol("t", real=True)  # Time variable

    for omega, detuning, rabi, coupling_group in zip(
        coupling_symbols, detuning_symbols, rabi_symbols, couplings
    ):
        for state1, state2 in coupling_group:
            # Store the relationship between frequency and energy difference
            if omega not in omega_substitutions:
                omega_substitutions[omega] = (
                    energy_symbols[state2] - energy_symbols[state1] + detuning
                )

            # Calculate the coupling term for the states
            coupling_term = rabi * smp.exp(smp.I * omega * t) / 2

            # Add coupling terms to the matrix
            coupling_matrix[state1, state2] += coupling_term
            coupling_matrix[state2, state1] += smp.conjugate(coupling_term)

            # Record the phase information
            if (state1, state2) not in coupling_phase:
                coupling_phase[(state1, state2)] = [omega]
            else:
                coupling_phase[(state1, state2)].append(omega)

    return coupling_matrix, coupling_phase, omega_substitutions


def common_diag_symbols(matrix: smp.Matrix) -> set:
    """Find symbols that are common to all diagonal elements of a matrix.

    This function extracts all diagonal elements from a symbolic matrix
    and identifies which symbolic variables appear in every diagonal element.

    Args:
        M (smp.Matrix): A symbolic matrix to analyze

    Returns:
        set: A set of symbolic variables common to all diagonal elements.
             Returns empty set if matrix has no rows or no common symbols exist.
    """
    # Extract all diagonal elements from the matrix
    diags = [matrix[i, i] for i in range(matrix.rows)]
    # If the matrix is empty, return an empty set
    if not diags:
        return set()
    # Find the intersection of free symbols across all diagonal elements
    return set.intersection(*(d.free_symbols for d in diags))


def subtract_common_diag_symbols(matrix: smp.Matrix) -> smp.Matrix:
    """Subtract common symbols from diagonal elements of a symbolic matrix.

    This function identifies symbolic variables that are common to all diagonal
    elements of the input matrix, then subtracts their sum from each diagonal
    element. This is useful for simplifying quantum Hamiltonians by removing
    constant energy shifts that don't affect the dynamics.

    Args:
        matrix: A sympy Matrix containing symbolic expressions on its diagonal.

    Returns:
        A new sympy Matrix with the sum of common symbols subtracted from each
        diagonal element. If no common symbols are found, returns a copy of the
        original matrix.
    """
    # Find the common symbols on the diagonal
    common = common_diag_symbols(matrix)
    if not common:
        # No common symbols found, return a copy of the original matrix
        return matrix.copy()

    # Sum up the common symbols into one expression to subtract
    to_subtract = sum(common)

    # Create a new matrix to preserve the original
    matrix_new = matrix.copy()
    # Subtract the common term from each diagonal element
    for i in range(matrix_new.rows):
        matrix_new[i, i] = matrix_new[i, i] - to_subtract

    return matrix_new


def split_hamiltonian_by_components(
    hamiltonian: HamiltonianSymbolic, components: list[nx.Graph]
) -> list[HamiltonianSymbolic]:
    """Split a HamiltonianSymbolic object based on independent graph components.

    When a quantum system contains independent subsystems (represented by disconnected
    components in the coupling graph), the Hamiltonian can be split into separate
    Hamiltonians for each subsystem. This function performs that splitting.

    Args:
        hamiltonian: The complete HamiltonianSymbolic object to split
        components: List of networkx graphs, each representing an independent component

    Returns:
        A list of HamiltonianSymbolic objects, one for each independent component
    """
    result_hamiltonians = []

    for component in components:
        # Get states (nodes) in this component
        states = sorted(component.nodes())
        nstates = len(states)

        # Create a mapping from original state indices to new state indices
        state_mapping = {old_idx: new_idx for new_idx, old_idx in enumerate(states)}
        reverse_mapping = {new_idx: old_idx for new_idx, old_idx in enumerate(states)}

        # Filter couplings that only involve states in this component
        filtered_couplings = []
        coupling_idx_map = {}  # Maps original coupling index to new coupling index

        for i, coupling_group in enumerate(hamiltonian.couplings):
            new_group = []
            for state1, state2 in coupling_group:
                if state1 in states and state2 in states:
                    # Map old state indices to new ones
                    new_state1 = state_mapping[state1]
                    new_state2 = state_mapping[state2]
                    new_group.append((new_state1, new_state2))

            if new_group:  # Only add non-empty coupling groups
                filtered_couplings.append(new_group)
                coupling_idx_map[i] = len(filtered_couplings) - 1

        # Extract relevant energy symbols
        energy_symbols = [hamiltonian.energy_symbols[i] for i in states]

        # Extract relevant coupling, detuning, and Rabi symbols
        coupling_symbols = []
        detuning_symbols = []
        rabi_symbols = []
        omega_substitutions = {}

        for i in range(len(hamiltonian.couplings)):
            if i in coupling_idx_map:
                new_idx = coupling_idx_map[i]
                coupling_symbols.append(hamiltonian.coupling_symbols[i])
                detuning_symbols.append(hamiltonian.detuning_symbols[i])
                rabi_symbols.append(hamiltonian.rabi_symbols[i])

                # Update omega_substitutions with the new mapping
                if hamiltonian.coupling_symbols[i] in hamiltonian.omega_substitutions:
                    omega_substitutions[hamiltonian.coupling_symbols[i]] = (
                        hamiltonian.omega_substitutions[hamiltonian.coupling_symbols[i]]
                    )

        # Create new Hamiltonian and coupling matrices
        new_hamiltonian = smp.zeros(nstates, nstates)
        new_coupling_matrix = smp.zeros(nstates, nstates, complex=True)

        # Fill matrices from the original matrices
        for i in range(nstates):
            for j in range(nstates):
                old_i = reverse_mapping[i]
                old_j = reverse_mapping[j]
                new_hamiltonian[i, j] = hamiltonian.hamiltonian[old_i, old_j]
                new_coupling_matrix[i, j] = hamiltonian.coupling_matrix[old_i, old_j]

        # Update coupling_symbol_paths with new state indices
        new_coupling_symbol_paths = {}
        for (
            old_state1,
            old_state2,
        ), symbols in hamiltonian.coupling_symbol_paths.items():
            if old_state1 in states and old_state2 in states:
                new_state1 = state_mapping[old_state1]
                new_state2 = state_mapping[old_state2]
                new_coupling_symbol_paths[(new_state1, new_state2)] = symbols

        # Create the new total Hamiltonian
        new_total = new_hamiltonian + new_coupling_matrix

        # Create and append the new HamiltonianSymbolic object
        new_ham_symbolic = HamiltonianSymbolic(
            nstates=nstates,
            hamiltonian=new_hamiltonian,
            coupling_matrix=new_coupling_matrix,
            total=new_total,
            coupling_symbol_paths=new_coupling_symbol_paths,
            couplings=filtered_couplings,
            energy_symbols=energy_symbols,
            coupling_symbols=coupling_symbols,
            detuning_symbols=detuning_symbols,
            rabi_symbols=rabi_symbols,
            omega_substitutions=omega_substitutions,
        )

        result_hamiltonians.append(new_ham_symbolic)

    return result_hamiltonians
