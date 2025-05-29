from collections import *
from helper import *

def find_best_swap_nnc(mapping,front_layer,circuit,D,all_phys,coupling_graph):
    """
    Implements the NNC-based heuristic cost.
    We do:
      1) Enumerate all neighbor SWAPs from 'coupling_graph'.
      2) For each candidate SWAP, temporarily apply it to 'mapping'.
      3) Compute cost = sum of distances for all gates in front_layer.
      4) Return the (p_label, q_label) that yields the smallest cost.

    Args:
      mapping: dict {logical_qubit -> physical_qubit}
      front_layer: list of gate_ids (the current front layer F)
      circuit: list of (gate_type, [lq1, lq2], gate_id)
      circuit_dag: adjacency dict gate_id -> [successor gate_ids]
      D: distance matrix, indexed by the *indices* of 'all_phys'
      all_phys: sorted list of physical qubit labels
      coupling_graph: adjacency dict {p_label: [neighbors], ...} for hardware
    """

    # Build label2index so we can do D[ index_of_p ][ index_of_q ]
    label2index = {phys_label: i for i, phys_label in enumerate(all_phys)}

    # Build a quick lookup: gate_id -> (gate_type, [lq1,lq2])
    gate_dict = {g[2]: (g[0], g[1]) for g in circuit}

    # Invert the mapping: physical_qubit -> logical_qubit
    phys2log = {p_label: lq for (lq, p_label) in mapping.items()}

    best_swap = None
    best_cost = float('inf')

    # Enumerate all possible neighbor SWAPs from the coupling graph
    possible_swaps = []
    for p in coupling_graph:
        for q in coupling_graph[p]:
            # To avoid duplicating pairs, only take (p, q) with p<q, or do p<q check
            if q > p:
                possible_swaps.append((p, q))

    # Evaluate each neighbor SWAP
    for (p_label, q_label) in possible_swaps:
        # Which logical qubits currently live at p_label, q_label?
        lqp = phys2log.get(p_label, None)
        lqq = phys2log.get(q_label, None)
        # If a physical wire is not currently used (None), skip
        if lqp is None or lqq is None:
            continue

        # Temporarily apply the SWAP
        temp_mapping = mapping.copy()
        temp_mapping[lqp], temp_mapping[lqq] = q_label, p_label

        # Compute the cost for front_layer gates
        cost = 0
        for gate_id in front_layer:
            gate_type, (lq1, lq2) = gate_dict[gate_id]
            # physical wires after the hypothetical swap
            p1 = temp_mapping[lq1]
            p2 = temp_mapping[lq2]
            idx1 = label2index[p1]
            idx2 = label2index[p2]
            cost += D[idx1][idx2]

        # Keep track of the minimal cost
        if cost < best_cost:
            best_cost = cost
            best_swap = (p_label, q_label, lqp, lqq)

    return best_swap

def sabre_swap_search(circuit, circuit_dag, gate_list, initial_mapping, device_graph, dist_matrix):
    mapping = initial_mapping.copy()
    executed_gates = []
    front_layer = []
    final_circuit = []

    all_phys = set(device_graph.keys())
    for p in device_graph:
        for q in device_graph[p]:
            all_phys.add(q)
    
    # Build in_degrees
    in_degrees = {}

    for g in gate_list:
        in_degrees[g] = 0
    for g in circuit_dag:
        for succ in circuit_dag[g]:
            in_degrees[succ] += 1

    # Initialize front_layer
    for g in gate_list:
        if in_degrees[g] == 0:
            front_layer.append(g)

    # Convert circuit list to a dict for easy reference
    gate_dict = {g[2]: (g[0], g[1]) for g in circuit}  # gate_id -> (type, [qubits])

    while True:
        if len(front_layer) == 0:
            # All gates with dependencies satisfied are done => we're finished
            break

        # 1) Collect executable gates from front_layer
        executable_gates = []
        for gate_id in front_layer:
            gate_type, qubits = gate_dict[gate_id]
            if gate_type == "CNOT":  # two-qubit
                p0 = mapping[qubits[0]]
                p1 = mapping[qubits[1]]
                if is_neighbor(p0, p1, device_graph):
                    executable_gates.append(gate_id)
            else:
                # Single-qubit gate always executable
                executable_gates.append(gate_id)

        if len(executable_gates) > 0:
            # Execute them (remove from front_layer, add to final_circuit)
            for g_id in executable_gates:
                final_circuit.append(("EXECUTE", g_id))  # record that we executed it
                front_layer.remove(g_id)
                executed_gates.append(g_id)

            # Add successors to front_layer if they are now ready
            for g_id in executable_gates:
                # find successors
                for succ in circuit_dag[g_id]:
                    if all_dependencies_executed(succ, executed_gates, circuit_dag):
                        if succ not in front_layer and succ not in executed_gates:
                            front_layer.append(succ)

        else:
            # No gate in front_layer is executable => we must insert a SWAP
            best_swap = find_best_swap_nnc(mapping, front_layer,circuit,circuit_dag,dist_matrix,all_phys, device_graph)
            if best_swap is None: # Debug statement
                raise RuntimeError("No valid swap found. Something is wrong.")
            (p, q, lqp,lqq) = best_swap

             # Insert SWAP into final circuit for clarity
            final_circuit.append(("SWAP", (p, q, lqp,lqq) ))
            
            

            # Update the mapping
            # Find which logical qubits are at p, q
            log_p = None
            log_q = None
            for log_qubit, phys_qubit in mapping.items():
                if phys_qubit == p:
                    log_p = log_qubit
                elif phys_qubit == q:
                    log_q = log_qubit
            mapping[log_p], mapping[log_q] = q, p
            

    return final_circuit, mapping
