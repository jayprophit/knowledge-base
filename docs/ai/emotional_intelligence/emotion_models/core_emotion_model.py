"""
Core Emotion Model

Implements a neural network-based model for simulating the human emotional spectrum.
Uses a combination of dimensional and categorical emotion models.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional

class CoreEmotionModel(nn.Module):
    """
    Neural network model for processing emotional states and generating responses.
    Implements a hybrid approach combining:
    - Dimensional model (Valence, Arousal, Dominance)
    - Basic emotions (Joy, Sadness, Anger, Fear, Disgust, Surprise)
    - Social emotions (Pride, Shame, Guilt, etc.)
    """
    
    def __init__(self, input_size: int = 512, hidden_size: int = 256, num_emotions: int = 24):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_emotions = num_emotions
        
        # Input processing layers
        self.encoder = nn.Sequential(
            nn.Linear(input_size, hidden_size * 2),
            nn.LeakyReLU(),
            nn.LayerNorm(hidden_size * 2)
        )
        
        # Emotion processing layers
        self.emotion_layers = nn.ModuleDict({
            'dimensional': nn.Sequential(
                nn.Linear(hidden_size * 2, hidden_size),
                nn.Tanh(),
                nn.Linear(hidden_size, 3)  # VAD: Valence, Arousal, Dominance
            ),
            'basic': nn.Sequential(
                nn.Linear(hidden_size * 2, hidden_size),
                nn.LeakyReLU(),
                nn.Linear(hidden_size, 6)  # 6 basic emotions
            ),
            'social': nn.Sequential(
                nn.Linear(hidden_size * 2, hidden_size // 2),
                nn.LeakyReLU(),
                nn.Linear(hidden_size // 2, 12)  # 12 social emotions
            )
        })
        
        # Emotion blending and regulation
        self.emotion_blender = nn.Sequential(
            nn.Linear(3 + 6 + 12, hidden_size),
            nn.LeakyReLU(),
            nn.Linear(hidden_size, num_emotions)
        )
        
        # Emotional state memory
        self.memory = []
        self.max_memory = 1000
        
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Process input through the emotion model."""
        # Encode input
        encoded = self.encoder(x)
        
        # Process through different emotion pathways
        dimensional = torch.sigmoid(self.emotion_layers['dimensional'](encoded))
        basic = F.softmax(self.emotion_layers['basic'](encoded), dim=-1)
        social = torch.sigmoid(self.emotion_layers['social'](encoded))
        
        # Combine emotion representations
        emotion_features = torch.cat([dimensional, basic, social], dim=-1)
        blended_emotions = F.softmax(self.emotion_blender(emotion_features), dim=-1)
        
        # Update emotional memory
        self._update_memory(blended_emotions.detach())
        
        return {
            'dimensional': dimensional,
            'basic': basic,
            'social': social,
            'blended': blended_emotions
        }
    
    def _update_memory(self, emotions: torch.Tensor) -> None:
        """Update emotional memory with current state."""
        self.memory.append(emotions.cpu().numpy())
        if len(self.memory) > self.max_memory:
            self.memory = self.memory[-self.max_memory:]
    
    def get_emotional_state(self) -> Dict[str, np.ndarray]:
        """Get current emotional state with interpretation."""
        if not self.memory:
            return {
                'intensity': 0.0,
                'dominant_emotion': 'neutral',
                'emotion_vector': np.zeros(self.num_emotions)
            }
            
        current = self.memory[-1]
        emotion_names = [
            # Basic emotions
            'joy', 'sadness', 'anger', 'fear', 'disgust', 'surprise',
            # Social emotions
            'pride', 'shame', 'guilt', 'embarrassment', 'gratitude', 'admiration',
            'contempt', 'envy', 'jealousy', 'pity', 'disappointment', 'hope',
            # Complex emotions
            'awe', 'nostalgia', 'confusion', 'curiosity', 'contentment', 'boredom'
        ]
        
        dominant_idx = np.argmax(current)
        return {
            'intensity': float(np.max(current)),
            'dominant_emotion': emotion_names[dominant_idx],
            'emotion_vector': current,
            'emotion_names': emotion_names
        }
    
    def regulate_emotion(self, target_emotion: str, strength: float = 0.5) -> torch.Tensor:
        """Generate regulation signal to shift emotional state."""
        emotion_names = self.get_emotional_state()['emotion_names']
        target_idx = emotion_names.index(target_emotion.lower())
        
        # Create target vector
        target = torch.zeros(self.num_emotions)
        target[target_idx] = strength
        
        # Generate regulation signal
        current = torch.tensor(self.memory[-1] if self.memory else np.zeros(self.num_emotions))
        regulation = target - current
        
        return regulation

# Example usage
if __name__ == "__main__":
    # Initialize model
    model = CoreEmotionModel()
    
    # Create random input (in practice, this would be processed sensory/context data)
    input_tensor = torch.randn(1, 512)
    
    # Get emotional response
    with torch.no_grad():
        emotions = model(input_tensor)
        state = model.get_emotional_state()
        
    print(f"Current emotional state: {state['dominant_emotion']} "
          f"(intensity: {state['intensity']:.2f})")
