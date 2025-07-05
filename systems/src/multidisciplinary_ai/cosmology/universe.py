"""
Universe Module
==============

Contains the Universe class that serves as the main container for cosmological
simulations, managing cosmic structures and their interactions.
"""

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import math
from .cosmic_structure import CosmicStructure, CosmicStructureType

class Universe:
    """
    Represents a simulated universe containing cosmic structures.
    
    The Universe class manages the collection of cosmic structures (galaxies, 
    stars, etc.) and handles their interactions over time.
    
    Attributes:
        box_size: Size of the simulation box in Mpc
        h: Dimensionless Hubble parameter (H0 = 100h km/s/Mpc)
        omega_m: Matter density parameter
        omega_lambda: Dark energy density parameter
        current_time: Current simulation time in Gyr
        structures: Dictionary of cosmic structures in the universe
    """
    
    def __init__(self, 
                box_size: float = 100.0,
                h: float = 0.7,
                omega_m: float = 0.3,
                omega_lambda: float = 0.7):
        """
        Initialize a new universe simulation.
        
        Args:
            box_size: Size of the simulation box in Mpc
            h: Dimensionless Hubble parameter (H0 = 100h km/s/Mpc)
            omega_m: Matter density parameter
            omega_lambda: Dark energy density parameter
        """
        self.box_size = box_size
        self.h = h
        self.omega_m = omega_m
        self.omega_lambda = omega_lambda
        self.current_time = 0.0  # Gyr
        self.structures: Dict[str, CosmicStructure] = {}
    
    def add_structure(self, structure: CosmicStructure) -> None:
        """
        Add a cosmic structure to the universe.
        
        Args:
            structure: The cosmic structure to add
        """
        self.structures[structure.structure_id] = structure
    
    def remove_structure(self, structure_id: str) -> bool:
        """
        Remove a cosmic structure from the universe.
        
        Args:
            structure_id: ID of the structure to remove
            
        Returns:
            True if the structure was found and removed, False otherwise
        """
        if structure_id in self.structures:
            del self.structures[structure_id]
            return True
        return False
    
    def update(self, time_step: float = 0.01) -> None:
        """
        Update the universe simulation by one time step.
        
        Args:
            time_step: Time step in Gyr
        """
        # Update all structures
        for structure in list(self.structures.values()):
            try:
                structure.update(time_step, self)
            except Exception as e:
                print(f"Error updating {structure.structure_id}: {e}")
        
        # Update cosmic time
        self.current_time += time_step
        
        # Clean up short-lived structures
        self._cleanup_short_lived_structures()
    
    def _cleanup_short_lived_structures(self) -> None:
        """Remove short-lived structures like supernovae."""
        to_remove = []
        for struct_id, structure in self.structures.items():
            if (structure.structure_type == CosmicStructureType.SUPERNOVA and 
                structure.age > 0.01):  # Supernovae last ~10,000 years
                to_remove.append(struct_id)
        
        for struct_id in to_remove:
            self.structures.pop(struct_id, None)
    
    def get_cosmic_web(self, resolution: int = 50) -> Dict[str, Any]:
        """
        Calculate the cosmic web structure using a density field.
        
        Args:
            resolution: Number of grid cells per dimension
            
        Returns:
            Dictionary containing the density field and other metrics
        """
        # Initialize density grid
        grid = np.zeros((resolution, resolution, resolution))
        cell_size = self.box_size / resolution
        
        # Assign masses to grid cells (cloud-in-cell interpolation)
        for structure in self.structures.values():
            if structure.structure_type in [CosmicStructureType.GALAXY, 
                                          CosmicStructureType.GALAXY_CLUSTER]:
                # Convert position to grid coordinates
                x, y, z = [int(p / cell_size) % resolution 
                          for p in structure.position]
                
                # Simple assignment (would use CIC in production)
                if (0 <= x < resolution and 
                    0 <= y < resolution and 
                    0 <= z < resolution):
                    grid[x, y, z] += structure.mass
        
        # Calculate power spectrum (simplified)
        power_spectrum = self._calculate_power_spectrum(grid)
        
        return {
            'density_field': grid.tolist(),
            'power_spectrum': power_spectrum.tolist(),
            'resolution': resolution,
            'cell_size': cell_size
        }
    
    def _calculate_power_spectrum(self, density_field: np.ndarray) -> np.ndarray:
        """
        Calculate the power spectrum of the density field.
        
        Args:
            density_field: 3D array of density values
            
        Returns:
            1D array representing the power spectrum
        """
        # Remove mean
        delta = (density_field - np.mean(density_field)) / np.mean(density_field)
        
        # FFT
        fft = np.fft.fftn(delta)
        power = np.abs(fft) ** 2
        
        # Radial average
        n = len(density_field)
        k_freq = np.fft.fftfreq(n) * 2 * np.pi / (self.box_size / n)
        k_freq_3d = np.meshgrid(k_freq, k_freq, k_freq, indexing='ij')
        k_mag = np.sqrt(sum(k**2 for k in k_freq_3d))
        
        # Bin the power spectrum
        k_bins = np.logspace(-2, 2, 20)
        k_centers = (k_bins[1:] + k_bins[:-1]) / 2
        power_spectrum = np.zeros_like(k_centers)
        
        for i in range(len(k_bins)-1):
            mask = (k_mag >= k_bins[i]) & (k_mag < k_bins[i+1])
            if np.any(mask):
                power_spectrum[i] = np.mean(power[mask])
        
        return power_spectrum
    
    def find_structures_in_volume(self, 
                                center: Tuple[float, float, float],
                                radius: float) -> List[CosmicStructure]:
        """
        Find all structures within a spherical volume.
        
        Args:
            center: (x, y, z) coordinates of the volume center in Mpc
            radius: Radius of the volume in Mpc
            
        Returns:
            List of structures within the volume
        """
        result = []
        cx, cy, cz = center
        
        for structure in self.structures.values():
            x, y, z = structure.position
            distance = math.sqrt((x-cx)**2 + (y-cy)**2 + (z-cz)**2)
            if distance <= radius:
                result.append(structure)
        
        return result
    
    def initialize_cosmology(self, 
                           initial_conditions: Dict[str, Any]) -> None:
        """
        Initialize the universe with specific cosmological conditions.
        
        Args:
            initial_conditions: Dictionary containing initial conditions
        """
        # Implementation would set up the initial distribution of matter
        # based on power spectrum, etc.
        pass
