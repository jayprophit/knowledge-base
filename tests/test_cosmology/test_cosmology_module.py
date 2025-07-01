"""
Tests for the CosmologyModule class.
"""

import pytest
import numpy as np
from src.multidisciplinary_ai.cosmology import CosmologyModule, CosmicStructure, CosmicStructureType

def test_cosmology_module_initialization():
    ""Test initialization of the CosmologyModule."""
    # Test with default parameters
    cosmo = CosmologyModule()
    assert cosmo.model.h == 0.7
    assert cosmo.model.omega_m == 0.3
    assert cosmo.model.omega_lambda == 0.7
    assert len(cosmo.simulations) == 0
    
    # Test with custom parameters
    cosmo_custom = CosmologyModule(h=0.68, omega_m=0.31, omega_lambda=0.69)
    assert cosmo_custom.model.h == 0.68
    assert cosmo_custom.model.omega_m == 0.31
    assert cosmo_custom.model.omega_lambda == 0.69

def test_calculate_distance():
    ""Test distance calculations."""
    cosmo = CosmologyModule()
    
    # Test luminosity distance
    result = cosmo.calculate_distance(0.5, 'luminosity')
    assert 'distance' in result
    assert result['type'] == 'luminosity'
    assert result['unit'] == 'Mpc'
    assert result['redshift'] == 0.5
    
    # Test angular diameter distance
    result = cosmo.calculate_distance(1.0, 'angular_diameter')
    assert 'distance' in result
    assert result['type'] == 'angular_diameter'
    
    # Test comoving distance
    result = cosmo.calculate_distance(2.0, 'comoving')
    assert 'distance' in result
    assert result['type'] == 'comoving'
    
    # Test invalid distance type
    with pytest.raises(ValueError):
        cosmo.calculate_distance(0.5, 'invalid_type')

def test_time_calculations():
    ""Test time-related calculations."""
    cosmo = CosmologyModule()
    
    # Test lookback time
    lookback = cosmo.calculate_lookback_time(1.0)
    assert 'lookback_time' in lookback
    assert lookback['unit'] == 'Gyr'
    assert lookback['redshift'] == 1.0
    
    # Test age of universe
    age = cosmo.calculate_age_of_universe(0.0)
    assert 'age' in age
    assert age['unit'] == 'Gyr'
    assert age['redshift'] == 0.0
    
    # Age should increase with redshift
    age_z1 = cosmo.calculate_age_of_universe(1.0)
    age_z2 = cosmo.calculate_age_of_universe(2.0)
    assert age_z1['age'] > age_z2['age']

def test_simulation_management():
    ""Test simulation creation and management."""
    cosmo = CosmologyModule()
    sim_id = "test_sim"
    
    # Create a new simulation
    result = cosmo.create_simulation(sim_id, box_size=200.0)
    assert result['status'] == 'success'
    assert result['simulation_id'] == sim_id
    assert result['box_size'] == 200.0
    assert sim_id in cosmo.simulations
    
    # Try to create duplicate simulation
    result = cosmo.create_simulation(sim_id)
    assert result['status'] == 'error'
    
    # Get simulation state
    state = cosmo.get_simulation_state(sim_id)
    assert state['status'] == 'success'
    assert state['simulation_id'] == sim_id
    assert state['n_structures'] == 0  # No structures added yet
    
    # Run simulation
    run_result = cosmo.run_simulation(sim_id, time_step=0.01, n_steps=10)
    assert run_result['status'] == 'success'
    assert run_result['simulation_id'] == sim_id
    assert run_result['time_elapsed'] == 0.1  # 0.01 * 10
    
    # Get updated state
    state = cosmo.get_simulation_state(sim_id)
    assert state['current_time'] == 0.1

def test_structure_analysis():
    ""Test structure analysis functions."""
    cosmo = CosmologyModule()
    sim_id = "analysis_test"
    
    # Create and run a simulation
    cosmo.create_simulation(sim_id, box_size=100.0)
    
    # Add some test structures
    universe = cosmo.simulations[sim_id]
    
    # Add a galaxy
    galaxy = CosmicStructure(
        structure_id="galaxy_1",
        structure_type=CosmicStructureType.GALAXY,
        position=(10.0, 10.0, 10.0),
        velocity=(0.0, 0.0, 0.0),
        mass=1e12,
        radius=30.0,
        properties={"morphology": "spiral"}
    )
    universe.add_structure(galaxy)
    
    # Add a star cluster
    cluster = CosmicStructure(
        structure_id="cluster_1",
        structure_type=CosmicStructureType.STAR_CLUSTER,
        position=(15.0, 15.0, 15.0),
        velocity=(100.0, 0.0, 0.0),
        mass=1e5,
        radius=10.0,
        properties={"age_gyr": 0.1}
    )
    universe.add_structure(cluster)
    
    # Test finding structures
    found = cosmo.find_structures(sim_id, (10.0, 10.0, 10.0), 10.0)
    assert found['status'] == 'success'
    assert found['n_structures'] == 2  # Both should be within 10 Mpc
    
    # Test cosmic web analysis
    analysis = cosmo.analyze_cosmic_web(sim_id, resolution=20)
    assert analysis['status'] == 'success'
    assert 'cosmic_web' in analysis
    assert 'density_range' in analysis['cosmic_web']
    assert 'power_spectrum' in analysis['cosmic_web']
    
    # Check that the galaxy is in the density field
    density_field = analysis['cosmic_web']['density_field']
    cell_size = 100.0 / 20  # box_size / resolution
    i, j, k = [int(10.0 / cell_size)] * 3  # Galaxy at (10, 10, 10)
    assert density_field[i][j][k] > 0  # Should have some density

def test_invalid_simulation_handling():
    ""Test handling of invalid simulation operations."""
    cosmo = CosmologyModule()
    
    # Try to get state of non-existent simulation
    state = cosmo.get_simulation_state("nonexistent")
    assert state['status'] == 'error'
    
    # Try to run non-existent simulation
    run_result = cosmo.run_simulation("nonexistent")
    assert run_result['status'] == 'error'
    
    # Try to analyze non-existent simulation
    analysis = cosmo.analyze_cosmic_web("nonexistent")
    assert analysis['status'] == 'error'
    
    # Try to find structures in non-existent simulation
    found = cosmo.find_structures("nonexistent", (0, 0, 0), 10.0)
    assert found['status'] == 'error'
