"""
Cosmology Model
==============

Implements cosmological calculations and distance measures for a homogeneous,
expanding universe based on the ΛCDM model.
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CosmologyModel:
    """
    Implements cosmological calculations based on the ΛCDM model.
    
    This class provides methods for calculating distances, times, and other
    cosmological quantities in a flat or curved universe with dark energy.
    
    Attributes:
        h: Dimensionless Hubble parameter (H0 = 100h km/s/Mpc)
        omega_m: Matter density parameter
        omega_lambda: Dark energy density parameter
        omega_k: Curvature density parameter (1 - omega_m - omega_lambda)
        H0: Hubble constant in km/s/Mpc
        DH: Hubble distance in Mpc (c/H0)
    """
    
    def __init__(self, 
                h: float = 0.7, 
                omega_m: float = 0.3, 
                omega_lambda: float = 0.7):
        """
        Initialize the cosmology model.
        
        Args:
            h: Dimensionless Hubble parameter (H0 = 100h km/s/Mpc)
            omega_m: Matter density parameter
            omega_lambda: Dark energy density parameter
        """
        self.h = h
        self.omega_m = omega_m
        self.omega_lambda = omega_lambda
        self.omega_k = 1.0 - omega_m - omega_lambda  # Curvature density
        
        # Physical constants
        self.c = 2.99792458e5  # Speed of light in km/s
        self.H0 = 100.0 * h  # Hubble constant in km/s/Mpc
        self.DH = self.c / self.H0  # Hubble distance in Mpc
        self.G = 4.30091e-3  # Gravitational constant in (km/s)^2 * kpc/M_sun
    
    def hubble_parameter(self, z: float) -> float:
        """
        Calculate the Hubble parameter at redshift z.
        
        Args:
            z: Redshift
            
        Returns:
            Hubble parameter in km/s/Mpc
        """
        a = 1.0 / (1.0 + z)  # Scale factor
        return self.H0 * np.sqrt(
            self.omega_m * (a ** -3) + 
            self.omega_k * (a ** -2) + 
            self.omega_lambda
        )
    
    def comoving_distance(self, z: float, n_steps: int = 1000) -> float:
        """
        Calculate the line-of-sight comoving distance to redshift z.
        
        Args:
            z: Redshift
            n_steps: Number of integration steps
            
        Returns:
            Comoving distance in Mpc
        """
        def integrand(z_prime):
            return self.c / self.hubble_parameter(z_prime)
        
        # Numerical integration using trapezoidal rule
        z_vals = np.linspace(0, z, n_steps)
        integrand_vals = [integrand(z_val) for z_val in z_vals]
        return np.trapz(integrand_vals, z_vals)
    
    def angular_diameter_distance(self, z: float) -> float:
        """
        Calculate the angular diameter distance to redshift z.
        
        Args:
            z: Redshift
            
        Returns:
            Angular diameter distance in Mpc
        """
        dc = self.comoving_distance(z)
        if self.omega_k == 0:
            return dc / (1.0 + z)
        elif self.omega_k > 0:
            return (self.DH / np.sqrt(self.omega_k)) * np.sinh(np.sqrt(self.omega_k) * dc / self.DH) / (1.0 + z)
        else:
            return (self.DH / np.sqrt(-self.omega_k)) * np.sin(np.sqrt(-self.omega_k) * dc / self.DH) / (1.0 + z)
    
    def luminosity_distance(self, z: float) -> float:
        """
        Calculate the luminosity distance to redshift z.
        
        Args:
            z: Redshift
            
        Returns:
            Luminosity distance in Mpc
        """
        dc = self.comoving_distance(z)
        if self.omega_k == 0:
            return dc * (1.0 + z)
        elif self.omega_k > 0:
            return (self.DH / np.sqrt(self.omega_k)) * np.sinh(np.sqrt(self.omega_k) * dc / self.DH) * (1.0 + z)
        else:
            return (self.DH / np.sqrt(-self.omega_k)) * np.sin(np.sqrt(-self.omega_k) * dc / self.DH) * (1.0 + z)
    
    def lookback_time(self, z: float, n_steps: int = 1000) -> float:
        """
        Calculate the lookback time to redshift z.
        
        Args:
            z: Redshift
            n_steps: Number of integration steps
            
        Returns:
            Lookback time in Gyr
        """
        def integrand(a):
            return 1.0 / (a * self.hubble_parameter(1.0/a - 1.0))
        
        a_vals = np.linspace(1.0/(1.0 + z), 1.0, n_steps)
        integrand_vals = [integrand(a) for a in a_vals]
        
        # Convert from s to Gyr
        return (np.trapz(integrand_vals, a_vals) / (self.H0 * 1e3)) / 3.08567758e19 * 3.16880878e-8
    
    def age_of_universe(self, z: float = 0.0, n_steps: int = 1000) -> float:
        """
        Calculate the age of the universe at redshift z.
        
        Args:
            z: Redshift (default: 0 for current age)
            n_steps: Number of integration steps
            
        Returns:
            Age in Gyr
        """
        return self.lookback_time(float('inf'), n_steps) - self.lookback_time(z, n_steps)
    
    def critical_density(self, z: float = 0.0) -> float:
        """
        Calculate the critical density of the universe at redshift z.
        
        Args:
            z: Redshift
            
        Returns:
            Critical density in M_sun/Mpc^3
        """
        H = self.hubble_parameter(z)  # km/s/Mpc
        rho_crit = (3.0 * (H * 1e3 / 3.08567758e19)**2) / (8.0 * np.pi * 6.67430e-11)  # kg/m^3
        return rho_crit * 5.02785e-31  # Convert to M_sun/Mpc^3
    
    def matter_density(self, z: float = 0.0) -> float:
        """
        Calculate the matter density at redshift z.
        
        Args:
            z: Redshift
            
        Returns:
            Matter density in M_sun/Mpc^3
        """
        return self.omega_m * (1.0 + z)**3 * self.critical_density(z)
    
    def dark_energy_density(self, z: float = 0.0) -> float:
        """
        Calculate the dark energy density at redshift z.
        
        Args:
            z: Redshift
            
        Returns:
            Dark energy density in M_sun/Mpc^3
        """
        return self.omega_lambda * self.critical_density(z)
    
    def growth_factor(self, z: float, n_steps: int = 1000) -> float:
        """
        Calculate the linear growth factor at redshift z.
        
        The growth factor describes how density perturbations grow over time.
        
        Args:
            z: Redshift
            n_steps: Number of integration steps
            
        Returns:
            Growth factor (normalized to 1 at z=0)
        """
        def integrand(a):
            H = self.hubble_parameter(1.0/a - 1.0)
            return (a * H / self.H0) ** -3
        
        a_vals = np.linspace(0, 1.0/(1.0 + z), n_steps)
        integrand_vals = [integrand(a) for a in a_vals[1:]]  # Skip a=0 to avoid division by zero
        
        # Calculate growth factor (unnormalized)
        D = np.trapz(integrand_vals, a_vals[1:]) * 2.5 * self.omega_m * self.H0**2 / a_vals[-1]**3
        
        # Normalize to 1 at z=0
        if z > 0:
            D0 = self.growth_factor(0.0, n_steps)
            return D / D0
        return D
    
    def sigma8(self, z: float = 0.0, n_steps: int = 1000) -> float:
        """
        Calculate σ₈, the RMS mass fluctuation in 8 Mpc/h spheres at redshift z.
        
        Args:
            z: Redshift
            n_steps: Number of integration steps
            
        Returns:
            σ₈ value
        """
        # This is a simplified approximation
        # A full calculation would involve integrating the power spectrum
        growth = self.growth_factor(z, n_steps)
        sigma8_0 = 0.8  # Typical value at z=0
        return sigma8_0 * growth
    
    def comoving_volume(self, z_min: float, z_max: float) -> float:
        """
        Calculate the comoving volume between two redshifts.
        
        Args:
            z_min: Minimum redshift
            z_max: Maximum redshift
            
        Returns:
            Comoving volume in (Mpc/h)³
        """
        def integrand(z):
            dc = self.comoving_distance(z)
            da = self.angular_diameter_distance(z)
            return dc**2 / (np.sqrt(self.omega_m * (1.0 + z)**3 + self.omega_k * (1.0 + z)**2 + self.omega_lambda))
        
        # Numerical integration
        z_vals = np.linspace(z_min, z_max, 1000)
        integrand_vals = [integrand(z) for z in z_vals]
        integral = np.trapz(integrand_vals, z_vals)
        
        # Volume element in (Mpc/h)³
        return 4.0 * np.pi * (self.DH**3) * integral
