"""
Emotional Intelligence Integration System

Orchestrates and integrates all emotional intelligence components:
- Core emotion processing and regulation
- Social awareness and empathy
- Emotional memory and learning
- Self-awareness and introspection
- Emotional reasoning and decision making
"""

import sys
import os
import torch
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import json
from datetime import datetime
from pathlib import Path

# Add the emotional intelligence modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai', 'emotional_intelligence'))

try:
    from emotion_models.core_emotion_model import CoreEmotionModel
    from empathy.social_awareness import EmpathyEngine
    from memory.emotional_memory import EmotionalMemory
    from self_awareness.introspection import IntrospectionEngine
except ImportError:
    # Fallback if modules aren't available
    CoreEmotionModel = None
    EmpathyEngine = None
    EmotionalMemory = None
    IntrospectionEngine = None

class EmotionalIntelligenceSystem:
    """
    Integrated Emotional Intelligence System that coordinates:
    - Emotion recognition and regulation
    - Social awareness and empathy
    - Emotional memory and learning
    - Self-reflection and metacognition
    - Emotional reasoning for decision making
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the emotional intelligence system."""
        self.config = config or self._default_config()
        
        # Initialize core components if available
        self.emotion_model = None
        self.empathy_engine = None
        self.emotional_memory = None
        self.introspection_engine = None
        
        self._initialize_components()
        
        # Integration state
        self.current_emotional_state = {
            'primary_emotion': 'neutral',
            'intensity': 0.5,
            'confidence': 0.5,
            'regulation_status': 'stable'
        }
        
        self.social_context = {
            'active_relationships': {},
            'current_interaction': None,
            'social_norms': {}
        }
        
        # Performance metrics
        self.metrics = {
            'emotional_accuracy': 0.0,
            'empathy_effectiveness': 0.0,
            'memory_retention': 0.0,
            'self_awareness_depth': 0.0
        }
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the EI system."""
        return {
            'emotion_model': {
                'num_emotions': 24,
                'regulation_threshold': 0.7,
                'learning_rate': 0.01
            },
            'empathy': {
                'memory_size': 1000,
                'cultural_sensitivity': True,
                'relationship_tracking': True
            },
            'memory': {
                'max_episodic_memories': 1000,
                'consolidation_interval': 100,
                'forgetting_rate': 0.01
            },
            'introspection': {
                'reflection_depth': 2,
                'metacognitive_monitoring': True,
                'self_model_updates': True
            }
        }
    
    def _initialize_components(self) -> None:
        """Initialize EI components if available."""
        try:
            if CoreEmotionModel:
                self.emotion_model = CoreEmotionModel(
                    num_emotions=self.config['emotion_model']['num_emotions']
                )
            
            if EmpathyEngine:
                self.empathy_engine = EmpathyEngine(
                    num_emotions=self.config['emotion_model']['num_emotions'],
                    memory_size=self.config['empathy']['memory_size']
                )
            
            if EmotionalMemory:
                self.emotional_memory = EmotionalMemory(
                    max_episodic_memories=self.config['memory']['max_episodic_memories'],
                    consolidation_interval=self.config['memory']['consolidation_interval']
                )
            
            if IntrospectionEngine:
                self.introspection_engine = IntrospectionEngine(
                    memory_capacity=self.config['memory']['max_episodic_memories']
                )
        except Exception as e:
            print(f"Warning: Could not initialize some EI components: {e}")
    
    def process_emotional_input(self, 
                              input_data: Dict[str, Any], 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process emotional input through the integrated EI system.
        
        Args:
            input_data: Input containing emotional information
            context: Optional contextual information
        
        Returns:
            Comprehensive emotional analysis and response
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'input_analysis': {},
            'emotional_response': {},
            'social_response': {},
            'memory_integration': {},
            'self_reflection': {},
            'recommendations': []
        }
        
        # Step 1: Emotion Recognition and Analysis
        if self.emotion_model:
            emotion_analysis = self._analyze_emotions(input_data, context)
            result['input_analysis'] = emotion_analysis
            result['emotional_response'] = self._generate_emotional_response(emotion_analysis)
        
        # Step 2: Social Awareness and Empathy
        if self.empathy_engine and context and context.get('social_interaction'):
            social_analysis = self._process_social_context(input_data, context)
            result['social_response'] = social_analysis
        
        # Step 3: Memory Integration
        if self.emotional_memory:
            memory_integration = self._integrate_with_memory(input_data, context, result)
            result['memory_integration'] = memory_integration
        
        # Step 4: Self-Reflection
        if self.introspection_engine:
            reflection = self._perform_self_reflection(input_data, context, result)
            result['self_reflection'] = reflection
        
        # Step 5: Generate Recommendations
        result['recommendations'] = self._generate_recommendations(result)
        
        # Update system state
        self._update_system_state(result)
        
        return result
    
    def _analyze_emotions(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze emotions using the core emotion model."""
        try:
            if hasattr(self.emotion_model, 'predict_emotion'):
                prediction = self.emotion_model.predict_emotion(input_data)
                return {
                    'primary_emotion': prediction.get('emotion', 'neutral'),
                    'intensity': prediction.get('intensity', 0.5),
                    'confidence': prediction.get('confidence', 0.5),
                    'secondary_emotions': prediction.get('secondary_emotions', []),
                    'regulation_needed': prediction.get('intensity', 0.5) > self.config['emotion_model']['regulation_threshold']
                }
            else:
                # Fallback emotion analysis
                return self._fallback_emotion_analysis(input_data)
        except Exception as e:
            print(f"Emotion analysis error: {e}")
            return self._fallback_emotion_analysis(input_data)
    
    def _fallback_emotion_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback emotion analysis when core model is unavailable."""
        # Simple keyword-based emotion detection
        text = input_data.get('text', '').lower()
        
        emotion_keywords = {
            'joy': ['happy', 'excited', 'great', 'wonderful', 'amazing'],
            'sadness': ['sad', 'disappointed', 'upset', 'down', 'depressed'],
            'anger': ['angry', 'frustrated', 'annoyed', 'mad', 'furious'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous'],
            'surprise': ['surprise', 'unexpected', 'shocked', 'amazed'],
            'disgust': ['disgusted', 'gross', 'awful', 'terrible']
        }
        
        detected_emotions = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                detected_emotions[emotion] = min(score / len(keywords), 1.0)
        
        primary = max(detected_emotions.items(), key=lambda x: x[1]) if detected_emotions else ('neutral', 0.5)
        
        return {
            'primary_emotion': primary[0],
            'intensity': primary[1],
            'confidence': 0.6 if detected_emotions else 0.3,
            'secondary_emotions': [{'emotion': k, 'intensity': v} for k, v in detected_emotions.items() if k != primary[0]],
            'regulation_needed': primary[1] > 0.7
        }
    
    def _generate_emotional_response(self, emotion_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate emotional response based on analysis."""
        primary_emotion = emotion_analysis['primary_emotion']
        intensity = emotion_analysis['intensity']
        
        response_strategies = {
            'joy': {'amplify': True, 'share': True, 'celebrate': True},
            'sadness': {'comfort': True, 'support': True, 'empathize': True},
            'anger': {'calm': True, 'understand': True, 'redirect': True},
            'fear': {'reassure': True, 'support': True, 'problem_solve': True},
            'surprise': {'acknowledge': True, 'explore': True, 'adapt': True},
            'disgust': {'respect': True, 'distance': True, 'alternative': True},
            'neutral': {'engage': True, 'explore': True, 'maintain': True}
        }
        
        strategy = response_strategies.get(primary_emotion, response_strategies['neutral'])
        
        return {
            'strategy': strategy,
            'recommended_tone': self._determine_tone(primary_emotion, intensity),
            'emotional_mirroring': intensity * 0.7,  # Mirror but dampen
            'regulation_advice': self._get_regulation_advice(primary_emotion, intensity) if emotion_analysis.get('regulation_needed') else None
        }
    
    def _determine_tone(self, emotion: str, intensity: float) -> str:
        """Determine appropriate conversational tone."""
        tone_map = {
            'joy': 'enthusiastic' if intensity > 0.7 else 'positive',
            'sadness': 'compassionate',
            'anger': 'calm' if intensity > 0.7 else 'understanding',
            'fear': 'reassuring',
            'surprise': 'curious',
            'disgust': 'respectful',
            'neutral': 'engaging'
        }
        return tone_map.get(emotion, 'neutral')
    
    def _get_regulation_advice(self, emotion: str, intensity: float) -> Dict[str, Any]:
        """Get emotion regulation advice."""
        regulation_strategies = {
            'anger': ['deep_breathing', 'count_to_ten', 'physical_exercise', 'perspective_taking'],
            'fear': ['reality_check', 'gradual_exposure', 'relaxation_techniques', 'positive_self_talk'],
            'sadness': ['social_support', 'pleasant_activities', 'self_compassion', 'meaning_making']
        }
        
        strategies = regulation_strategies.get(emotion, ['mindfulness', 'self_awareness', 'acceptance'])
        
        return {
            'immediate_strategies': strategies[:2],
            'long_term_strategies': strategies[2:],
            'intensity_level': 'high' if intensity > 0.8 else 'moderate',
            'professional_help_recommended': intensity > 0.9
        }
    
    def _process_social_context(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process social interaction through empathy engine."""
        try:
            if hasattr(self.empathy_engine, 'process_social_cue'):
                agent_id = context.get('agent_id', 'unknown')
                social_cue = {
                    'text': input_data.get('text', ''),
                    'tone': input_data.get('tone', 'neutral'),
                    'context': context
                }
                
                return self.empathy_engine.process_social_cue(agent_id, social_cue, context)
            else:
                return self._basic_social_processing(input_data, context)
        except Exception as e:
            print(f"Social processing error: {e}")
            return self._basic_social_processing(input_data, context)
    
    def _basic_social_processing(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Basic social processing fallback."""
        return {
            'relationship_context': context.get('relationship', 'neutral'),
            'social_appropriateness': 0.8,  # Default assumption
            'empathic_response': 'I understand this might be important to you.',
            'relationship_impact': 'positive'
        }
    
    def _integrate_with_memory(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]], result: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate current experience with emotional memory."""
        try:
            if hasattr(self.emotional_memory, 'add_episodic_memory'):
                # Store this emotional experience
                emotion_data = result.get('input_analysis', {})
                memory_id = self.emotional_memory.add_episodic_memory(
                    emotion=emotion_data,
                    context=context or {},
                    importance=emotion_data.get('intensity', 0.5)
                )
                
                # Retrieve relevant memories
                if hasattr(self.emotional_memory, 'retrieve_relevant_memories'):
                    query = {
                        'emotion': emotion_data,
                        'context': context or {}
                    }
                    relevant_memories = self.emotional_memory.retrieve_relevant_memories(query, k=3)
                    
                    return {
                        'memory_stored': True,
                        'memory_id': memory_id,
                        'relevant_memories': relevant_memories,
                        'memory_insights': self._extract_memory_insights(relevant_memories)
                    }
                
                return {'memory_stored': True, 'memory_id': memory_id}
            else:
                return self._basic_memory_integration(input_data, context, result)
        except Exception as e:
            print(f"Memory integration error: {e}")
            return self._basic_memory_integration(input_data, context, result)
    
    def _basic_memory_integration(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]], result: Dict[str, Any]) -> Dict[str, Any]:
        """Basic memory integration fallback."""
        return {
            'memory_stored': False,
            'relevant_memories': [],
            'memory_insights': ['This appears to be a new type of experience.']
        }
    
    def _extract_memory_insights(self, memories: List[Dict[str, Any]]) -> List[str]:
        """Extract insights from retrieved memories."""
        if not memories:
            return ['This appears to be a new type of experience.']
        
        insights = []
        if len(memories) > 1:
            insights.append(f'You have {len(memories)} similar emotional experiences in memory.')
        
        # Analyze patterns
        emotions = [mem.get('emotion', {}).get('label', 'unknown') for mem in memories]
        if len(set(emotions)) == 1:
            insights.append(f'This consistently triggers {emotions[0]} emotions.')
        
        return insights
    
    def _perform_self_reflection(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]], result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform self-reflection using introspection engine."""
        try:
            if hasattr(self.introspection_engine, 'reflect'):
                current_state = {
                    'emotion': result.get('input_analysis', {}),
                    'context': context or {},
                    'social_context': result.get('social_response', {})
                }
                
                reflection = self.introspection_engine.reflect(current_state, depth=self.config['introspection']['reflection_depth'])
                
                # Update self-model if configured
                if self.config['introspection']['self_model_updates']:
                    observation = {
                        'emotional_response': result,
                        'context': context,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.introspection_engine.update_self_model(observation)
                
                return reflection
            else:
                return self._basic_self_reflection(input_data, context, result)
        except Exception as e:
            print(f"Self-reflection error: {e}")
            return self._basic_self_reflection(input_data, context, result)
    
    def _basic_self_reflection(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]], result: Dict[str, Any]) -> Dict[str, Any]:
        """Basic self-reflection fallback."""
        return {
            'confidence_level': 0.7,
            'learning_opportunity': True,
            'performance_assessment': 'adequate',
            'areas_for_improvement': ['emotional_accuracy', 'contextual_understanding']
        }
    
    def _generate_recommendations(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on the analysis."""
        recommendations = []
        
        # Emotional regulation recommendations
        emotional_response = result.get('emotional_response', {})
        if emotional_response.get('regulation_advice'):
            recommendations.append({
                'type': 'emotion_regulation',
                'priority': 'high',
                'action': 'Practice emotion regulation techniques',
                'details': emotional_response['regulation_advice']
            })
        
        # Social interaction recommendations
        social_response = result.get('social_response', {})
        if social_response:
            recommendations.append({
                'type': 'social_interaction',
                'priority': 'medium',
                'action': 'Consider social context in responses',
                'details': {'tone': emotional_response.get('recommended_tone', 'neutral')}
            })
        
        # Memory-based recommendations
        memory_integration = result.get('memory_integration', {})
        if memory_integration.get('memory_insights'):
            recommendations.append({
                'type': 'learning',
                'priority': 'low',
                'action': 'Reflect on patterns from similar experiences',
                'details': {'insights': memory_integration['memory_insights']}
            })
        
        return recommendations
    
    def _update_system_state(self, result: Dict[str, Any]) -> None:
        """Update the system's internal state based on processing results."""
        # Update current emotional state
        emotion_analysis = result.get('input_analysis', {})
        if emotion_analysis:
            self.current_emotional_state.update({
                'primary_emotion': emotion_analysis.get('primary_emotion', 'neutral'),
                'intensity': emotion_analysis.get('intensity', 0.5),
                'confidence': emotion_analysis.get('confidence', 0.5),
                'regulation_status': 'stable' if not emotion_analysis.get('regulation_needed') else 'needs_attention'
            })
        
        # Update metrics (simplified)
        self.metrics['emotional_accuracy'] = min(self.metrics['emotional_accuracy'] + 0.01, 1.0)
        if result.get('social_response'):
            self.metrics['empathy_effectiveness'] = min(self.metrics['empathy_effectiveness'] + 0.01, 1.0)
        if result.get('memory_integration', {}).get('memory_stored'):
            self.metrics['memory_retention'] = min(self.metrics['memory_retention'] + 0.01, 1.0)
        if result.get('self_reflection'):
            self.metrics['self_awareness_depth'] = min(self.metrics['self_awareness_depth'] + 0.01, 1.0)
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current emotional intelligence system state."""
        return {
            'emotional_state': self.current_emotional_state,
            'social_context': self.social_context,
            'metrics': self.metrics,
            'components_active': {
                'emotion_model': self.emotion_model is not None,
                'empathy_engine': self.empathy_engine is not None,
                'emotional_memory': self.emotional_memory is not None,
                'introspection_engine': self.introspection_engine is not None
            }
        }
    
    def save_state(self, filepath: str) -> bool:
        """Save the system state to file."""
        try:
            state = {
                'config': self.config,
                'current_emotional_state': self.current_emotional_state,
                'social_context': self.social_context,
                'metrics': self.metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save component states if they support serialization
            if self.emotional_memory and hasattr(self.emotional_memory, 'to_json'):
                state['emotional_memory'] = self.emotional_memory.to_json()
            if self.introspection_engine and hasattr(self.introspection_engine, 'to_json'):
                state['introspection_engine'] = self.introspection_engine.to_json()
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    @classmethod
    def load_state(cls, filepath: str) -> Optional['EmotionalIntelligenceSystem']:
        """Load system state from file."""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            instance = cls(config=state.get('config'))
            instance.current_emotional_state = state.get('current_emotional_state', {})
            instance.social_context = state.get('social_context', {})
            instance.metrics = state.get('metrics', {})
            
            # Restore component states if available
            if 'emotional_memory' in state and instance.emotional_memory:
                if hasattr(instance.emotional_memory, 'from_json'):
                    instance.emotional_memory = EmotionalMemory.from_json(state['emotional_memory'])
            
            if 'introspection_engine' in state and instance.introspection_engine:
                if hasattr(instance.introspection_engine, 'from_json'):
                    instance.introspection_engine = IntrospectionEngine.from_json(state['introspection_engine'])
            
            return instance
        except Exception as e:
            print(f"Error loading state: {e}")
            return None


# Main functions for backward compatibility and easy usage
def emotional_intelligence(input_data: Optional[Dict[str, Any]] = None, 
                         context: Optional[Dict[str, Any]] = None,
                         config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main emotional intelligence function for processing emotional input.
    
    Args:
        input_data: Input containing emotional information
        context: Optional contextual information
        config: Optional configuration for the EI system
    
    Returns:
        Comprehensive emotional analysis and response
    """
    if input_data is None:
        input_data = {'text': 'Hello, how are you?', 'tone': 'neutral'}
    
    # Create or reuse global EI system instance
    global _ei_system
    if '_ei_system' not in globals() or config:
        _ei_system = EmotionalIntelligenceSystem(config)
    
    return _ei_system.process_emotional_input(input_data, context)


def get_info() -> Dict[str, Any]:
    """Return information about the emotional intelligence module."""
    return {
        "name": "emotional_intelligence",
        "version": "2.0.0",
        "description": "Comprehensive Emotional Intelligence Integration System",
        "components": [
            "CoreEmotionModel - Neural network-based emotion recognition and regulation",
            "EmpathyEngine - Social awareness and empathy processing", 
            "EmotionalMemory - Episodic and semantic emotional memory",
            "IntrospectionEngine - Self-awareness and metacognition"
        ],
        "capabilities": [
            "Multi-modal emotion recognition",
            "Emotion regulation and management",
            "Social context understanding",
            "Empathic response generation",
            "Emotional memory integration",
            "Self-reflection and metacognition",
            "Personalized recommendations"
        ]
    }


# Example usage and testing
if __name__ == "__main__":
    # Initialize the emotional intelligence system
    ei_system = EmotionalIntelligenceSystem()
    
    # Test with various emotional inputs
    test_cases = [
        {
            'input': {'text': 'I just got promoted at work!', 'tone': 'excited'},
            'context': {'social_interaction': True, 'relationship': 'professional'}
        },
        {
            'input': {'text': 'I feel really anxious about the presentation tomorrow', 'tone': 'worried'},
            'context': {'social_interaction': False, 'setting': 'work'}
        },
        {
            'input': {'text': 'Thank you for listening to me', 'tone': 'grateful'},
            'context': {'social_interaction': True, 'relationship': 'supportive'}
        }
    ]
    
    print("Emotional Intelligence System Testing")
    print("=" * 40)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {test_case['input']['text']}")
        
        result = ei_system.process_emotional_input(
            test_case['input'], 
            test_case['context']
        )
        
        print(f"Primary Emotion: {result['input_analysis'].get('primary_emotion', 'unknown')}")
        print(f"Intensity: {result['input_analysis'].get('intensity', 0):.2f}")
        print(f"Recommended Tone: {result['emotional_response'].get('recommended_tone', 'neutral')}")
        
        if result['recommendations']:
            print("Recommendations:")
            for rec in result['recommendations']:
                print(f"  - {rec['action']} (Priority: {rec['priority']})")
    
    # Display system state
    print("\nSystem State:")
    state = ei_system.get_current_state()
    print(f"Current Emotion: {state['emotional_state']['primary_emotion']}")
    print(f"Metrics: {state['metrics']}")
    print(f"Active Components: {sum(state['components_active'].values())}/4")
