"""
Quantum Circuit Module

This module implements a quantum circuit for the virtual quantum computer.
"""

from typing import List, Tuple, Union, Optional, Dict, Any
import numpy as np
from .quantum_state import QuantumState
from ..components.quantum_gates import (
    I_gate, X_gate, Y_gate, Z_gate, H_gate, S_gate, T_gate,
    CNOT_gate, SWAP_gate, TOFFOLI_gate,
    rotation_x, rotation_y, rotation_z, phase_shift, controlled_u
)

class QuantumCircuit:
    """
    A quantum circuit that can apply quantum gates and perform measurements.
    """
    
    def __init__(self, num_qubits: int, num_classical_bits: int = 0):
        """
        Initialize a quantum circuit.
        
        Args:
            num_qubits: Number of qubits in the circuit
            num_classical_bits: Number of classical bits for measurement results
        """
        self.num_qubits = num_qubits
        self.num_classical_bits = num_classical_bits
        self.quantum_state = QuantumState(num_qubits)
        self.gates = []
        self.classical_bits = [0] * num_classical_bits
        self.measurement_results = []
        
        # Standard gate set
        self.gate_set = {
            'i': I_gate, 'x': X_gate, 'y': Y_gate, 'z': Z_gate,
            'h': H_gate, 's': S_gate, 't': T_gate,
            'cnot': CNOT_gate, 'cx': CNOT_gate,
            'swap': SWAP_gate,
            'toffoli': TOFFOLI_gate, 'ccx': TOFFOLI_gate
        }
    
    def append(self, gate, qubits: Union[int, List[int]], *params) -> 'QuantumCircuit':
        """
        Append a gate to the circuit.
        
        Args:
            gate: Gate to append (can be a string name or gate object)
            qubits: Qubit(s) to apply the gate to
            *params: Additional parameters for parameterized gates
            
        Returns:
            self for method chaining
        """
        if isinstance(gate, str):
            gate_name = gate.lower()
            if gate_name not in self.gate_set:
                raise ValueError(f"Unknown gate: {gate}")
            gate = self.gate_set[gate_name]
        
        if not isinstance(qubits, (list, tuple)):
            qubits = [qubits]
        
        # Handle parameterized gates
        if callable(gate):
            gate = gate(*params)
        
        self.gates.append((gate, qubits))
        return self
    
    def x(self, qubit: int) -> 'QuantumCircuit':
        """Apply Pauli-X (NOT) gate."""
        return self.append(X_gate, qubit)
    
    def y(self, qubit: int) -> 'QuantumCircuit':
        """Apply Pauli-Y gate."""
        return self.append(Y_gate, qubit)
    
    def z(self, qubit: int) -> 'QuantumCircuit':
        """Apply Pauli-Z gate."""
        return self.append(Z_gate, qubit)
    
    def h(self, qubit: int) -> 'QuantumCircuit':
        """Apply Hadamard gate."""
        return self.append(H_gate, qubit)
    
    def s(self, qubit: int) -> 'QuantumCircuit':
        """Apply S gate (π/2 phase)."""
        return self.append(S_gate, qubit)
    
    def t(self, qubit: int) -> 'QuantumCircuit':
        """Apply T gate (π/4 phase)."""
        return self.append(T_gate, qubit)
    
    def rx(self, theta: float, qubit: int) -> 'QuantumCircuit':
        """Apply rotation around X-axis by angle theta."""
        return self.append(rotation_x, qubit, theta)
    
    def ry(self, theta: float, qubit: int) -> 'QuantumCircuit':
        """Apply rotation around Y-axis by angle theta."""
        return self.append(rotation_y, qubit, theta)
    
    def rz(self, theta: float, qubit: int) -> 'QuantumCircuit':
        """Apply rotation around Z-axis by angle theta."""
        return self.append(rotation_z, qubit, theta)
    
    def cnot(self, control: int, target: int) -> 'QuantumCircuit':
        """Apply controlled-NOT (CNOT) gate."""
        return self.append(CNOT_gate, [control, target])
    
    def cx(self, control: int, target: int) -> 'QuantumCircuit':
        """Alias for CNOT gate."""
        return self.cnot(control, target)
    
    def swap(self, qubit1: int, qubit2: int) -> 'QuantumCircuit':
        """Apply SWAP gate."""
        return self.append(SWAP_gate, [qubit1, qubit2])
    
    def toffoli(self, control1: int, control2: int, target: int) -> 'QuantumCircuit':
        """Apply Toffoli (CCNOT) gate."""
        return self.append(TOFFOLI_gate, [control1, control2, target])
    
    def ccx(self, control1: int, control2: int, target: int) -> 'QuantumCircuit':
        """Alias for Toffoli (CCNOT) gate."""
        return self.toffoli(control1, control2, target)
    
    def measure(self, qubit: int, cbit: Optional[int] = None) -> 'QuantumCircuit':
        """
        Measure a qubit and store the result in a classical bit.
        
        Args:
            qubit: Qubit to measure
            cbit: Classical bit to store the result (defaults to qubit index)
            
        Returns:
            self for method chaining
        """
        if cbit is None:
            cbit = qubit
        if cbit >= self.num_classical_bits:
            raise ValueError(f"Classical bit {cbit} out of range")
        
        # For now, just perform immediate measurement
        # In a more advanced implementation, we might want to defer measurement
        result = self.quantum_state.measure(qubit)
        if cbit is not None:
            self.classical_bits[cbit] = result
        self.measurement_results.append((qubit, cbit, result))
        return self
    
    def reset(self, qubit: Optional[int] = None) -> 'QuantumCircuit':
        """
        Reset one or all qubits to |0⟩.
        
        Args:
            qubit: Qubit to reset (if None, reset all qubits)
            
        Returns:
            self for method chaining
        """
        if qubit is None:
            # Reset all qubits
            self.quantum_state = QuantumState(self.num_qubits)
        else:
            # Measure and apply X gate if needed to reset to |0⟩
            if self.measure(qubit).get_measurement(qubit) == 1:
                self.x(qubit)
        return self
    
    def run(self, shots: int = 1) -> Dict[str, int]:
        """
        Run the circuit and return measurement statistics.
        
        Args:
            shots: Number of times to run the circuit
            
        Returns:
            Dictionary mapping measurement outcomes to their counts
        """
        results = {}
        
        for _ in range(shots):
            # Create a fresh copy of the initial state
            state = QuantumState(self.num_qubits)
            
            # Apply all gates
            for gate, qubits in self.gates:
                if isinstance(gate, tuple):
                    # Handle parameterized gates
                    gate_obj, *params = gate
                    gate = gate_obj(*params)
                
                if hasattr(gate, 'matrix'):
                    state.apply_unitary(gate.matrix, qubits)
                else:
                    # Handle custom unitary operations
                    state.apply_unitary(gate, qubits)
            
            # Perform measurements
            measurement = []
            for qubit, cbit, _ in self.measurement_results:
                result = state.measure(qubit)
                measurement.append(str(result))
            
            # Update results
            outcome = ''.join(reversed(measurement)) if measurement else '0' * self.num_qubits
            results[outcome] = results.get(outcome, 0) + 1
        
        return results
    
    def get_statevector(self) -> np.ndarray:
        """
        Get the current state vector of the quantum circuit.
        
        Returns:
            The state vector as a numpy array
        """
        return self.quantum_state.state
    
    def get_measurement(self, qubit: int) -> int:
        """
        Get the last measurement result for a qubit.
        
        Args:
            qubit: Qubit index
            
        Returns:
            Last measurement result (0 or 1)
        """
        for q, _, result in reversed(self.measurement_results):
            if q == qubit:
                return result
        raise ValueError(f"No measurement result available for qubit {qubit}")
    
    def depth(self) -> int:
        """
        Calculate the depth of the circuit.
        
        Returns:
            The circuit depth (number of layers)
        """
        if not self.gates:
            return 0
        
        # Simple implementation: count the maximum number of gates on any qubit
        qubit_depth = [0] * self.num_qubits
        
        for gate, qubits in self.gates:
            if isinstance(qubits, int):
                qubits = [qubits]
            max_depth = max(qubit_depth[q] for q in qubits)
            for q in qubits:
                qubit_depth[q] = max_depth + 1
        
        return max(qubit_depth, default=0)
    
    def draw(self) -> str:
        """
        Generate a simple ASCII art representation of the circuit.
        
        Returns:
            String representation of the circuit
        """
        # Simple text-based circuit drawing
        lines = []
        for q in range(self.num_qubits):
            line = [f"q{q}:"]
            for gate, qubits in self.gates:
                if q in qubits:
                    if isinstance(qubits, (list, tuple)) and len(qubits) > 1:
                        # Multi-qubit gate
                        if q == qubits[0]:  # Control qubit
                            line.append(f"{gate.name.upper()}")
                        else:  # Target qubit(s)
                            line.append(" |")
                    else:
                        # Single-qubit gate
                        line.append(f"{gate.name.upper()}")
                else:
                    line.append("-" * 3)
            lines.append(" ".join(line))
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        """String representation of the quantum circuit."""
        return f"QuantumCircuit({self.num_qubits} qubits, {self.num_classical_bits} classical bits, {len(self.gates)} gates)"
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return self.__str__()
