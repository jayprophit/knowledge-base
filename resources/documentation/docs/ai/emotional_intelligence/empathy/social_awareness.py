"""
Social Awareness and Empathy Module

Implements theory of mind, empathy, and social intelligence capabilities.
"""

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import json

class EmpathyEngine:
    """
    Implements social awareness through:
    - Emotion recognition in others
    - Perspective taking
    - Empathic responding
    - Social norm understanding
    - Relationship modeling
    """
    
    def __init__(self, num_emotions: int = 24, memory_size: int = 1000):
        self.num_emotions = num_emotions
        self.social_memory = defaultdict(lambda: {
            'interactions': [],
            'relationship_strength': 0.5,
            'emotional_history': [],
            'needs_preferences': {}
        })
        self.social_norms = self._initialize_social_norms()
        self.empathy_network = self._build_empathy_network()
        self.max_memory = memory_size
    
    def process_social_cue(self, 
                          agent_id: str, 
                          cue: Dict[str, Any], 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Process social cues from another agent."""
        # Update memory of this agent
        self._update_agent_memory(agent_id, cue, context)
        
        # Recognize emotional state
        emotion_recognition = self._recognize_emotion(cue, context)
        
        # Take perspective
        perspective = self._take_perspective(agent_id, emotion_recognition, context)
        
        # Generate empathic response
        response = self._generate_empathic_response(
            agent_id, 
            emotion_recognition, 
            perspective, 
            context
        )
        
        return {
            'emotion_recognition': emotion_recognition,
            'perspective': perspective,
            'empathic_response': response,
            'relationship_update': self._update_relationship(agent_id, response, context)
        }
    
    def _recognize_emotion(self, 
                          cue: Dict[str, Any], 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Recognize emotions from social cues."""
        # In a real implementation, this would use multimodal emotion recognition
        # For now, we'll use a simplified version
        
        # Extract features from cue (facial expression, tone, language, etc.)
        features = self._extract_emotional_features(cue)
        
        # Process through emotion recognition network
        with torch.no_grad():
            emotion_probs = torch.softmax(
                self.empathy_network['emotion_recognizer'](
                    torch.tensor(features, dtype=torch.float32)
                ), 
                dim=-1
            ).numpy()
        
        # Get top emotions
        top_emotions = np.argsort(emotion_probs)[-3:][::-1]
        
        return {
            'emotion_probs': emotion_probs,
            'dominant_emotion': int(top_emotions[0]),
            'confidence': float(emotion_probs[top_emotions[0]]),
            'secondary_emotions': [
                {'emotion': int(e), 'confidence': float(emotion_probs[e])}
                for e in top_emotions[1:]
            ]
        }
    
    def _take_perspective(self, 
                         agent_id: str, 
                         emotion_recognition: Dict[str, Any],
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Take the perspective of another agent."""
        # Get relationship history
        history = self.social_memory[agent_id]
        
        # Consider cultural and contextual factors
        cultural_context = self._get_cultural_context(context)
        
        # Simulate mental state inference
        mental_state = {
            'beliefs': self._infer_beliefs(agent_id, context),
            'desires': self._infer_desires(agent_id, context),
            'intentions': self._infer_intentions(agent_id, context)
        }
        
        return {
            'inferred_mental_state': mental_state,
            'relationship_context': {
                'strength': history['relationship_strength'],
                'history_length': len(history['interactions']),
                'recent_interactions': history['interactions'][-3:]
            },
            'cultural_context': cultural_context
        }
    
    def _generate_empathic_response(self, 
                                   agent_id: str, 
                                   emotion_recognition: Dict[str, Any],
                                   perspective: Dict[str, Any],
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an appropriate empathic response."""
        # Determine response type based on emotion and context
        emotion = emotion_recognition['dominant_emotion']
        confidence = emotion_recognition['confidence']
        
        # Get relationship context
        relationship_strength = perspective['relationship_context']['strength']
        
        # Generate response based on emotion type and intensity
        if confidence > 0.7:  # High confidence in emotion recognition
            if emotion in [0, 1, 2]:  # Positive emotions
                response_type = 'celebrate' if relationship_strength > 0.6 else 'acknowledge_positive'
            elif emotion in [3, 4, 5]:  # Negative emotions
                response_type = 'comfort' if relationship_strength > 0.6 else 'acknowledge_distress'
            else:  # Neutral/mixed
                response_type = 'validate'
        else:  # Low confidence
            response_type = 'explore'
        
        # Generate response content
        response = self._formulate_response(
            response_type, 
            emotion_recognition, 
            perspective,
            context
        )
        
        return {
            'response_type': response_type,
            'content': response,
            'appropriate_intimacy': min(0.3 + (relationship_strength * 0.7), 0.9),
            'suggested_actions': self._suggest_actions(emotion_recognition, perspective)
        }
    
    def _update_relationship(self, 
                           agent_id: str, 
                           response: Dict[str, Any],
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Update relationship model based on interaction."""
        # Get current relationship state
        relationship = self.social_memory[agent_id]
        
        # Update relationship strength based on interaction quality
        interaction_quality = self._assess_interaction_quality(response, context)
        relationship['relationship_strength'] = np.clip(
            relationship['relationship_strength'] + (0.1 * (interaction_quality - 0.5)),
            0.0, 1.0
        )
        
        # Add to interaction history
        relationship['interactions'].append({
            'timestamp': context.get('timestamp', ''),
            'interaction_quality': interaction_quality,
            'response_type': response['response_type']
        })
        
        # Trim old interactions if needed
        if len(relationship['interactions']) > self.max_memory:
            relationship['interactions'] = relationship['interactions'][-self.max_memory:]
        
        return {
            'updated_strength': relationship['relationship_strength'],
            'interaction_count': len(relationship['interactions']),
            'recent_quality': np.mean([i['interaction_quality'] 
                                     for i in relationship['interactions'][-10:]])
        }
    
    def _build_empathy_network(self) -> Dict[str, torch.nn.Module]:
        """Initialize neural networks for empathy and social cognition."""
        # Emotion recognition network
        emotion_recognizer = torch.nn.Sequential(
            torch.nn.Linear(128, 64),  # Input features
            torch.nn.LeakyReLU(),
            torch.nn.Linear(64, self.num_emotions)
        )
        
        # Perspective taking network
        perspective_taker = torch.nn.LSTMCell(256, 128)  # For modeling mental states over time
        
        # Response generation network
        response_generator = torch.nn.Sequential(
            torch.nn.Linear(128, 64),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(64, 32)  # Response features
        )
        
        return {
            'emotion_recognizer': emotion_recognizer,
            'perspective_taker': perspective_taker,
            'response_generator': response_generator
        }
    
    def _extract_emotional_features(self, cue: Dict[str, Any]) -> List[float]:
        """Extract emotional features from social cues."""
        # This would extract features from:
        # - Facial expressions
        # - Vocal tone/prosody
        # - Language use
        # - Body language
        # - Contextual information
        
        # For now, return random features as placeholder
        return np.random.rand(128).tolist()
    
    def _get_cultural_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant cultural context for social interaction."""
        # In a real implementation, this would consider:
        # - Cultural norms
        # - Social hierarchy
        # - Communication style preferences
        # - Taboos and sensitivities
        
        return {
            'formality_level': 0.6,  # 0-1 scale
            'individualism': 0.8,    # Individualistic vs collectivistic
            'power_distance': 0.4,   # Acceptance of hierarchy
            'uncertainty_avoidance': 0.5,
            'context_dependence': 0.7  # High vs low context communication
        }
    
    def _infer_beliefs(self, agent_id: str, context: Dict[str, Any]) -> List[str]:
        """Infer likely beliefs of the other agent."""
        # This would use theory of mind to infer beliefs
        return [
            "Wants to be understood",
            "Has goals they're pursuing",
            "Has their own perspective"
        ]
    
    def _infer_desires(self, agent_id: str, context: Dict[str, Any]) -> List[str]:
        """Infer likely desires of the other agent."""
        return [
            "Seeks validation",
            "Wants effective communication",
            "Desires positive interaction"
        ]
    
    def _infer_intentions(self, agent_id: str, context: Dict[str, Any]) -> List[str]:
        """Infer likely intentions of the other agent."""
        return [
            "To communicate effectively",
            "To achieve mutual understanding",
            "To maintain positive relationship"
        ]
    
    def _formulate_response(self, 
                          response_type: str,
                          emotion_recognition: Dict[str, Any],
                          perspective: Dict[str, Any],
                          context: Dict[str, Any]) -> str:
        """Formulate an appropriate response based on type and context."""
        # In a real implementation, this would use NLG to create responses
        responses = {
            'celebrate': [
                "That's wonderful! I'm really happy for you!",
                "What great news! You must be thrilled!"
            ],
            'acknowledge_positive': [
                "That sounds like a positive development.",
                "I'm glad to hear things are going well."
            ],
            'comfort': [
                "I'm really sorry you're going through this. That sounds difficult.",
                "I can only imagine how hard this must be for you."
            ],
            'acknowledge_distress': [
                "I hear that you're feeling upset about this.",
                "That sounds like a challenging situation."
            ],
            'validate': [
                "I can understand why you'd feel that way.",
                "Your feelings make sense given the situation."
            ],
            'explore': [
                "Can you tell me more about how you're feeling?",
                "I want to make sure I understand - could you say more?"
            ]
        }
        
        # Select response based on context
        possible_responses = responses.get(response_type, ["I see."])
        return np.random.choice(possible_responses)
    
    def _suggest_actions(self, 
                        emotion_recognition: Dict[str, Any],
                        perspective: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest possible actions based on the social context."""
        emotion = emotion_recognition['dominant_emotion']
        strength = perspective['relationship_context']['strength']
        
        actions = []
        
        if emotion in [0, 1, 2]:  # Positive emotions
            if strength > 0.7:
                actions.append({"action": "share_personal_experience", "priority": 0.8})
            actions.append({"action": "express_shared_joy", "priority": 0.9})
            
        elif emotion in [3, 4, 5]:  # Negative emotions
            if strength > 0.7:
                actions.append({"action": "offer_support", "priority": 0.9})
                actions.append({"action": "suggest_solutions", "priority": 0.6})
            else:
                actions.append({"action": "express_concern", "priority": 0.8})
        
        # Always include these basic actions
        actions.extend([
            {"action": "active_listening", "priority": 0.95},
            {"action": "validate_feelings", "priority": 0.9}
        ])
        
        # Sort by priority
        return sorted(actions, key=lambda x: -x['priority'])
    
    def _assess_interaction_quality(self, 
                                  response: Dict[str, Any],
                                  context: Dict[str, Any]) -> float:
        """Assess the quality of the interaction for relationship updates."""
        # In a real implementation, this would consider:
        # - Response appropriateness
        # - Emotional attunement
        # - Cultural sensitivity
        # - Timing and turn-taking
        
        # For now, return a random quality score
        return np.clip(np.random.normal(0.7, 0.15), 0.0, 1.0)
    
    def _initialize_social_norms(self) -> Dict[str, Any]:
        """Initialize social norms and expectations."""
        return {
            'turn_taking': {
                'min_pause': 0.5,  # seconds
                'max_pause': 3.0,
                'interruption_allowed': False
            },
            'emotional_expression': {
                'appropriate_intensity': 0.7,  # 0-1 scale
                'cultural_variation': {
                    'display_rules': {
                        'positive': 'encouraged',
                        'negative': 'moderated'
                    }
                }
            },
            'relationship_boundaries': {
                'appropriate_topics': {
                    'acquaintance': ['weather', 'hobbies', 'general_news'],
                    'friend': ['work', 'interests', 'moderate_personal'],
                    'close_friend': ['relationships', 'personal_issues', 'emotions']
                },
                'physical_boundaries': {
                    'personal_space': 1.2,  # meters
                    'touch': 'context_dependent'
                }
            }
        }
    
    def to_json(self) -> str:
        """Serialize social awareness state to JSON."""
        return json.dumps({
            'social_memory': dict(self.social_memory),
            'social_norms': self.social_norms
        }, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x.__dict__)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EmpathyEngine':
        """Deserialize from JSON."""
        data = json.loads(json_str)
        instance = cls()
        instance.social_memory = defaultdict(lambda: {
            'interactions': [],
            'relationship_strength': 0.5,
            'emotional_history': [],
            'needs_preferences': {}
        }, data.get('social_memory', {}))
        instance.social_norms = data.get('social_norms', instance._initialize_social_norms())
        return instance

# Example usage
if __name__ == "__main__":
    # Initialize empathy engine
    empathy = EmpathyEngine()
    
    # Simulate processing a social cue
    cue = {
        'text': "I just got the job I've been interviewing for!",
        'tone': 'excited',
        'facial_expression': 'smiling',
        'body_language': 'open'
    }
    
    context = {
        'relationship': 'acquaintance',
        'setting': 'professional',
        'timestamp': '2023-11-15T14:30:00Z'
    }
    
    # Process the social cue
    result = empathy.process_social_cue('user123', cue, context)
    
    print("Empathy Engine Results:")
    print(f"Recognized emotion: {result['emotion_recognition']['dominant_emotion']}")
    print(f"Response: {result['empathic_response']['content']}")
    print(f"Updated relationship strength: {result['relationship_update']['updated_strength']:.2f}")
