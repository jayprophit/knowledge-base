"""
Quantum State Module

This module implements the core quantum state representation and operations
for the virtual quantum computer.
"""

import numpy as np
from typing import List, Tuple, Union, Optional

class QuantumState:
    """
    Represents a quantum state in the virtual quantum computer.
    
    This class handles the state vector representation of quantum states and
    provides methods for applying quantum operations and measurements.
    """
    
    def __init__(self, num_qubits: int = 1):
        """
        Initialize a quantum state with the specified number of qubits.
        
        Args:
            num_qubits: Number of qubits in the quantum state
        """
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        self.state = np.zeros(self.dim, dtype=complex)
        self.state[0] = 1.0  # Initialize to |0...0⟩
        self._validate_state()
    
    def _validate_state(self):
        """Ensure the state vector is properly normalized."""
        norm = np.sum(np.abs(self.state) ** 2)
        if not np.isclose(norm, 1.0, atol=1e-10):
            self.state /= np.sqrt(norm)
    
    def apply_unitary(self, matrix: np.ndarray, qubits: Union[int, List[int]]):
        """
        Apply a unitary operation to the quantum state.
        
        Args:
            matrix: Unitary matrix to apply
            qubits: Qubit(s) to apply the operation to
        """
        if isinstance(qubits, int):
            qubits = [qubits]
        
        # Convert qubit indices to proper positions in the state vector
        num_target_qubits = int(np.log2(matrix.shape[0]))
        
        # Create the full matrix for the operation
        full_matrix = self._embed_operator(matrix, qubits)
        
        # Apply the operation
        self.state = np.dot(full_matrix, self.state)
        self._validate_state()
    
    def measure(self, qubit: int, basis: str = 'z') -> int:
        """
        Measure a qubit in the specified basis.
        
        Args:
            qubit: Index of the qubit to measure
            basis: Measurement basis ('x', 'y', or 'z')
            
        Returns:
            Measurement outcome (0 or 1)
        """
        # For now, just implement Z-basis measurement
        if basis != 'z':
            raise NotImplementedError("Only Z-basis measurement is currently implemented")
        
        # Calculate probabilities
        prob0 = 0.0
        for i in range(self.dim):
            if not (i & (1 << qubit)):  # Check if qubit is 0 in this basis state
                prob0 += np.abs(self.state[i]) ** 2
        
        # Perform measurement
        if np.random.random() < prob0:
            # Collapse to |0⟩
            for i in range(self.dim):
                if (i & (1 << qubit)):  # If qubit is 1 in this basis state
                    self.state[i] = 0.0
            self._normalize()
            return 0
        else:
            # Collapse to |1⟩
            for i in range(self.dim):
                if not (i & (1 << qubit)):  # If qubit is 0 in this basis state
                    self.state[i] = 0.0
            self._normalize()
            return 1
    
    def _normalize(self):
        """Normalize the state vector."""
        norm = np.linalg.norm(self.state)
        if norm > 0:
            self.state /= norm
    
    def _embed_operator(self, matrix: np.ndarray, qubits: List[int]) -> np.ndarray:
        """
        Embed an operator matrix into the full Hilbert space.
        
        Args:
            matrix: Operator matrix to embed
            qubits: Qubits the operator acts on
            
        Returns:
            Full operator matrix in the complete Hilbert space
        """
        # Sort qubits to determine the correct tensor product order
        qubits = sorted(qubits)
        num_qubits_op = int(np.log2(matrix.shape[0]))
        
        # Create identity matrices for non-target qubits
        full_matrix = np.eye(1, dtype=complex)
        current_qubit = 0
        
        for q in range(self.num_qubits):
            if q in qubits:
                # This qubit is part of the operation
                op_qubit_idx = qubits.index(q)
                # Get the appropriate sub-matrix for this qubit
                sub_matrix = np.eye(2)
                # For now, just use the full matrix (will need to be updated for multi-qubit gates)
                if op_qubit_idx == 0:
                    sub_matrix = matrix
                full_matrix = np.kron(full_matrix, sub_matrix)
                current_qubit += num_qubits_op
            else:
                # This qubit is not part of the operation, use identity
                full_matrix = np.kron(full_matrix, np.eye(2))
                current_qubit += 1
        
        return full_matrix
    
    def get_probabilities(self) -> np.ndarray:
        """
        Get the probability distribution over computational basis states.
        
        Returns:
            Array of probabilities for each basis state
        """
        return np.abs(self.state) ** 2
    
    def get_density_matrix(self) -> np.ndarray:
        """
        Get the density matrix representation of the state.
        
        Returns:
            Density matrix (2^N x 2^N for N qubits)
        """
        return np.outer(self.state, self.state.conj())
    
    def __str__(self) -> str:
        """String representation of the quantum state."""
        result = []
        for i in range(self.dim):
            if not np.isclose(self.state[i], 0):
                basis_state = f"|{i:0{self.num_qubits}b}>"
                amplitude = self.state[i]
                result.append(f"{amplance:.4f}{basis_state}")
        return " + ".join(result)
