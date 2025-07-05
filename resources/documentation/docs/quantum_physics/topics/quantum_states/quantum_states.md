---
title: "Quantum States"
description: "Mathematical descriptions of quantum systems and their evolution"
date: 2025-07-05
weight: 230
tags:
  - quantum_physics
  - quantum_mechanics
  - state_vectors
  - density_matrices
  - quantum_information
---

# Quantum States

## Overview

Quantum states are mathematical descriptions of the state of a quantum system. They provide a complete description of the system's quantum mechanical properties and are fundamental to the formulation of quantum mechanics.

## Key Concepts

### Pure States

Represented by state vectors in a Hilbert space:

$$|\psi\rangle = \sum_i c_i |\phi_i\rangle$$

### Mixed States

Described by density matrices:

$$\rho = \sum_i p_i |\psi_i\rangle\langle\psi_i|$$

### Entangled States

Non-separable states that cannot be written as a tensor product:

$$|\psi\rangle_{AB} \neq |\phi\rangle_A \otimes |\chi\rangle_B$$

### Bell States

Maximally entangled two-qubit states:

$$|\Phi^\pm\rangle = \frac{1}{\sqrt{2}}(|00\rangle \pm |11\rangle)$$
$$|\Psi^\pm\rangle = \frac{1}{\sqrt{2}}(|01\rangle \pm |10\rangle)$$

## Types of Quantum States

### Fock States

Number states with definite particle number:

$$|n\rangle$$

### Coherent States

Quasi-classical states with minimum uncertainty:

$$|\alpha\rangle = e^{-|\alpha|^2/2} \sum_{n=0}^\infty \frac{\alpha^n}{\sqrt{n!}}|n\rangle$$

### Squeezed States

States with reduced quantum noise in one quadrature:

$$|\zeta\rangle = \hat{S}(\zeta)|0\rangle$$

### Cat States

Superposition of macroscopically distinct states:

$$|\text{cat}\rangle \propto |\alpha\rangle + |-\alpha\rangle$$

## Applications

- Quantum computing
- Quantum teleportation
- Quantum cryptography
- Quantum metrology
- Quantum simulation

## Current Research and Open Questions

- Topological quantum states
- Many-body localization
- Non-equilibrium quantum states
- Quantum phase transitions

## See Also

- [Quantum Entanglement](quantum_entanglement.md)
- [Quantum Information](quantum_information.md)
- [Quantum Measurement](quantum_measurement.md)

## References

1. von Neumann, J. (1932). Mathematical Foundations of Quantum Mechanics. Princeton University Press.
2. Peres, A. (1995). Quantum Theory: Concepts and Methods. Kluwer Academic.
3. Bengtsson, I., & Życzkowski, K. (2017). Geometry of Quantum States: An Introduction to Quantum Entanglement. Cambridge University Press.

## Further Reading

- Quantum Mechanics and Path Integrals by Richard P. Feynman and Albert R. Hibbs
- Quantum Theory: Concepts and Methods by Asher Peres
- Quantum Mechanics: Concepts and Applications by Nouredine Zettili
