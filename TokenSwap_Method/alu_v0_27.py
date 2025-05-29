import pennylane as qml

# We need at least 5 qubits since the highest index is 4
dev = qml.device("default.qubit", wires=5)

@qml.qnode(dev)
def alu_v0_circuit():
    # 1. CNOT gates
    qml.CNOT(wires=[3, 4])
    qml.CNOT(wires=[2, 1])

    # 2. Single-qubit gates: H, T
    qml.Hadamard(wires=2)
    qml.T(wires=3)
    qml.T(wires=1)
    qml.T(wires=2)

    # 3. More CNOT
    qml.CNOT(wires=[1, 3])
    qml.CNOT(wires=[2, 1])
    qml.CNOT(wires=[3, 2])

    # 4. tdag is T^\dagger
    qml.adjoint(qml.T)(wires=1)   
    qml.CNOT(wires=[3, 1])
    qml.adjoint(qml.T)(wires=3)
    qml.adjoint(qml.T)(wires=1)

    # 5. T on qubit 2
    qml.T(wires=2)

    # 6. More CNOT
    qml.CNOT(wires=[2, 1])
    qml.CNOT(wires=[3, 2])
    qml.CNOT(wires=[1, 3])

    # 7. Another H, then CNOT, X, H
    qml.Hadamard(wires=2)
    qml.CNOT(wires=[2, 0])
    qml.PauliX(wires=2)
    qml.Hadamard(wires=2)

    # 8. T gates
    qml.T(wires=4)
    qml.T(wires=0)
    qml.T(wires=2)

    # 9. More CNOT
    qml.CNOT(wires=[0, 4])
    qml.CNOT(wires=[2, 0])
    qml.CNOT(wires=[4, 2])

    # 10. tdag on qubit 0
    qml.adjoint(qml.T)(wires=0)
    qml.CNOT(wires=[4, 0])
    qml.adjoint(qml.T)(wires=4)
    qml.adjoint(qml.T)(wires=0)

    # 11. T on qubit 2
    qml.T(wires=2)

    # 12. Final batch of CNOT gates and one last H
    qml.CNOT(wires=[2, 0])
    qml.CNOT(wires=[4, 2])
    qml.CNOT(wires=[0, 4])
    qml.Hadamard(wires=2)

    # Return final state for demonstration
    return qml.state()
