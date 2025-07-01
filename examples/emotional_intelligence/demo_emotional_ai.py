#!/usr/bin/env python3
"""
Emotional AI Demonstration
--------------------------
This script demonstrates the emotional intelligence capabilities of the system,
including emotion modeling, self-awareness, and empathy.
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from pydantic import BaseModel

# Emotion model (simplified for demonstration)
class EmotionVector(BaseModel):
    valence: float  # -1.0 (negative) to 1.0 (positive)
    arousal: float  # 0.0 (calm) to 1.0 (excited)
    dominance: float  # 0.0 (submissive) to 1.0 (dominant)

class EmotionModel:
    """Simplified emotion model for demonstration."""
    
    def __init__(self):
        # Initialize with neutral state
        self.current_emotion = EmotionVector(
            valence=0.0,
            arousal=0.5,
            dominance=0.5
        )
        self.emotion_history = []
        
    def update_emotion(self, stimulus: Dict[str, float]) -> EmotionVector:
        """Update emotional state based on stimulus."""
        # Simple weighted update
        self.current_emotion.valence = 0.9 * self.current_emotion.valence + 0.1 * stimulus.get('valence', 0)
        self.current_emotion.arousal = 0.9 * self.current_emotion.arousal + 0.1 * stimulus.get('arousal', 0.5)
        self.current_emotion.dominance = 0.9 * self.current_emotion.dominance + 0.1 * stimulus.get('dominance', 0.5)
        
        # Ensure values stay in valid range
        self.current_emotion.valence = max(-1.0, min(1.0, self.current_emotion.valence))
        self.current_emotion.arousal = max(0.0, min(1.0, self.current_emotion.arousal))
        self.current_emotion.dominance = max(0.0, min(1.0, self.current_emotion.dominance))
        
        # Record in history
        self.emotion_history.append((datetime.now(), self.current_emotion.copy()))
        return self.current_emotion
    
    def get_emotion_label(self) -> str:
        """Convert VAD vector to emotion label."""
        v, a, d = self.current_emotion.valence, self.current_emotion.arousal, self.current_emotion.dominance
        
        if v > 0.5 and a > 0.5: return "excited"
        if v > 0.5 and a <= 0.5: return "content"
        if v > 0 and a > 0.5: return "happy"
        if v > 0 and a <= 0.5: return "calm"
        if v < -0.5 and a > 0.5: return "angry"
        if v < -0.5 and a <= 0.5: return "sad"
        if v < 0 and a > 0.5: return "anxious"
        if v < 0 and a <= 0.5: return "bored"
        return "neutral"

class SelfAwarenessModule:
    """Self-awareness and introspection capabilities."""
    
    def __init__(self, emotion_model: EmotionModel):
        self.emotion_model = emotion_model
        self.self_reflections = []
        
    async def reflect(self) -> str:
        """Perform self-reflection on current emotional state."""
        emotion = self.emotion_model.get_emotion_label()
        reflection = f"I'm feeling {emotion}. "
        
        if emotion in ["angry", "anxious"]:
            reflection += "I should take a moment to calm down."
        elif emotion in ["happy", "excited"]:
            reflection += "I'm in a good mood to be productive!"
            
        self.self_reflections.append((datetime.now(), reflection))
        return reflection

class EmpathyModule:
    """Empathy and social awareness capabilities."""
    
    def __init__(self, emotion_model: EmotionModel):
        self.emotion_model = emotion_model
        
    async def respond_with_empathy(self, user_emotion: str) -> str:
        """Generate an empathetic response to user's emotion."""
        responses = {
            "happy": ["I'm glad to hear that!", "That's wonderful!", "I'm happy for you!"],
            "sad": ["I'm sorry to hear that.", "That sounds difficult.", "I'm here for you."],
            "angry": ["I can see you're upset.", "That sounds frustrating.", "Let's work through this together."],
            "anxious": ["I can understand why you'd feel that way.", "Let's take a deep breath together.", "You're not alone in this."],
            "default": ["I see.", "Tell me more.", "I understand."]
        }
        
        return random.choice(responses.get(user_emotion, responses["default"]))

async def main():
    print("=== Emotional AI Demonstration ===\n")
    
    # Initialize components
    emotion_model = EmotionModel()
    self_awareness = SelfAwarenessModule(emotion_model)
    empathy = EmpathyModule(emotion_model)
    
    # Simulate emotional stimuli
    stimuli = [
        {"valence": 0.8, "arousal": 0.9, "dominance": 0.7},  # Excited
        {"valence": -0.6, "arousal": 0.8, "dominance": 0.4},  # Angry
        {"valence": -0.7, "arousal": 0.3, "dominance": 0.2},  # Sad
        {"valence": 0.9, "arousal": 0.4, "dominance": 0.6},  # Content
    ]
    
    for i, stimulus in enumerate(stimuli, 1):
        print(f"\n--- Scenario {i} ---")
        
        # Update emotion based on stimulus
        emotion = emotion_model.update_emotion(stimulus)
        emotion_label = emotion_model.get_emotion_label()
        print(f"Current emotion: {emotion_label} (V: {emotion.valence:.2f}, A: {emotion.arousal:.2f}, D: {emotion.dominance:.2f})")
        
        # Demonstrate self-awareness
        reflection = await self_awareness.reflect()
        print(f"Self-reflection: {reflection}")
        
        # Demonstrate empathy (simulate user emotion)
        user_emotion = random.choice(["happy", "sad", "angry", "anxious"])
        print(f"User seems: {user_emotion}")
        response = await empathy.respond_with_empathy(user_emotion)
        print(f"Empathetic response: {response}")
        
        await asyncio.sleep(1)  # Pause between scenarios
    
    print("\n=== End of Demonstration ===")

if __name__ == "__main__":
    asyncio.run(main())
