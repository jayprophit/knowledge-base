"""
Virtual Quantum Computer

This module provides a high-level interface for simulating quantum computations
using the virtual quantum computer implementation.
"""

from typing import Dict, List, Union, Optional, Any
import numpy as np
from .core.quantum_circuit import QuantumCircuit
from .core.quantum_state import QuantumState
from .components.quantum_gates import (
    I_gate, X_gate, Y_gate, Z_gate, H_gate, S_gate, T_gate,
    CNOT_gate, SWAP_gate, TOFFOLI_gate,
    rotation_x, rotation_y, rotation_z, phase_shift, controlled_u
)

class VirtualQuantumComputer:
    """
    A virtual quantum computer that provides a high-level interface for quantum computations.
    """
    
    def __init__(self, num_qubits: int, num_classical_bits: Optional[int] = None):
        """
        Initialize the virtual quantum computer.
        
        Args:
            num_qubits: Number of qubits in the quantum computer
            num_classical_bits: Number of classical bits (defaults to num_qubits)
        """
        if num_classical_bits is None:
            num_classical_bits = num_qubits
        
        self.num_qubits = num_qubits
        self.num_classical_bits = num_classical_bits
        self.circuit = QuantumCircuit(num_qubits, num_classical_bits)
        self.results = {}
    
    def x(self, qubit: int) -> 'VirtualQuantumComputer':
        """Apply Pauli-X (NOT) gate."""
        self.circuit.x(qubit)
        return self
    
    def y(self, qubit: int) -> 'VirtualQuantumComputer':
        """Apply Pauli-Y gate."""
        self.circuit.y(qubit)
        return self
    
    def z(self, qubit: int) -> 'VirtualQuantumComputer':
        """Apply Pauli-Z gate."""
        self.circuit.z(qubit)
        return self
    
    def h(self, qubit: int) -> 'VirtualQuantumComputer':
        """Apply Hadamard gate."""
        self.circuit.h(qubit)
        return self
    
    def s(self, qubit: int) -> 'VirtualQuantumComputer':
        """Apply S gate (π/2 phase)."""
        self.circuit.s(qubit)
        return self
    
    def t(self, qubit: int) -> 'VirtualQuantumComputer':
        """Apply T gate (π/4 phase)."""
        self.circuit.t(qubit)
        return self
    
    def rx(self, theta: float, qubit: int) -> 'VirtualQuantumComputer':
        """Apply rotation around X-axis by angle theta."""
        self.circuit.rx(theta, qubit)
        return self
    
    def ry(self, theta: float, qubit: int) -> 'VirtualQuantumComputer':
        """Apply rotation around Y-axis by angle theta."""
        self.circuit.ry(theta, qubit)
        return self
    
    def rz(self, phi: float, qubit: int) -> 'VirtualQuantumComputer':
        """Apply rotation around Z-axis by angle phi."""
        self.circuit.rz(phi, qubit)
        return self
    
    def phase(self, phi: float, qubit: int) -> 'VirtualQuantumComputer':
        """Apply phase shift gate."""
        self.circuit.append(phase_shift(phi), qubit)
        return self
    
    def cnot(self, control: int, target: int) -> 'VirtualQuantumComputer':
        """Apply controlled-NOT (CNOT) gate."""
        self.circuit.cnot(control, target)
        return self
    
    def cx(self, control: int, target: int) -> 'VirtualQuantumComputer':
        """Alias for CNOT gate."""
        return self.cnot(control, target)
    
    def swap(self, qubit1: int, qubit2: int) -> 'VirtualQuantumComputer':
        """Apply SWAP gate."""
        self.circuit.swap(qubit1, qubit2)
        return self
    
    def toffoli(self, control1: int, control2: int, target: int) -> 'VirtualQuantumComputer':
        """Apply Toffoli (CCNOT) gate."""
        self.circuit.toffoli(control1, control2, target)
        return self
    
    def ccx(self, control1: int, control2: int, target: int) -> 'VirtualQuantumComputer':
        """Alias for Toffoli (CCNOT) gate."""
        return self.toffoli(control1, control2, target)
    
    def measure(self, qubit: int, cbit: Optional[int] = None) -> 'VirtualQuantumComputer':
        """
        Measure a qubit and store the result in a classical bit.
        
        Args:
            qubit: Qubit to measure
            cbit: Classical bit to store the result (defaults to qubit index)
        """
        self.circuit.measure(qubit, cbit)
        return self
    
    def reset(self, qubit: Optional[int] = None) -> 'VirtualQuantumComputer':
        """
        Reset one or all qubits to |0⟩.
        
        Args:
            qubit: Qubit to reset (if None, reset all qubits)
        """
        self.circuit.reset(qubit)
        return self
    
    def run(self, shots: int = 1024) -> Dict[str, int]:
        """
        Run the quantum circuit and return measurement statistics.
        
        Args:
            shots: Number of times to run the circuit
            
        Returns:
            Dictionary mapping measurement outcomes to their counts
        """
        self.results = self.circuit.run(shots)
        return self.results
    
    def get_statevector(self) -> np.ndarray:
        """
        Get the current state vector of the quantum computer.
        
        Returns:
            The state vector as a numpy array
        """
        return self.circuit.get_statevector()
    
    def get_counts(self) -> Dict[str, int]:
        """
        Get the measurement counts from the last run.
        
        Returns:
            Dictionary mapping measurement outcomes to their counts
        """
        return self.results
    
    def get_expectation_value(self, operator: np.ndarray, qubits: List[int]) -> float:
        """
        Calculate the expectation value of an operator.
        
        Args:
            operator: The operator to calculate expectation value for
            qubits: Qubits the operator acts on
            
        Returns:
            The expectation value
        """
        state = self.get_statevector()
        if len(qubits) == 1:
            # Single-qubit operator
            op = operator
            for _ in range(qubits[0]):
                op = np.kron(np.eye(2), op)
            for _ in range(self.num_qubits - qubits[0] - 1):
                op = np.kron(op, np.eye(2))
        else:
            # Multi-qubit operator (simplified implementation)
            op = operator
            # This is a simplified implementation and may need adjustment
            # for arbitrary multi-qubit operators
            pass
            
        return np.real(np.vdot(state, op @ state))
    
    def get_density_matrix(self) -> np.ndarray:
        """
        Get the density matrix of the current quantum state.
        
        Returns:
            The density matrix
        """
        state = self.get_statevector()
        return np.outer(state, state.conj())
    
    def get_entropy(self, qubit: int) -> float:
        """
        Calculate the von Neumann entropy of a qubit.
        
        Args:
            qubit: Qubit index
            
        Returns:
            The von Neumann entropy
        """
        # Get the reduced density matrix for the qubit
        rho = self.get_reduced_density_matrix([qubit])
        
        # Calculate eigenvalues (avoid log(0) by adding a small epsilon)
        eigvals = np.linalg.eigvalsh(rho)
        eigvals = np.maximum(eigvals, 1e-16)  # Avoid log(0)
        
        # Calculate von Neumann entropy: -sum(p_i * log2(p_i))
        entropy = -np.sum(eigvals * np.log2(eigvals))
        return entropy
    
    def get_reduced_density_matrix(self, qubits: List[int]) -> np.ndarray:
        """
        Get the reduced density matrix for a subset of qubits.
        
        Args:
            qubits: List of qubit indices to keep
            
        Returns:
            The reduced density matrix
        """
        # This is a simplified implementation
        # For a full implementation, we would need to trace out the other qubits
        # Here we just return the full density matrix for simplicity
        return self.get_density_matrix()
    
    def draw(self) -> str:
        """
        Generate a simple ASCII art representation of the circuit.
        
        Returns:
            String representation of the circuit
        """
        return self.circuit.draw()
    
    def __str__(self) -> str:
        """String representation of the virtual quantum computer."""
        return f"VirtualQuantumComputer({self.num_qubits} qubits, {self.num_classical_bits} classical bits)"
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return self.__str__()
