"""
Multidisciplinary AI Integration Module
======================================

This module provides the core integration of multiple disciplines
into a cohesive AI system.
"""

from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass, asdict
import json

from .psychology import PsychologyModule
from .philosophy import PhilosophyModule
from .sociology import SociologyModule
from .biology import BiologyModule
from .cosmology import CosmologyModule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Structured response from the multidisciplinary AI system."""
    psychology: Dict[str, Any]
    philosophy: Dict[str, Any]
    sociology: Dict[str, Any]
    biology: Dict[str, Any]
    cosmology: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return asdict(self)
    
    def to_json(self, **kwargs) -> str:
        """Convert response to JSON string."""
        return json.dumps(self.to_dict(), **kwargs)

class MultidisciplinaryAI:
    """
    Main class for the multidisciplinary AI system that integrates
    knowledge from multiple disciplines.
    """
    
    def __init__(self, 
                 psychology_config: Optional[Dict] = None,
                 philosophy_config: Optional[Dict] = None,
                 sociology_config: Optional[Dict] = None,
                 biology_config: Optional[Dict] = None,
                 cosmology_config: Optional[Dict] = None):
        """
        Initialize the multidisciplinary AI system with optional configurations
        for each discipline module.
        
        Args:
            psychology_config: Configuration for the psychology module
            philosophy_config: Configuration for the philosophy module
            sociology_config: Configuration for the sociology module
            biology_config: Configuration for the biology module
            cosmology_config: Configuration for the cosmology module
        """
        self.psychology = PsychologyModule(**(psychology_config or {}))
        self.philosophy = PhilosophyModule(**(philosophy_config or {}))
        self.sociology = SociologyModule(**(sociology_config or {}))
        self.biology = BiologyModule(**(biology_config or {}))
        self.cosmology = CosmologyModule(**(cosmology_config or {}))
        
        logger.info("Multidisciplinary AI system initialized")
    
    def process_input(self, input_data: Dict[str, Any]) -> AIResponse:
        """
        Process input data through all discipline modules and return
        a comprehensive response.
        
        Args:
            input_data: Dictionary containing input data for each discipline.
                       Expected keys: 'psychology', 'philosophy', 'sociology',
                       'biology', 'cosmology'.
        
        Returns:
            AIResponse: Structured response containing outputs from all modules.
        """
        logger.info("Processing input through multidisciplinary AI system")
        
        # Process each discipline in parallel (in a real implementation)
        psych_result = self.psychology.analyze(input_data.get('psychology', {}))
        phil_result = self.philosophy.analyze(input_data.get('philosophy', {}))
        soc_result = self.sociology.analyze(input_data.get('sociology', {}))
        bio_result = self.biology.analyze(input_data.get('biology', {}))
        cosmo_result = self.cosmology.analyze(input_data.get('cosmology', {}))
        
        # Create and return integrated response
        return AIResponse(
            psychology=psych_result,
            philosophy=phil_result,
            sociology=soc_result,
            biology=bio_result,
            cosmology=cosmo_result
        )
    
    def __call__(self, input_data: Dict[str, Any]) -> AIResponse:
        """Alias for process_input to allow direct calling of the instance."""
        return self.process_input(input_data)
