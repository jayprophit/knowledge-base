"""
Psychology Module
================

Implements psychological models for cognitive and emotional processing.
"""

from typing import Dict, Any, List, Optional
import random
import numpy as np
from dataclasses import dataclass
from enum import Enum, auto

class EmotionalState(Enum):
    """Basic emotional states based on the circumplex model."""
    JOY = auto()
    SADNESS = auto()
    ANGER = auto()
    FEAR = auto()
    SURPRISE = auto()
    DISGUST = auto()
    NEUTRAL = auto()

class PersonalityTrait(Enum):
    """Big Five personality traits."""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"

@dataclass
class CognitiveBias:
    """Represents a cognitive bias that can affect decision making."""
    name: str
    description: str
    impact: float  # -1.0 (negative) to 1.0 (positive)

class PsychologyModule:
    """
    Handles psychological aspects including emotions, personality, and cognitive processes.
    """
    
    def __init__(self, 
                 personality_profile: Optional[Dict[PersonalityTrait, float]] = None,
                 emotional_state: EmotionalState = EmotionalState.NEUTRAL,
                 cognitive_biases: Optional[List[CognitiveBias]] = None):
        """
        Initialize the psychology module with optional personality profile and biases.
        
        Args:
            personality_profile: Dictionary mapping personality traits to values (0.0 to 1.0)
            emotional_state: Initial emotional state
            cognitive_biases: List of cognitive biases to model
        """
        # Initialize with default personality profile if none provided
        self.personality = personality_profile or {
            PersonalityTrait.OPENNESS: 0.5,
            PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
            PersonalityTrait.EXTRAVERSION: 0.5,
            PersonalityTrait.AGREEABLENESS: 0.5,
            PersonalityTrait.NEUROTICISM: 0.5
        }
        
        self.emotional_state = emotional_state
        self.emotional_intensity = 0.5  # 0.0 to 1.0
        
        # Common cognitive biases
        self.cognitive_biases = cognitive_biases or [
            CognitiveBias("confirmation_bias", 
                         "Tendency to search for or interpret information in a way that confirms one's preconceptions", 
                         -0.3),
            CognitiveBias("optimism_bias", 
                         "Tendency to be over-optimistic about the outcome of planned actions", 
                         0.4),
            CognitiveBias("anchoring", 
                         "Relying too heavily on the first piece of information offered", 
                         -0.2)
        ]
        
        # Memory for emotional experiences
        self.memory = []
        self.mood_history = []
    
    def update_emotional_state(self, stimulus: Dict[str, float]) -> Dict[str, Any]:
        """
        Update emotional state based on stimulus.
        
        Args:
            stimulus: Dictionary with 'valence' (-1.0 to 1.0) and 'arousal' (0.0 to 1.0)
            
        Returns:
            Dict containing the new emotional state and intensity
        """
        valence = stimulus.get('valence', 0.0)
        arousal = stimulus.get('arousal', 0.5)
        
        # Simple emotion model based on valence and arousal
        if valence > 0.5 and arousal > 0.5:
            self.emotional_state = EmotionalState.JOY
        elif valence > 0.5 and arousal <= 0.5:
            self.emotional_state = EmotionalState.JOY  # Contentment
        elif valence < -0.5 and arousal > 0.5:
            self.emotional_state = EmotionalState.ANGER
        elif valence < -0.5 and arousal <= 0.5:
            self.emotional_state = EmotionalState.SADNESS
        elif arousal > 0.7:
            self.emotional_state = EmotionalState.SURPRISE
        else:
            self.emotional_state = EmotionalState.NEUTRAL
        
        # Update emotional intensity (dampened by neuroticism)
        neuroticism = self.personality[PersonalityTrait.NEUROTICISM]
        self.emotional_intensity = min(1.0, max(0.0, 
            arousal * (1.0 + neuroticism * 0.5)  # More neurotic = more intense emotions
        ))
        
        # Record in memory
        self.memory.append({
            'timestamp': len(self.memory),
            'stimulus': stimulus,
            'emotion': self.emotional_state.name,
            'intensity': self.emotional_intensity
        })
        
        return {
            'emotion': self.emotional_state.name,
            'intensity': self.emotional_intensity,
            'personality': {k.value: v for k, v in self.personality.items()}
        }
    
    def apply_cognitive_biases(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply cognitive biases to a decision.
        
        Args:
            decision: Dictionary containing decision information
            
        Returns:
            Modified decision with biases applied
        """
        biased_decision = decision.copy()
        
        for bias in self.cognitive_biases:
            # Apply each bias based on its impact
            if 'confidence' in biased_decision:
                biased_decision['confidence'] = max(0.0, min(1.0, 
                    biased_decision['confidence'] * (1.0 + bias.impact)
                ))
            
            # Add bias information to metadata
            if '_biases' not in biased_decision:
                biased_decision['_biases'] = []
            
            biased_decision['_biases'].append({
                'name': bias.name,
                'description': bias.description,
                'impact': bias.impact
            })
        
        return biased_decision
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method that processes psychological input data.
        
        Args:
            input_data: Dictionary containing 'stimulus' and optional 'decision'
            
        Returns:
            Analysis results including emotional state and cognitive processing
        """
        # Process emotional stimulus if present
        if 'stimulus' in input_data:
            emotion_result = self.update_emotional_state(input_data['stimulus'])
        else:
            emotion_result = {
                'emotion': self.emotional_state.name,
                'intensity': self.emotional_intensity,
                'personality': {k.value: v for k, v in self.personality.items()}
            }
        
        # Apply cognitive biases to decision if present
        result = {'emotion': emotion_result}
        
        if 'decision' in input_data:
            result['decision'] = self.apply_cognitive_biases(input_data['decision'])
        
        # Add cognitive load estimation
        result['cognitive_load'] = self.estimate_cognitive_load(input_data)
        
        return result
    
    def estimate_cognitive_load(self, input_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Estimate the cognitive load based on input complexity and current state.
        
        Args:
            input_data: Input data to analyze
            
        Returns:
            Dictionary with cognitive load metrics
        """
        # Simple heuristic for cognitive load
        complexity = len(str(input_data)) / 1000  # Rough measure of input size
        emotional_impact = self.emotional_intensity * 0.5  # Higher emotions increase load
        
        # Neuroticism makes cognitive load more volatile
        neuroticism = self.personality[PersonalityTrait.NEUROTICISM]
        volatility = random.random() * neuroticism * 0.2
        
        load = min(1.0, max(0.0, 
            complexity * (1.0 + emotional_impact) + volatility - 0.1
        ))
        
        return {
            'load': load,
            'complexity': complexity,
            'emotional_impact': emotional_impact,
            'volatility': volatility
        }
