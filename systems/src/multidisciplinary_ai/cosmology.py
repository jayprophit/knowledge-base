"""
Cosmology Module
===============

Integrates cosmological models, astrophysics simulations, and time-space modeling into the multidisciplinary AI system.

This module provides a high-level interface for simulating cosmic phenomena, analyzing large-scale structure, and integrating cosmological principles with other scientific domains (psychology, philosophy, sociology, biology).
"""

from .cosmology.cosmology_model import CosmologyModel

class CosmologyModule:
    """
    High-level interface for cosmological simulation and integration.
    """
    def __init__(self, h=0.7, omega_m=0.3, omega_lambda=0.7):
        self.model = CosmologyModel(h=h, omega_m=omega_m, omega_lambda=omega_lambda)

    def simulate_gravity(self, m1, m2, distance):
        """
        Simulate gravitational attraction between two masses (simplified Newtonian).
        Args:
            m1: Mass 1 (kg)
            m2: Mass 2 (kg)
            distance: Distance between masses (meters)
        Returns:
            Gravitational force (Newtons)
        """
        G = 6.67430e-11
        return G * (m1 * m2) / (distance ** 2)

    def cosmic_distance(self, z):
        """
        Calculate comoving, angular diameter, and luminosity distances for a given redshift.
        """
        return {
            'comoving_distance': self.model.comoving_distance(z),
            'angular_diameter_distance': self.model.angular_diameter_distance(z),
            'luminosity_distance': self.model.luminosity_distance(z)
        }

    def universe_age(self, z=0.0):
        """
        Get the age of the universe at a given redshift.
        """
        return self.model.age_of_universe(z)

    def simulate_cosmic_evolution(self, z_start, z_end):
        """
        Simulate cosmic evolution between two redshifts (returns growth factor, density evolution).
        """
        return {
            'growth_factor': self.model.growth_factor(z_end),
            'matter_density': self.model.matter_density(z_end),
            'dark_energy_density': self.model.dark_energy_density(z_end)
        }
