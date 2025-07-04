""
Tests for the CosmologyModel class.
"""

import pytest
import numpy as np
from src.multidisciplinary_ai.cosmology import CosmologyModel

# Test cases for different cosmologies
COSMOLOGIES = [
    # (h, omega_m, omega_lambda, description)
    (0.7, 0.3, 0.7, "Flat ΛCDM"),
    (0.7, 1.0, 0.0, "Einstein-de Sitter"),
    (0.7, 0.3, 0.0, "Open universe"),
]

@pytest.mark.parametrize("h, omega_m, omega_lambda, desc", COSMOLOGIES)
def test_cosmology_initialization(h, omega_m, omega_lambda, desc):
    """Test initialization of different cosmologies."""
    cosmo = CosmologyModel(h=h, omega_m=omega_m, omega_lambda=omega_lambda)
    
    # Check parameters are set correctly
    assert cosmo.h == h
    assert cosmo.omega_m == omega_m
    assert cosmo.omega_lambda == omega_lambda
    
    # Check derived parameters
    assert cosmo.omega_k == pytest.approx(1.0 - omega_m - omega_lambda)
    assert cosmo.H0 == pytest.approx(100.0 * h)
    assert cosmo.DH == pytest.approx(cosmo.c / cosmo.H0)

@pytest.mark.parametrize("z, expected_hz_ratio", [
    (0.0, 1.0),  # At z=0, H(z) = H0
    (1.0, 1.84),  # Approximate value for ΛCDM
    (2.0, 2.96),  # Approximate value for ΛCDM
])
def test_hubble_parameter(z, expected_hz_ratio):
    ""Test Hubble parameter calculation."""
    cosmo = CosmologyModel()  # Default ΛCDM
    hz = cosmo.hubble_parameter(z)
    hz_ratio = hz / cosmo.H0
    
    # Check against expected values (with 5% tolerance)
    assert hz_ratio == pytest.approx(expected_hz_ratio, rel=0.05)

def test_distance_measures():
    ""Test consistency between different distance measures."""
    cosmo = CosmologyModel()
    z = 1.0
    
    # Calculate distances
    dc = cosmo.comoving_distance(z)
    da = cosmo.angular_diameter_distance(z)
    dl = cosmo.luminosity_distance(z)
    
    # Check distance duality relations
    assert da == pytest.approx(dc / (1.0 + z))
    assert dl == pytest.approx(dc * (1.0 + z))
    assert dl == pytest.approx(da * (1.0 + z) ** 2)

@pytest.mark.parametrize("z, expected_age", [
    (0.0, 13.8),  # Approximate age of the universe in Gyr
    (1.0, 5.9),   # Approximate age at z=1 in Gyr
    (2.0, 3.3),   # Approximate age at z=2 in Gyr
], ids=["z=0", "z=1", "z=2"])
def test_age_of_universe(z, expected_age):
    ""Test age of universe calculation."""
    cosmo = CosmologyModel()
    age = cosmo.age_of_universe(z)
    
    # Check against expected values (with 10% tolerance)
    assert age == pytest.approx(expected_age, rel=0.1)

def test_lookback_time():
    ""Test lookback time calculation."""
    cosmo = CosmologyModel()
    
    # Lookback time to z=0 should be 0
    assert cosmo.lookback_time(0.0) == pytest.approx(0.0)
    
    # Lookback time to z=∞ should be the age of the universe
    age = cosmo.age_of_universe(0.0)
    assert cosmo.lookback_time(1e6) == pytest.approx(age, rel=0.01)
    
    # Lookback time should be additive
    z1, z2 = 0.5, 1.0
    t1 = cosmo.lookback_time(z1)
    t2 = cosmo.lookback_time(z2)
    t_diff = cosmo.lookback_time(z2, z1)  # Lookback time between z1 and z2
    
    assert (t2 - t1) == pytest.approx(t_diff, rel=1e-3)

def test_critical_density():
    ""Test critical density calculation."""
    cosmo = CosmologyModel()
    
    # Critical density at z=0
    rho_crit = cosmo.critical_density(0.0)
    
    # Should be close to 2.77e11 h² M⊙/Mpc³
    expected = 2.77e11 * (cosmo.h ** 2)
    assert rho_crit == pytest.approx(expected, rel=0.1)
    
    # Critical density should increase with redshift
    rho_crit_z1 = cosmo.critical_density(1.0)
    assert rho_crit_z1 > rho_crit

def test_growth_factor():
    ""Test growth factor calculation."""
    cosmo = CosmologyModel()
    
    # Growth factor should be 1 at z=0
    assert cosmo.growth_factor(0.0) == pytest.approx(1.0)
    
    # Growth factor should decrease with redshift
    d1 = cosmo.growth_factor(1.0)
    d2 = cosmo.growth_factor(2.0)
    assert 0 < d2 < d1 < 1.0
    
    # Growth factor should be approximately proportional to 1/(1+z) at high z
    d10 = cosmo.growth_factor(10.0)
    d20 = cosmo.growth_factor(20.0)
    assert (d10 / d20) == pytest.approx(2.0, rel=0.1)

def test_comoving_volume():
    ""Test comoving volume calculation."""
    cosmo = CosmologyModel()
    
    # Volume should be approximately (4/3)πr³ for small volumes
    z = 0.01
    dc = cosmo.comoving_distance(z)
    expected_volume = (4.0/3.0) * np.pi * (dc ** 3)
    volume = cosmo.comoving_volume(0, z)
    
    assert volume == pytest.approx(expected_volume, rel=0.01)
    
    # Volume should increase with redshift
    vol1 = cosmo.comoving_volume(0, 0.1)
    vol2 = cosmo.comoving_volume(0, 0.2)
    assert vol2 > vol1

def test_sigma8():
    ""Test sigma8 calculation."""
    cosmo = CosmologyModel()
    
    # sigma8 should be between 0.7 and 0.9 for standard cosmologies
    sigma8 = cosmo.sigma8(0.0)
    assert 0.7 <= sigma8 <= 0.9
    
    # sigma8 should decrease with redshift
    s0 = cosmo.sigma8(0.0)
    s1 = cosmo.sigma8(1.0)
    s2 = cosmo.sigma8(2.0)
    
    assert s0 > s1 > s2
    
    # Ratio should be approximately equal to growth factor ratio
    d0 = cosmo.growth_factor(0.0)  # Should be 1.0
    d1 = cosmo.growth_factor(1.0)
    d2 = cosmo.growth_factor(2.0)
    
    assert (s1 / s0) == pytest.approx(d1 / d0, rel=0.1)
    assert (s2 / s0) == pytest.approx(d2 / d0, rel=0.1)
