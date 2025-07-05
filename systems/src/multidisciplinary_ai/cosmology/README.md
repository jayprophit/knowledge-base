---
title: Cosmology Documentation
description: Documentation and guides for the Cosmology module.
author: Knowledge Base Team
created_at: '2025-07-05'
updated_at: '2025-07-05'
version: 1.0.0
---

# Cosmology Module

This module provides tools for cosmological calculations and simulations, including distance measures, time evolution, and large-scale structure formation.

## Features

- **Cosmological Calculations**:
  - Distance measures (luminosity, angular diameter, comoving)
  - Time evolution (age of universe, lookback time)
  - Density parameters and growth factors

- **Simulation Capabilities**:
  - N-body simulation of cosmic structures
  - Cosmic web analysis
  - Structure formation and evolution

- **Pre-built Cosmological Models**:
  - Flat ΛCDM (default)
  - Custom parameter support

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/knowledge-base.git
cd knowledge-base

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from src.multidisciplinary_ai.cosmology import CosmologyModule

# Initialize with default ΛCDM parameters
cosmo = CosmologyModule()

# Calculate luminosity distance to redshift z=0.5
distance = cosmo.calculate_distance(0.5, 'luminosity')
print(f"Luminosity distance: {distance['distance']} Mpc")

# Calculate age of the universe at z=3
age = cosmo.calculate_age_of_universe(3.0)
print(f"Age at z=3: {age['age']} Gyr")
```

### Running a Simulation

```python
# Create a new simulation
sim_id = "my_simulation"
cosmo.create_simulation(sim_id, box_size=200.0)

# Run the simulation for 1 Gyr
result = cosmo.run_simulation(sim_id, time_step=0.01, n_steps=100):
print(f"Simulation complete. Current time: {result['current_time']} Gyr")

# Analyze the cosmic web
analysis = cosmo.analyze_cosmic_web(sim_id, resolution=50)
print(f"Density range: {analysis['cosmic_web']['density_range']}")
```

## API Reference

### `CosmologyModule`

Main class for cosmological calculations and simulations.

#### Methods

- `calculate_distance(z, distance_type='luminosity')`: Calculate cosmological distance
- `calculate_lookback_time(z)`: Calculate lookback time to redshift z
- `calculate_age_of_universe(z=0.0)`: Calculate age of the universe at redshift z
- `create_simulation(sim_id, box_size=100.0, **params)`: Create a new simulation
- `run_simulation(sim_id, time_step=0.01, n_steps=100)`: Run a simulation
- `get_simulation_state(sim_id)`: Get current state of a simulation
- `analyze_cosmic_web(sim_id, resolution=50)`: Analyze cosmic web structure
- `find_structures(sim_id, center, radius)`: Find structures in a volume

## Examples

### Plotting the Distance-Redshift Relation

```python
import matplotlib.pyplot as plt

# Initialize cosmology
cosmo = CosmologyModule()

# Calculate distances for a range of redshifts
redshifts = np.linspace(0, 5, 100)
distances = [cosmo.calculate_distance(z, 'luminosity')['distance'] for z in redshifts]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(redshifts, distances)
plt.xlabel('Redshift (z)')
plt.ylabel('Luminosity Distance (Mpc)')
plt.title('Distance-Redshift Relation')
plt.grid(True)
plt.show():
```

### Visualizing the Cosmic Web

```python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create and run a simulation
sim_id = "web_simulation"
cosmo.create_simulation(sim_id, box_size=100.0)
cosmo.run_simulation(sim_id, time_step=0.1, n_steps=10)

# Get galaxy positions
galaxies = [s for s in cosmo.simulations[sim_id].structures.values() 
            if s.structure_type == CosmicStructureType.GALAXY]
positions = np.array([g.position for g in galaxies])

# Plot 3D distribution
fig = plt.figure(figsize=(10, 8)):
ax = fig.add_subplot(111, projection='3d'):
ax.scatter(positions[:,0], positions[:,1], positions[:,2], s=1, alpha=0.5)
ax.set_xlabel('X (Mpc)')
ax.set_ylabel('Y (Mpc)')
ax.set_zlabel('Z (Mpc)')
ax.set_title('Galaxy Distribution in the Cosmic Web')
plt.show()
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## References

1. Hogg, D. W. (1999). "Distance measures in cosmology". arXiv:astro-ph/9905116
2. Peebles, P. J. E. (1993). Principles of Physical Cosmology. Princeton University Press
3. Mo, H., van den Bosch, F. C., & White, S. (2010). Galaxy Formation and Evolution. Cambridge University Press
