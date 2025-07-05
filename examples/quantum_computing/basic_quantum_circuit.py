"""
Basic Quantum Circuit Example

This script demonstrates how to use the Virtual Quantum Computer
implementation to create and run simple quantum circuits.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Add the project root to the path so we can import our quantum computer
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.quantum.virtual_quantum_computer import VirtualQuantumComputer

def simple_superposition():
    """Demonstrate quantum superposition with a single qubit."""
    print("\n=== Quantum Superposition ===")
    
    # Create a quantum computer with 1 qubit
    qc = VirtualQuantumComputer(1)
    
    # Apply Hadamard gate to create superposition
    qc.h(0)
    
    # Run the circuit
    counts = qc.run(shots=1000)
    
    print("Measurement results:", counts)
    print("State vector:", qc.get_statevector())
    
    return qc

def quantum_entanglement():
    """Demonstrate quantum entanglement with two qubits."""
    print("\n=== Quantum Entanglement ===")
    
    # Create a quantum computer with 2 qubits
    qc = VirtualQuantumComputer(2)
    
    # Create a Bell pair (maximally entangled state)
    qc.h(0)     # Apply Hadamard to first qubit
    qc.cx(0, 1)  # Apply CNOT with control on first qubit and target on second
    
    # Run the circuit
    counts = qc.run(shots=1000)
    
    print("Measurement results:", counts)
    print("State vector:", qc.get_statevector())
    
    return qc

def quantum_teleportation():
    """Demonstrate quantum teleportation protocol."""
    print("\n=== Quantum Teleportation ===")
    
    # Create a quantum computer with 3 qubits
    # q0: Alice's qubit to be teleported
    # q1: Alice's part of entangled pair
    # q2: Bob's part of entangled pair
    qc = VirtualQuantumComputer(3)
    
    # Prepare the state to be teleported (let's use |1⟩ for demonstration)
    qc.x(0)
    
    # Create entanglement between Alice and Bob (Bell pair on q1 and q2)
    qc.h(1)
    qc.cx(1, 2)
    
    # Alice performs Bell measurement on her qubits (q0 and q1)
    qc.cx(0, 1)
    qc.h(0)
    
    # Measure Alice's qubits
    qc.measure(0, 0)  # Store result in classical bit 0
    qc.measure(1, 1)  # Store result in classical bit 1
    
    # Bob applies corrections based on measurement results
    qc.cx(1, 2)
    qc.cz(0, 2)
    
    # Run the circuit
    counts = qc.run(shots=1000)
    
    print("Measurement results (classical bits):", counts)
    print("Final state of Bob's qubit (should be |1⟩):", qc.get_statevector()[4:])  # Last two amplitudes for |100⟩ and |101⟩
    
    return qc

def quantum_fourier_transform(n_qubits=3):
    """Demonstrate the quantum Fourier transform."""
    print(f"\n=== Quantum Fourier Transform ({n_qubits} qubits) ===")
    
    # Create a quantum computer with n_qubits
    qc = VirtualQuantumComputer(n_qubits)
    
    # Prepare an input state (superposition of all basis states)
    for i in range(n_qubits):
        qc.h(i)
    
    # Apply QFT
    for i in range(n_qubits):
        # Apply Hadamard to qubit i
        qc.h(i)
        
        # Apply controlled rotations
        for j in range(i + 1, n_qubits):
            theta = np.pi / (2 ** (j - i))
            qc.cp(theta, j, i)  # Controlled phase shift
    
    # Swap qubits to match the standard QFT definition
    for i in range(n_qubits // 2):
        qc.swap(i, n_qubits - 1 - i)
    
    # Run the circuit
    counts = qc.run(shots=1000)
    
    print("Measurement results:", counts)
    print("State vector:", qc.get_statevector())
    
    return qc

def grovers_algorithm():
    """Demonstrate Grover's search algorithm."""
    print("\n=== Grover's Algorithm ===")
    
    # Number of qubits (2 qubits can represent 4 states: 00, 01, 10, 11)
    n_qubits = 2
    qc = VirtualQuantumComputer(n_qubits)
    
    # Oracle: marks the state |11⟩ (target state)
    def oracle():
        # This is a controlled-Z gate (flips the sign of |11⟩)
        qc.h(1)
        qc.cx(0, 1)
        qc.h(1)
    
    # Diffusion operator
    def diffusion():
        for i in range(n_qubits):
            qc.h(i)
            qc.x(i)
        
        # Apply controlled-Z
        qc.h(1)
        qc.cx(0, 1)
        qc.h(1)
        
        for i in range(n_qubits):
            qc.x(i)
            qc.h(i)
    
    # Initialize all qubits in superposition
    for i in range(n_qubits):
        qc.h(i)
    
    # Apply Grover iteration (optimal number of times)
    num_iterations = int(np.floor(np.pi * np.sqrt(2**n_qubits) / 4))
    
    for _ in range(num_iterations):
        # Apply oracle
        oracle()
        
        # Apply diffusion operator
        diffusion()
    
    # Measure the qubits
    for i in range(n_qubits):
        qc.measure(i, i)
    
    # Run the circuit
    counts = qc.run(shots=1000)
    
    print(f"Measurement results (after {num_iterations} iterations):", counts)
    print("Most probable state:", max(counts, key=counts.get))
    
    return qc

def plot_results(counts, title):
    """Plot the measurement results."""
    plt.figure(figsize=(10, 5))
    plt.bar(counts.keys(), counts.values())
    plt.title(title)
    plt.xlabel('State')
    plt.ylabel('Counts')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("=== Quantum Computing Examples ===")
    
    # Run examples
    qc1 = simple_superposition()
    plot_results(qc1.get_counts(), "Quantum Superposition")
    
    qc2 = quantum_entanglement()
    plot_results(qc2.get_counts(), "Quantum Entanglement (Bell State)")
    
    qc3 = quantum_teleportation()
    
    qc4 = quantum_fourier_transform(3)
    plot_results(qc4.get_counts(), "Quantum Fourier Transform")
    
    qc5 = grovers_algorithm()
    plot_results(qc5.get_counts(), "Grover's Algorithm")
