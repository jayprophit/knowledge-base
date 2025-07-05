"""
Cosmology Module
===============

This module provides tools for cosmological simulations and analysis, including:
- Cosmic structure modeling (galaxies, stars, dark matter halos)
"""

from .cosmology_model import CosmologyModel
from .cosmic_structure import CosmicStructure, CosmicStructureType
from .universe import Universe
from .cosmology_module import CosmologyModule

# Define the public API
__all__ = [
    'CosmologyModel',
    'CosmicStructure',
    'CosmicStructureType',
    'Universe',
    'CosmologyModule'
]

# Package version
__version__ = '0.1.0'
