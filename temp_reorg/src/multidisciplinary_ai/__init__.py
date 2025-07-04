"""
Multidisciplinary AI System
==========================

An integrated AI system that combines knowledge from multiple disciplines
including psychology, philosophy, sociology, biology, and cosmology.
"""

from .psychology import PsychologyModule
from .philosophy import PhilosophyModule
from .sociology import SociologyModule
from .biology import BiologyModule
from .cosmology import CosmologyModule
from .integration import MultidisciplinaryAI

__version__ = '0.1.0'
__all__ = [
    'PsychologyModule',
    'PhilosophyModule',
    'SociologyModule',
    'BiologyModule',
    'CosmologyModule',
    'MultidisciplinaryAI'
]
