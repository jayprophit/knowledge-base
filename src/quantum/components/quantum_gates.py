"""
Quantum Gates Module

This module implements standard quantum gates and operations for the virtual quantum computer.
"""

import numpy as np
from typing import List, Union, Optional

# Single-qubit gates
I = np.array([[1, 0], [0, 1]], dtype=complex)  # Identity
X = np.array([[0, 1], [1, 0]], dtype=complex)  # Pauli-X (NOT)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)  # Pauli-Y
Z = np.array([[1, 0], [0, -1]], dtype=complex)  # Pauli-Z
H = (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)  # Hadamard
S = np.array([[1, 0], [0, 1j]], dtype=complex)  # Phase gate
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)  # T gate

# Two-qubit gates
CNOT = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 0]
], dtype=complex)

SWAP = np.array([
    [1, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1]
], dtype=complex)

# Three-qubit gates
TOFFOLI = np.eye(8, dtype=complex)
TOFFOLI[6:8, 6:8] = [[0, 1], [1, 0]]

class QuantumGate:
    """Base class for quantum gates."""
    
    def __init__(self, name: str, matrix: np.ndarray, num_qubits: int):
        """
        Initialize a quantum gate.
        
        Args:
            name: Name of the gate
            matrix: Unitary matrix representing the gate
            num_qubits: Number of qubits this gate acts on
        """
        self.name = name
        self.matrix = matrix
        self.num_qubits = num_qubits
    
    def __call__(self, *qubits):
        """
        Apply this gate to specific qubits.
        
        Args:
            *qubits: Qubit indices to apply the gate to
            
        Returns:
            A tuple of (gate, qubits) for deferred application
        """
        if len(qubits) != self.num_qubits:
            raise ValueError(f"{self.name} gate requires exactly {self.num_qubits} qubits")
        return (self, qubits)
    
    def __str__(self) -> str:
        return f"{self.name} gate"


# Single-qubit gate instances
class SingleQubitGate(QuantumGate):
    """Single-qubit quantum gate."""
    def __init__(self, name: str, matrix: np.ndarray):
        super().__init__(name, matrix, 1)

# Standard single-qubit gates
I_gate = SingleQubitGate("I", I)
X_gate = SingleQubitGate("X", X)
Y_gate = SingleQubitGate("Y", Y)
Z_gate = SingleQubitGate("Z", Z)
H_gate = SingleQubitGate("H", H)
S_gate = SingleQubitGate("S", S)
T_gate = SingleQubitGate("T", T)

# Two-qubit gate instances
class TwoQubitGate(QuantumGate):
    """Two-qubit quantum gate."""
    def __init__(self, name: str, matrix: np.ndarray):
        super().__init__(name, matrix, 2)

CNOT_gate = TwoQubitGate("CNOT", CNOT)
SWAP_gate = TwoQubitGate("SWAP", SWAP)

# Three-qubit gate instances
class ThreeQubitGate(QuantumGate):
    """Three-qubit quantum gate."""
    def __init__(self, name: str, matrix: np.ndarray):
        super().__init__(name, matrix, 3)

TOFFOLI_gate = ThreeQubitGate("TOFFOLI", TOFFOLI)

def rotation_x(theta: float) -> np.ndarray:
    """
    Rotation around the X-axis by angle theta.
    
    Args:
        theta: Rotation angle in radians
        
    Returns:
        Rotation matrix
    """
    return np.array([
        [np.cos(theta/2), -1j*np.sin(theta/2)],
        [-1j*np.sin(theta/2), np.cos(theta/2)]
    ], dtype=complex)

def rotation_y(theta: float) -> np.ndarray:
    """
    Rotation around the Y-axis by angle theta.
    
    Args:
        theta: Rotation angle in radians
        
    Returns:
        Rotation matrix
    """
    return np.array([
        [np.cos(theta/2), -np.sin(theta/2)],
        [np.sin(theta/2), np.cos(theta/2)]
    ], dtype=complex)

def rotation_z(theta: float) -> np.ndarray:
    """
    Rotation around the Z-axis by angle theta.
    
    Args:
        theta: Rotation angle in radians
        
    Returns:
        Rotation matrix
    """
    return np.array([
        [np.exp(-1j*theta/2), 0],
        [0, np.exp(1j*theta/2)]
    ], dtype=complex)

def phase_shift(phi: float) -> np.ndarray:
    """
    Phase shift gate.
    
    Args:
        phi: Phase shift angle in radians
        
    Returns:
        Phase shift matrix
    """
    return np.array([
        [1, 0],
        [0, np.exp(1j*phi)]
    ], dtype=complex)

def controlled_u(u_matrix: np.ndarray) -> np.ndarray:
    """
    Create a controlled-U gate from a single-qubit unitary U.
    
    Args:
        u_matrix: 2x2 unitary matrix
        
    Returns:
        4x4 controlled-U matrix
    """
    return np.block([
        [np.eye(2), np.zeros((2, 2))],
        [np.zeros((2, 2)), u_matrix]
    ])

def tensor_product(gates: List[np.ndarray]) -> np.ndarray:
    """
    Compute the tensor product of multiple gates.
    
    Args:
        gates: List of gate matrices
        
    Returns:
        Tensor product of all gates
    """
    result = np.array([[1.0+0.0j]])
    for gate in gates:
        result = np.kron(result, gate)
    return result
