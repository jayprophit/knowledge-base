# Quantum Simulations

This directory contains quantum simulation code, including the implementation of the supersolid light simulation.

## Supersolid Light Simulation

### Overview
This module provides a numerical simulation of supersolid light behavior in a 2D quantum well structure. It models the dynamics of polaritons (light-matter quasiparticles) that exhibit both crystalline order and superfluid properties.

### Features
- **Split-step Fourier method** for efficient quantum evolution
- Visualization of both density and phase of the quantum wavefunction
- Customizable parameters for different experimental conditions
- Animated output showing the time evolution of the system

### Requirements
- Python 3.7+
- NumPy
- SciPy
- Matplotlib
- FFmpeg (for saving animations)

### Installation
```bash
pip install numpy scipy matplotlib
```

### Usage
Run the simulation:
```bash
python supersolid_simulation.py
```

### Parameters
You can modify these parameters in the `SupersolidLightSimulator` class:
- `size`: Grid size (default: 256)
- `dt`: Time step (default: 0.1)
- `hbar`: Reduced Planck constant (default: 1.0)
- `m`: Effective mass of polaritons (default: 1.0)

### Output
The simulation generates an animation showing:
1. **Density plot (left)**: Shows the probability density |ψ|²
2. **Phase plot (right)**: Shows the phase of the wavefunction

The animation is saved as `supersolid_light_simulation.mp4` in the current directory.

### Related Documentation
- [Supersolid Light Theory](../../resources/documentation/docs/quantum_physics/supersolid_light.md)
- [Quantum Computing Basics](../../resources/documentation/docs/quantum_computing/)

### References
1. [Nature Physics, March 2025]()
2. [Physical Review Letters, 2025]()
3. [Science Advances, 2025]()

### License
This project is licensed under the MIT License - see the LICENSE file for details.
