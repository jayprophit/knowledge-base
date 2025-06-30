"""
Test suite for Quantum Circuit Optimization
"""
import unittest
import numpy as np
from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit import Parameter
from pathlib import Path
import sys

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from quantum_optimizer import CircuitOptimizer, analyze_circuit

class TestCircuitAnalysis(unittest.TestCase):
    """Test cases for circuit analysis functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simple_circuit = QuantumCircuit(2)
        self.simple_circuit.h(0)
        self.simple_circuit.cx(0, 1)
        
        self.parameterized_circuit = QuantumCircuit(2)
        theta = Parameter('θ')
        self.parameterized_circuit.rx(theta, 0)
        self.parameterized_circuit.ry(theta, 1)
        self.parameterized_circuit.cx(0, 1)
    
    def test_analyze_circuit_simple(self):
        """Test analysis of a simple circuit."""
        metrics = analyze_circuit(self.simple_circuit)
        self.assertEqual(metrics['num_qubits'], 2)
        self.assertEqual(metrics['depth'], 2)
        self.assertEqual(metrics['gate_counts'], {'h': 1, 'cx': 1})
        self.assertTrue(metrics['is_entangled'])
    
    def test_analyze_parameterized_circuit(self):
        """Test analysis of a parameterized circuit."""
        metrics = analyze_circuit(self.parameterized_circuit)
        self.assertEqual(metrics['num_parameters'], 1)
        self.assertEqual(metrics['depth'], 2)
        self.assertEqual(metrics['gate_counts'], {'rx': 1, 'ry': 1, 'cx': 1})


class TestCircuitOptimizer(unittest.TestCase):
    """Test cases for the CircuitOptimizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.num_qubits = 3
        self.optimizer = CircuitOptimizer(self.num_qubits)
        
        # Create a test circuit
        self.test_circuit = QuantumCircuit(self.num_qubits)
        self.test_circuit.h(range(self.num_qubits))
        for i in range(self.num_qubits - 1):
            self.test_circuit.cx(i, i + 1)
    
    def test_optimizer_initialization(self):
        """Test that the optimizer initializes correctly."""
        self.assertEqual(self.optimizer.num_qubits, self.num_qubits)
        self.assertIsNotNone(self.optimizer.model)
    
    def test_optimization_results(self):
        """Test that optimization produces valid results."""
        original_metrics = analyze_circuit(self.test_circuit)
        optimized_circuit = self.optimizer.optimize(self.test_circuit, iterations=5)
        
        # Verify the optimized circuit is still valid
        self.assertIsInstance(optimized_circuit, QuantumCircuit)
        self.assertEqual(optimized_circuit.num_qubits, self.num_qubits)
        
        # Verify optimization metrics
        optimized_metrics = analyze_circuit(optimized_circuit)
        self.assertLessEqual(optimized_metrics['depth'], original_metrics['depth'])
        
        # Verify the circuit still produces the same results (within tolerance)
        self._verify_circuit_equivalence(self.test_circuit, optimized_circuit)
    
    def _verify_circuit_equivalence(self, circ1: QuantumCircuit, circ2: QuantumCircuit, 
                                  tolerance: float = 1e-6):
        """Verify that two circuits produce the same output state."""
        backend = Aer.get_backend('statevector_simulator')
        
        # Get statevector for original circuit
        job1 = execute(circ1, backend)
        state1 = job1.result().get_statevector()
        
        # Get statevector for optimized circuit
        job2 = execute(circ2, backend)
        state2 = job2.result().get_statevector()
        
        # Verify the states are equivalent (up to global phase)
        inner_product = np.abs(np.vdot(state1, state2))
        self.assertAlmostEqual(inner_product, 1.0, delta=tolerance)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_invalid_circuit(self):
        """Test behavior with invalid circuit input."""
        optimizer = CircuitOptimizer(2)
        with self.assertRaises(ValueError):
            optimizer.optimize("not a quantum circuit")
    
    def test_empty_circuit(self):
        """Test behavior with empty circuit."""
        optimizer = CircuitOptimizer(2)
        empty_circuit = QuantumCircuit(2)
        optimized = optimizer.optimize(empty_circuit)
        self.assertEqual(analyze_circuit(optimized)['depth'], 0)


class TestPerformance(unittest.TestCase):
    """Performance testing for the optimizer."""
    
    def test_large_circuit_performance(self):
        """Test optimization performance on a larger circuit."""
        num_qubits = 5
        depth = 20
        
        # Create a larger test circuit
        circuit = QuantumCircuit(num_qubits)
        for _ in range(depth):
            # Add a layer of random single-qubit gates
            for q in range(num_qubits):
                circuit.rx(np.random.random() * 2 * np.pi, q)
                circuit.ry(np.random.random() * 2 * np.pi, q)
            
            # Add some entangling gates
            for q in range(0, num_qubits - 1, 2):
                circuit.cx(q, q + 1)
        
        # Test optimization time
        import time
        optimizer = CircuitOptimizer(num_qubits)
        
        start_time = time.time()
        optimized = optimizer.optimize(circuit, iterations=10)
        optimization_time = time.time() - start_time
        
        # Verify the optimization completed in a reasonable time
        self.assertLess(optimization_time, 10.0)  # Should complete in under 10 seconds
        
        # Verify the optimized circuit is valid
        self.assertIsInstance(optimized, QuantumCircuit)
        self.assertEqual(optimized.num_qubits, num_qubits)


if __name__ == '__main__':
    unittest.main()
