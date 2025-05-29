# Code for drawing the physical mapping and assigned logical qubits for question 1.

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def draw_physical_qubit_graph(device_graph, qubit_assignments=None):
    """
    device_graph: dict {phys_qubit: [neighbors]}
    qubit_assignments: list of (phys_qubit, logical_qubit)
                      e.g. [(0, "q0"), (1, "q1"), ...]
    """
    # Create an undirected graph
    G = nx.Graph()
    for node, neighbors in device_graph.items():
        for neighbor in neighbors:
            G.add_edge(node, neighbor)

    # Convert list of tuples into a dict: phys_qubit -> logical_qubit
    # (If None or empty, we just use an empty dict.)
    assignment_dict = {}
    if qubit_assignments:
        assignment_dict = {p: l for (p, l) in qubit_assignments}

    # Get positions for nodes
    pos = nx.spring_layout(G, seed=42)

    # Draw nodes and edges
    plt.figure(figsize=(5, 4))
    nx.draw_networkx_nodes(G, pos, node_size=1500, node_color="lightblue")
    nx.draw_networkx_edges(G, pos, width=2)

    # 1) Physical labels in black
    phys_labels = {n: str(n) for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=phys_labels,
                            font_color="black", font_size=12)

    # 2) Logical labels in green, drawn slightly below the node
    offset_pos = {n: (x, y - 0.07) for n, (x, y) in pos.items()}
    log_labels = {}
    for pnode in G.nodes():
        if pnode in assignment_dict:
            log_labels[pnode] = str(assignment_dict[pnode])  # "q0", "q1", etc.

    nx.draw_networkx_labels(G, offset_pos, labels=log_labels,
                            font_color="green", font_size=12)

    # Create a legend for physical vs. logical qubits
    phys_patch = mpatches.Patch(color='black', label='Physical Qubit')
    log_patch = mpatches.Patch(color='green', label='Logical Qubit')
    plt.legend(handles=[phys_patch, log_patch], loc='best')

    plt.title("Device Connectivity Graph")
    plt.axis("off")
    plt.show()
