"""
Cosmic Structure Module
======================

Defines the base class for all cosmic structures (galaxies, stars, etc.) and their properties.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import random
import math

class CosmicStructureType(Enum):
    """Types of cosmic structures."""
    STAR = "star"
    PLANET = "planet"
    GALAXY = "galaxy"
    NEBULA = "nebula"
    BLACK_HOLE = "black_hole"
    DARK_MATTER_HALO = "dark_matter_halo"
    GALAXY_CLUSTER = "galaxy_cluster"
    SUPERNOVA = "supernova"
    PULSAR = "pulsar"
    QUASAR = "quasar"

@dataclass
class CosmicStructure:
    """
    Base class representing a cosmic structure in the universe.
    
    Attributes:
        structure_id: Unique identifier for the structure
        structure_type: Type of cosmic structure
        position: 3D position in space (Mpc)
        velocity: 3D velocity vector (km/s)
        mass: Mass in solar masses
        radius: Radius in kpc
        age: Age in Gyr
        properties: Dictionary of type-specific properties
    """
    structure_id: str
    structure_type: CosmicStructureType
    position: Tuple[float, float, float]
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    mass: float = 0.0  # Solar masses
    radius: float = 0.0  # kpc
    age: float = 0.0  # Gyr
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def update(self, time_step: float, universe: 'Universe') -> None:
        """
        Update the structure's state based on physical laws.
        
        Args:
            time_step: Time step in Gyr
            universe: Reference to the parent universe for gravity calculations
        """
        # Apply gravitational forces from other structures
        total_force = np.zeros(3)
        
        for other in universe.structures.values():
            if other.structure_id == self.structure_id:
                continue
                
            # Calculate distance vector
            r = np.array(other.position) - np.array(self.position)
            distance = np.linalg.norm(r)
            
            # Skip if too close to avoid division by zero
            if distance < 1e-6:
                continue
            
            # Gravitational force (simplified)
            G = 4.30091e-3  # (km/s)^2 * kpc / M_sun
            force_mag = G * self.mass * other.mass / (distance**2 + 1e-6)
            force_dir = r / distance
            total_force += force_mag * force_dir
        
        # Update velocity (F = ma, a = F/m)
        acceleration = total_force / (self.mass + 1e-10)
        self.velocity = tuple(
            v + a * time_step * 0.98 
            for v, a in zip(self.velocity, acceleration)
        )
        
        # Update position
        self.position = tuple(
            p + v * time_step * 978.47  # Convert km/s to kpc/Gyr
            for p, v in zip(self.position, self.velocity)
        )
        
        # Update age
        self.age += time_step
        
        # Type-specific updates
        self._structure_specific_update(time_step, universe)
    
    def _structure_specific_update(self, time_step: float, universe: 'Universe') -> None:
        """Handle updates specific to different structure types."""
        if self.structure_type == CosmicStructureType.STAR:
            self._update_star(time_step, universe)
        elif self.structure_type == CosmicStructureType.GALAXY:
            self._update_galaxy(time_step, universe)
        elif self.structure_type == CosmicStructureType.BLACK_HOLE:
            self._update_black_hole(time_step, universe)
    
    def _update_star(self, time_step: float, universe: 'Universe') -> None:
        """Update star-specific properties."""
        if 'luminosity' not in self.properties:
            # Luminosity ~ Mass^3.5 (main sequence)
            self.properties['luminosity'] = (self.mass ** 3.5) * 3.846e26  # W
        
        # Simple stellar evolution
        if self.mass > 8.0 and self.age > 0.01:  # Massive stars
            self.properties['luminosity'] *= 1.0 + time_step * 0.1
        
        # Supernova condition
        if self.mass > 8.0 and self.age > (10.0 / (self.mass ** 0.8)):
            self._go_supernova(universe)
    
    def _update_galaxy(self, time_step: float, universe: 'Universe') -> None:
        """Update galaxy-specific properties."""
        if 'star_formation_rate' not in self.properties:
            self.properties['star_formation_rate'] = self.mass * 1e-10  # M_sun/yr
        
        # Star formation depends on gas content
        gas_mass = self.properties.get('gas_mass', self.mass * 0.1)
        if gas_mass > 1e6:  # Enough gas for star formation
            new_stars = self.properties['star_formation_rate'] * time_step * 1e9  # Gyr to yr
            gas_mass -= new_stars * 0.7  # 70% of mass forms stars, 30% returned
            self.properties['gas_mass'] = max(0, gas_mass)
            self.mass += new_stars * 0.7  # Only 70% of gas turns into stars
    
    def _go_supernova(self, universe: 'Universe') -> None:
        """Handle supernova event for massive stars."""
        # Create a supernova remnant (neutron star or black hole)
        remnant_mass = 1.4  # Chandrasekhar limit for white dwarf
        ejected_mass = self.mass - remnant_mass
        
        # Update self to be the remnant
        self.mass = remnant_mass
        self.radius = 10.0  # km for neutron star
        self.structure_type = (
            CosmicStructureType.BLACK_HOLE 
            if self.mass > 3.0  # Tolman-Oppenheimer-Volkoff limit
            else CosmicStructureType.PULSAR
        )
        
        # Create supernova explosion effect
        explosion = CosmicStructure(
            structure_id=f"snr_{random.randint(0, int(1e6))}",
            structure_type=CosmicStructureType.SUPERNOVA,
            position=self.position,
            velocity=self.velocity,
            mass=ejected_mass,
            radius=10.0,  # kpc
            properties={
                'explosion_energy': 1e44,  # J
                'remnant_id': self.structure_id
            }
        )
        
        # Add to universe
        universe.add_structure(explosion)
    
    def distance_to(self, other: 'CosmicStructure') -> float:
        """Calculate distance to another cosmic structure in Mpc."""
        return math.sqrt(
            (self.position[0] - other.position[0])**2 +
            (self.position[1] - other.position[1])**2 +
            (self.position[2] - other.position[2])**2
        )
