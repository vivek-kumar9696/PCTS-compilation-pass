from pennylane import numpy as np
from collections import *

import math

def is_neighbor(p, q, device_graph):
    return q in device_graph[p]
    
def all_dependencies_executed(gate_id, executed_set, circuit_dag):
    """
    Check if all gates leading into gate_id are in executed_set.
    """
    for gate_src in circuit_dag:
        if gate_id in circuit_dag[gate_src] and gate_src not in executed_set:
            return False
    return True

def build_distance_matrix(device_graph, num_qubits):
    # Initialize distance matrix with infinity
    dist_matrix = [[math.inf]*num_qubits for _ in range(num_qubits)]
    # Distance from a node to itself = 0
    for i in range(num_qubits):
        dist_matrix[i][i] = 0

    # Fill in edges
    for p in device_graph:
        for neighbor in device_graph[p]:
            dist_matrix[p][neighbor] = 1
            dist_matrix[neighbor][p] = 1

    # Floyd-Warshall to find all pairs shortest paths
    for k in range(num_qubits):
        for i in range(num_qubits):
            for j in range(num_qubits):
                if dist_matrix[i][j] > dist_matrix[i][k] + dist_matrix[k][j]:
                    dist_matrix[i][j] = dist_matrix[i][k] + dist_matrix[k][j]
    return dist_matrix

def build_circuit_dag(circuit):
    # circuit_dag will store adjacency as: gate -> [list_of_successors]
    circuit_dag = defaultdict(list)
    # keep track of all the qubits used by each gate
    qubit_usage = {}
    gate_list = []

    for idx, gate in enumerate(circuit):
        gate_type, qubits, gate_id = gate
        gate_list.append(gate_id)
        qubit_usage[gate_id] = qubits

    # For each pair of gates, see if they share qubits
    # and if there's an ordering in the original circuit
    for i in range(len(circuit)):
        _, qubits_i, id_i = circuit[i]
        for j in range(i+1, len(circuit)):
            _, qubits_j, id_j = circuit[j]
            # If they share any qubit, then there's a dependence
            if set(qubits_i).intersection(qubits_j):
                # i must come before j in the circuit listing
                circuit_dag[id_i].append(id_j)

    return circuit_dag, gate_list

def count_logical_qubits(circuit):
    """
    Given an 'initial_circuit' list like:
        [("CNOT", [0,1], "g1"), ("CNOT", [1,2], "g2"), ...]
    returns the total number of distinct logical qubits used.
    """
    used_qubits = set()
    for (gate_type, qubits, gate_id) in circuit:
        for q in qubits:
            used_qubits.add(q)
    return len(used_qubits)

def count_physical_qubits(coupling_graph):
    """
    Given a coupling graph dict like:
        {0:[1], 1:[0,2,3], 2:[1], 3:[1,4], 4:[3]}
    returns how many distinct physical qubits are in the hardware.
    """
    # The keys themselves are the physical qubits, but let's also
    # check neighbors (in case some qubits appear only as neighbors).
    all_nodes = set(coupling_graph.keys())
    for k, neighbors in coupling_graph.items():
        for n in neighbors:
            all_nodes.add(n)
    return len(all_nodes), sorted(all_nodes)