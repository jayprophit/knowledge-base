"""
Tests for the Universe class.
"""

import pytest
import numpy as np
from src.multidisciplinary_ai.cosmology import Universe, CosmicStructure, CosmicStructureType

@pytest.fixture
def empty_universe():
    ""Create an empty universe for testing."""
    return Universe(box_size=100.0, h=0.7, omega_m=0.3, omega_lambda=0.7)

@pytest.fixture
def populated_universe(empty_universe):
    ""Create a universe with test structures."""
    universe = empty_universe
    
    # Add some test structures
    galaxy = CosmicStructure(
        structure_id="galaxy_1",
        structure_type=CosmicStructureType.GALAXY,
        position=(10.0, 10.0, 10.0),
        velocity=(0.0, 0.0, 0.0),
        mass=1e12,  # 10^12 solar masses
        radius=30.0,  # 30 kpc
        properties={"morphology": "spiral", "metallicity": 0.02}
    )
    
    star_cluster = CosmicStructure(
        structure_id="cluster_1",
        structure_type=CosmicStructureType.STAR_CLUSTER,
        position=(15.0, 15.0, 15.0),
        velocity=(100.0, 0.0, 0.0),  # 100 km/s
        mass=1e5,  # 10^5 solar masses
        radius=10.0,  # 10 pc
        properties={"age_gyr": 0.1, "metallicity": 0.008}
    )
    
    universe.add_structure(galaxy)
    universe.add_structure(star_cluster)
    
    return universe

def test_universe_initialization(empty_universe):
    ""Test universe initialization."""
    assert empty_universe.box_size == 100.0
    assert empty_universe.h == 0.7
    assert empty_universe.omega_m == 0.3
    assert empty_universe.omega_lambda == 0.7
    assert empty_universe.current_time == 0.0
    assert len(empty_universe.structures) == 0

def test_add_remove_structure(empty_universe):
    ""Test adding and removing structures."""
    # Create a test structure
    galaxy = CosmicStructure(
        structure_id="test_galaxy",
        structure_type=CosmicStructureType.GALAXY,
        position=(0.0, 0.0, 0.0),
        velocity=(0.0, 0.0, 0.0),
        mass=1e10,
        radius=10.0
    )
    
    # Add structure
    empty_universe.add_structure(galaxy)
    assert len(empty_universe.structures) == 1
    assert "test_galaxy" in empty_universe.structures
    
    # Remove structure
    result = empty_universe.remove_structure("test_galaxy")
    assert result is True
    assert len(empty_universe.structures) == 0
    
    # Try to remove non-existent structure
    result = empty_universe.remove_structure("nonexistent")
    assert result is False

def test_update_universe(populated_universe):
    ""Test updating the universe simulation."""
    # Get initial positions
    initial_positions = {}
    for struct_id, struct in populated_universe.structures.items():
        initial_positions[struct_id] = np.array(struct.position)
    
    # Update the universe
    dt = 0.01  # 10 Myr
    populated_universe.update(time_step=dt)
    
    # Check that time has advanced
    assert populated_universe.current_time == dt
    
    # Check that structures have moved
    for struct_id, struct in populated_universe.structures.items():
        if struct_id == "cluster_1":
            # Star cluster should have moved due to its velocity
            new_pos = np.array(struct.position)
            expected_pos = initial_positions[struct_id] + np.array([100.0, 0.0, 0.0]) * dt
            assert np.allclose(new_pos, expected_pos, rtol=1e-6)

def test_find_structures_in_volume(populated_universe):
    ""Test finding structures within a volume."""
    # Search near the galaxy
    center = (10.0, 10.0, 10.0)
    radius = 5.0  # Mpc
    
    found = populated_universe.find_structures_in_volume(center, radius)
    assert len(found) == 1
    assert found[0].structure_id == "galaxy_1"
    
    # Increase search radius to find both structures
    radius = 10.0  # Mpc
    found = populated_universe.find_structures_in_volume(center, radius)
    assert len(found) == 2
    assert {s.structure_id for s in found} == {"galaxy_1", "cluster_1"}
    
    # Search in empty region
    center = (90.0, 90.0, 90.0)
    found = populated_universe.find_structures_in_volume(center, 5.0)
    assert len(found) == 0

def test_get_cosmic_web(populated_universe):
    ""Test cosmic web analysis."""
    resolution = 10
    cosmic_web = populated_universe.get_cosmic_web(resolution=resolution)
    
    # Check output structure
    assert 'density_field' in cosmic_web
    assert 'power_spectrum' in cosmic_web
    assert 'resolution' in cosmic_web
    assert 'cell_size' in cosmic_web
    
    # Check dimensions
    density_field = cosmic_web['density_field']
    assert len(density_field) == resolution
    assert len(density_field[0]) == resolution
    assert len(density_field[0][0]) == resolution
    
    # Check that the galaxy is in the correct cell
    cell_size = populated_universe.box_size / resolution
    galaxy = populated_universe.structures["galaxy_1"]
    i, j, k = [int(p / cell_size) for p in galaxy.position]
    assert density_field[i][j][k] > 0
    
    # Check power spectrum
    power_spectrum = cosmic_web['power_spectrum']
    assert len(power_spectrum) > 0
    assert all(p >= 0 for p in power_spectrum)

def test_short_lived_structures(empty_universe):
    ""Test cleanup of short-lived structures."""
    # Add a supernova
    supernova = CosmicStructure(
        structure_id="supernova_1",
        structure_type=CosmicStructureType.SUPERNOVA,
        position=(50.0, 50.0, 50.0),
        velocity=(0.0, 0.0, 0.0),
        mass=1.4,  # 1.4 solar masses (Chandrasekhar mass)
        radius=0.01,  # 10 km
        properties={"peak_luminosity": 1e10, "explosion_energy": 1e51}
    )
    
    empty_universe.add_structure(supernova)
    assert "supernova_1" in empty_universe.structures
    
    # Update for a short time - supernova should still exist
    empty_universe.update(time_step=0.001)  # 1 Myr
    assert "supernova_1" in empty_universe.structures
    
    # Update for longer - supernova should be removed
    empty_universe.update(time_step=0.1)  # 100 Myr
    assert "supernova_1" not in empty_universe.structures

def test_periodic_boundary_conditions(empty_universe):
    ""Test that structures wrap around periodic boundaries."""
    # Add a structure near the edge
    edge_galaxy = CosmicStructure(
        structure_id="edge_galaxy",
        structure_type=CosmicStructureType.GALAXY,
        position=(95.0, 5.0, 5.0),  # Near the +x edge
        velocity=(1000.0, 0.0, 0.0),  # Moving outward
        mass=1e11,
        radius=20.0
    )
    
    empty_universe.add_structure(edge_galaxy)
    
    # Update for a short time - galaxy should move past the boundary
    empty_universe.update(time_step=0.01)  # 10 Myr
    
    # Position should have wrapped around to the other side
    new_pos = empty_universe.structures["edge_galaxy"].position[0]
    assert 0 <= new_pos < 100.0  # Within bounds
    assert new_pos < 5.0  # Should have wrapped around
"""