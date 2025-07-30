"""Graph transformation utilities for RWA calculations.

This module provides functions to create and manipulate graphs that represent
quantum state couplings, and to generate unitary transformations based on these graphs.
These transformations are used to move into rotating frames for applying the
rotating wave approximation (RWA) in quantum systems.
"""

from typing import Sequence
import string

import networkx as nx
import sympy as smp


def create_coupling_graph(
    couplings: Sequence[Sequence[tuple[int, int]]], nstates: int
) -> nx.Graph:
    """Create a graph representing the couplings between quantum states.

    This function builds a NetworkX MultiGraph where nodes represent quantum states
    and edges represent couplings between states. Each edge is annotated with symbolic
    parameters for frequency (ω) and Rabi frequency (Ω) that characterize the coupling.

    For multiple couplings that share the same frequency, coefficient symbols (a0, a1, etc.)
    are introduced to allow independent control of coupling strengths within the same
    frequency group.

    Args:
        couplings: A list of lists of tuples, where each tuple contains two elements
            representing the indices of coupled states. Each sublist represents a
            group of couplings that share the same frequency.
        nstates: An integer representing the total number of states in the system.

    Returns:
        nx.Graph: A NetworkX MultiGraph where:
            - Nodes represent quantum states (indexed from 0 to nstates-1)
            - Edges represent couplings between states
            - Each edge has attributes:
                * frequency: Symbolic frequency parameter (ω)
                * rabi: Symbolic Rabi frequency parameter (Ω or a{n}*Ω)
                * type: String identifier ("coupling")

    Note:
        Rabi frequencies use the format a{number} * Omega only when there's more
        than one coupling in a group. For single couplings, only the base Omega is used.
        For example:
        - For a group with multiple couplings: a0*Ω0, a1*Ω0, a2*Ω0
        - For a group with a single coupling: just Ω1
    """
    # Initialize an empty MultiGraph (allows multiple edges between same nodes)
    coupling_graph = nx.MultiGraph()

    # Add nodes representing quantum states (numbered 0 to nstates-1)
    coupling_graph.add_nodes_from(range(nstates))

    # Create symbolic parameters for frequencies and base Rabi frequencies
    frequencies = smp.symbols(f"ω0:{len(couplings)}", real=True)
    base_rabis = smp.symbols(f"Ω0:{len(couplings)}", complex=True)

    # Keep track of the global identifier index (across all coupling sets)
    global_identifier_index = 0

    # Process each coupling group
    for idx, (frequency, base_rabi, coupling_group) in enumerate(zip(frequencies, base_rabis, couplings)):
        # Only use identifiers if there's more than one coupling in the group
        multiple_couplings = len(coupling_group) > 1

        # For each coupling in the group, create the appropriate Rabi frequency
        for i, (state1, state2) in enumerate(coupling_group):
            # For single couplings, use the base Rabi directly
            # For multiple couplings, create coefficient symbols (a0, a1, etc.)
            if multiple_couplings:
                coef = smp.symbols(f"a{global_identifier_index}", real=True)
                global_identifier_index += 1
                rabi = coef * base_rabi
            else:
                rabi = base_rabi

            # Add an edge between the coupled states with the corresponding parameters
            coupling_graph.add_edge(
                state1,
                state2,
                frequency=frequency,
                rabi=rabi,
                type="coupling"
            )

    return coupling_graph


def create_transform_matrix(
    coupling_graph: nx.Graph,
) -> smp.Matrix:
    """Create a transformation matrix based on the coupling graph.

    This function analyzes the coupling graph to determine the shortest paths
    between quantum states and generates a transformation matrix. It uses the
    coupling information to calculate phase factors for each state, resulting in
    a diagonal transformation matrix that can be used for rotating the Hamiltonian
    in the interaction picture.

    Args:
        coupling_graph (nx.Graph): A NetworkX graph where nodes represent quantum
            states and edges represent couplings between states.

    Returns:
        smp.Matrix: A diagonal transformation matrix where each element [i,i] contains
            a time-dependent exponential phase factor calculated from the coupling path.

    Raises:
        nx.NetworkXNoPath: If there is no path between a state and the reference node.
    """
    # Get the total number of states from the graph
    nstates = coupling_graph.number_of_nodes()

    # Create time symbol for the transformation
    t = smp.symbols("t", real=True)

    # Initialize the transformation matrix (diagonal)
    transform_matrix = smp.zeros(nstates, nstates, complex=True)

    # Find the node with the highest connectivity (largest degree)
    # This will serve as a reference node for all paths
    reference_node = max(coupling_graph.degree, key=lambda nd: nd[1])[0]

    # Calculate transformation for each state
    for state_idx in range(nstates):
        # Calculate the phase for this state
        phase = _calculate_phase_along_path(
            coupling_graph, state_idx, reference_node
        )

        # Set the diagonal element with the calculated phase
        transform_matrix[state_idx, state_idx] = smp.exp(smp.I * phase * t)

    return transform_matrix


def _calculate_phase_along_path(
    coupling_graph: nx.Graph,
    source: int,
    target: int,
) -> smp.Expr:
    """Calculate the accumulated phase along a path from source to target state.

    Args:
        coupling_graph: NetworkX graph representing state couplings
        coupling_phase: Dictionary of coupling phases between state pairs
        source: Source state index
        target: Target (reference) state index

    Returns:
        sympy expression: The accumulated phase along the path

    Raises:
        nx.NetworkXNoPath: If no path exists between source and target
    """
    try:
        shortest_path = nx.algorithms.shortest_path(
            coupling_graph, source=source, target=target, weight="weight"
        )
    except nx.NetworkXNoPath:
        raise nx.NetworkXNoPath(
            f"No path exists between state {source} and reference state {target}"
        )

    # Initialize the accumulated phase
    phase = smp.S(0)

    # Calculate the phase by traversing along the path
    for j in range(len(shortest_path) - 1):
        # Get adjacent states in the path
        start, stop = shortest_path[j : j + 2]

        # Get the coupling phase between these states
        phase += coupling_graph.get_edge_data(start, stop)[0]["frequency"]

    return phase

def split_into_independent_components(graph: nx.Graph) -> list[nx.Graph]:
    """Split a graph into its independent connected components.

    In quantum systems, connected components represent isolated subsystems that
    don't interact with each other. This function identifies such subsystems by
    finding connected components in the coupling graph.

    A connected component is a subgraph where any two nodes are connected by a
    path, and no nodes in the subgraph are connected to nodes outside the subgraph.

    Args:
        graph: An undirected graph representing couplings between quantum states.
            Nodes represent states, and edges represent couplings.
            s:
        A list of subgraphs, one for each connected component of the input graph.
        Each subgraph contains a set of nodes that are connected to each other
        but disconnected from nodes in other subgraphs.

    Raises:
        TypeError: If the input is not an undirected NetworkX graph.
    """
    # Validate input is a NetworkX undirected graph
    if not isinstance(graph, nx.Graph):
        raise TypeError("Input must be an undirected NetworkX graph")

    # Find all connected components and create separate subgraphs
    # A connected component is a subgraph where all nodes are connected
    return [
        graph.subgraph(component).copy()
        for component in nx.connected_components(graph)
        if len(component) > 1
    ]
