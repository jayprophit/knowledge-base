"""
Cosmology Module
===============

Main interface for cosmological calculations and simulations.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np

from .cosmology_model import CosmologyModel
from .cosmic_structure import CosmicStructure, CosmicStructureType
from .universe import Universe

class CosmologyModule:
    """
    Main interface for cosmological calculations and simulations.
    
    This class provides a high-level API for performing cosmological
    calculations and running simulations of cosmic structure formation.
    """
    
    def __init__(self, 
                h: float = 0.7, 
                omega_m: float = 0.3, 
                omega_lambda: float = 0.7):
        """
        Initialize the cosmology module.
        
        Args:
            h: Dimensionless Hubble parameter (H0 = 100h km/s/Mpc)
            omega_m: Matter density parameter
            omega_lambda: Dark energy density parameter
        """
        self.model = CosmologyModel(h, omega_m, omega_lambda)
        self.simulations: Dict[str, Universe] = {}
    
    # ====================
    # Distance Calculations
    # ====================
    
    def calculate_distance(self, 
                         z: float, 
                         distance_type: str = 'luminosity') -> Dict[str, Any]:
        """
        Calculate a cosmological distance.
        
        Args:
            z: Redshift
            distance_type: Type of distance to calculate. Options are:
                         'luminosity', 'angular_diameter', 'comoving'
            
        Returns:
            Dictionary containing the distance and metadata
        """
        if distance_type == 'luminosity':
            distance = self.model.luminosity_distance(z)
        elif distance_type == 'angular_diameter':
            distance = self.model.angular_diameter_distance(z)
        elif distance_type == 'comoving':
            distance = self.model.comoving_distance(z)
        else:
            raise ValueError(f"Unknown distance type: {distance_type}")
        
        return {
            'distance': distance,
            'unit': 'Mpc',
            'type': distance_type,
            'redshift': z,
            'cosmology': {
                'h': self.model.h,
                'omega_m': self.model.omega_m,
                'omega_lambda': self.model.omega_lambda
            }
        }
    
    # ==================
    # Time Calculations
    # ==================
    
    def calculate_lookback_time(self, z: float) -> Dict[str, Any]:
        """
        Calculate the lookback time to redshift z.
        
        Args:
            z: Redshift
            
        Returns:
            Dictionary containing the lookback time and metadata
        """
        lookback_time = self.model.lookback_time(z)
        
        return {
            'lookback_time': lookback_time,
            'unit': 'Gyr',
            'redshift': z,
            'cosmology': {
                'h': self.model.h,
                'omega_m': self.model.omega_m,
                'omega_lambda': self.model.omega_lambda
            }
        }
    
    def calculate_age_of_universe(self, z: float = 0.0) -> Dict[str, Any]:
        """
        Calculate the age of the universe at redshift z.
        
        Args:
            z: Redshift (default: 0 for current age)
            
        Returns:
            Dictionary containing the age and metadata
        """
        age = self.model.age_of_universe(z)
        
        return {
            'age': age,
            'unit': 'Gyr',
            'redshift': z,
            'cosmology': {
                'h': self.model.h,
                'omega_m': self.model.omega_m,
                'omega_lambda': self.model.omega_lambda
            }
        }
    
    # ====================
    # Simulation Management
    # ====================
    
    def create_simulation(self, 
                         sim_id: str, 
                         box_size: float = 100.0,
                         h: Optional[float] = None,
                         omega_m: Optional[float] = None,
                         omega_lambda: Optional[float] = None) -> Dict[str, Any]:
        """
        Create a new cosmological simulation.
        
        Args:
            sim_id: Unique identifier for the simulation
            box_size: Size of the simulation box in Mpc
            h: Hubble parameter (uses model default if None)
            omega_m: Matter density (uses model default if None)
            omega_lambda: Dark energy density (uses model default if None)
            
        Returns:
            Status of the operation
        """
        if sim_id in self.simulations:
            return {
                'status': 'error',
                'message': f'Simulation {sim_id} already exists'
            }
        
        # Use provided parameters or fall back to model defaults
        h = h if h is not None else self.model.h
        omega_m = omega_m if omega_m is not None else self.model.omega_m
        omega_lambda = omega_lambda if omega_lambda is not None else self.model.omega_lambda
        
        # Create a new universe with the specified parameters
        universe = Universe(
            box_size=box_size,
            h=h,
            omega_m=omega_m,
            omega_lambda=omega_lambda
        )
        
        # Store the simulation
        self.simulations[sim_id] = universe
        
        return {
            'status': 'success',
            'simulation_id': sim_id,
            'box_size': box_size,
            'parameters': {
                'h': h,
                'omega_m': omega_m,
                'omega_lambda': omega_lambda
            }
        }
    
    def run_simulation(self, 
                      sim_id: str, 
                      time_step: float = 0.01,
                      n_steps: int = 100) -> Dict[str, Any]:
        """
        Run a cosmological simulation.
        
        Args:
            sim_id: ID of the simulation to run
            time_step: Time step in Gyr
            n_steps: Number of time steps to simulate
            
        Returns:
            Simulation results
        """
        if sim_id not in self.simulations:
            return {
                'status': 'error',
                'message': f'Simulation {sim_id} not found'
            }
        
        universe = self.simulations[sim_id]
        
        # Run the simulation
        for _ in range(n_steps):
            universe.update(time_step)
        
        # Get some statistics
        n_structures = len(universe.structures)
        galaxy_count = sum(1 for s in universe.structures.values() 
                          if s.structure_type == CosmicStructureType.GALAXY)
        
        return {
            'status': 'success',
            'simulation_id': sim_id,
            'current_time': universe.current_time,
            'n_structures': n_structures,
            'n_galaxies': galaxy_count,
            'box_size': universe.box_size,
            'time_elapsed': n_steps * time_step
        }
    
    def get_simulation_state(self, sim_id: str) -> Dict[str, Any]:
        """
        Get the current state of a simulation.
        
        Args:
            sim_id: ID of the simulation
            
        Returns:
            Simulation state
        """
        if sim_id not in self.simulations:
            return {
                'status': 'error',
                'message': f'Simulation {sim_id} not found'
            }
        
        universe = self.simulations[sim_id]
        
        # Count different types of structures
        type_counts = {}
        for structure in universe.structures.values():
            type_name = structure.structure_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            'status': 'success',
            'simulation_id': sim_id,
            'current_time': universe.current_time,
            'n_structures': len(universe.structures),
            'structure_counts': type_counts,
            'box_size': universe.box_size,
            'parameters': {
                'h': universe.h,
                'omega_m': universe.omega_m,
                'omega_lambda': universe.omega_lambda
            }
        }
    
    # ====================
    # Structure Analysis
    # ====================
    
    def analyze_cosmic_web(self, 
                          sim_id: str, 
                          resolution: int = 50) -> Dict[str, Any]:
        """
        Analyze the cosmic web structure in a simulation.
        
        Args:
            sim_id: ID of the simulation
            resolution: Resolution of the density field
            
        Returns:
            Analysis results
        """
        if sim_id not in self.simulations:
            return {
                'status': 'error',
                'message': f'Simulation {sim_id} not found'
            }
        
        universe = self.simulations[sim_id]
        cosmic_web = universe.get_cosmic_web(resolution)
        
        return {
            'status': 'success',
            'simulation_id': sim_id,
            'cosmic_web': {
                'resolution': resolution,
                'cell_size': cosmic_web['cell_size'],
                'density_range': {
                    'min': float(np.min(cosmic_web['density_field'])),
                    'max': float(np.max(cosmic_web['density_field'])),
                    'mean': float(np.mean(cosmic_web['density_field']))
                },
                'power_spectrum': {
                    'k': np.linspace(0.1, 10, len(cosmic_web['power_spectrum'])).tolist(),
                    'Pk': cosmic_web['power_spectrum'].tolist()
                }
            }
        }
    
    def find_structures(self, 
                       sim_id: str, 
                       center: Tuple[float, float, float],
                       radius: float) -> Dict[str, Any]:
        """
        Find structures within a spherical volume.
        
        Args:
            sim_id: ID of the simulation
            center: (x, y, z) coordinates of the volume center in Mpc
            radius: Radius of the volume in Mpc
            
        Returns:
            List of structures within the volume
        """
        if sim_id not in self.simulations:
            return {
                'status': 'error',
                'message': f'Simulation {sim_id} not found'
            }
        
        universe = self.simulations[sim_id]
        structures = universe.find_structures_in_volume(center, radius)
        
        # Convert structures to a serializable format
        result = []
        for s in structures:
            result.append({
                'id': s.structure_id,
                'type': s.structure_type.value,
                'position': s.position,
                'mass': s.mass,
                'radius': s.radius,
                'age': s.age,
                'properties': s.properties
            })
        
        return {
            'status': 'success',
            'simulation_id': sim_id,
            'n_structures': len(result),
            'structures': result,
            'search_volume': {
                'center': center,
                'radius': radius,
                'volume': (4.0/3.0) * np.pi * (radius ** 3)
            }
        }
