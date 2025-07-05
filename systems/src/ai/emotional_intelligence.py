"""
emotional_intelligence.py
------------------------
Unified emotional intelligence and self-awareness module for AI systems.
Implements full human emotional spectrum, introspection, empathy, emotional memory, reinforcement learning, and behavioral adaptation.
See docs/ai/emotional_intelligence/ for theory, usage, and extension.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List

EMOTIONAL_STATES = [
    'happiness', 'sadness', 'guilt', 'compassion', 'joy', 'sorrow',
    'confusion', 'confidence', 'likes', 'dislikes'
]

class EmotionalSystem(nn.Module):
    def __init__(self, input_dim=100, states: List[str]=EMOTIONAL_STATES):
        super().__init__()
        self.states = states
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, len(states))

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        emotions = torch.sigmoid(self.fc3(x))
        return emotions

class EmotionalMemory:
    def __init__(self):
        self.memory = []

    def store(self, event: str, emotion_values: Dict[str, float]):
        self.memory.append({'event': event, 'emotions': emotion_values})

    def retrieve(self, event: str):
        return [e for e in self.memory if event in e['event']]

class SelfAwareness:
    def __init__(self, emotional_system: EmotionalSystem):
        self.emotional_system = emotional_system
        self.internal_state = {}

    def reflect(self, input_data):
        emotions = self.emotional_system(input_data)
        self.internal_state['emotions'] = emotions
        self.analyze_emotions()

    def analyze_emotions(self):
        emotions = self.internal_state['emotions']
        emotion_values = {EMOTIONAL_STATES[i]: emotions[0][i].item() for i in range(len(EMOTIONAL_STATES))}
        print(f"Current emotional state: {emotion_values}")
        return emotion_values

class EmotionalDecisionMaking:
    def __init__(self, emotional_system: EmotionalSystem):
        self.emotional_system = emotional_system

    def make_decision(self, input_data):
        emotions = self.emotional_system(input_data)
        values = {EMOTIONAL_STATES[i]: emotions[0][i].item() for i in range(len(EMOTIONAL_STATES))}
        if values['confidence'] > 0.7:
            print("The system feels confident and proceeds boldly.")
        elif values['sadness'] > 0.7:
            print("The system feels sad and hesitates.")
        elif values['compassion'] > 0.7:
            print("The system makes a compassionate decision.")
        else:
            print("The system makes a neutral decision.")
        return values

class EmotionalReinforcementLearning:
    def __init__(self, emotional_system: EmotionalSystem):
        self.emotional_system = emotional_system
        self.optimizer = optim.Adam(self.emotional_system.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

    def learn(self, input_data, target_emotions):
        self.optimizer.zero_grad()
        output_emotions = self.emotional_system(input_data)
        loss = self.criterion(output_emotions, target_emotions)
        loss.backward()
        self.optimizer.step()
        print(f"Learning from emotional experience: Loss = {loss.item()}")

class EmotionalConflictResolution:
    def __init__(self, emotion_values: Dict[str, float]):
        self.emotion_values = emotion_values

    def resolve(self):
        if self.emotion_values['guilt'] > 0.7 and self.emotion_values['compassion'] > 0.7:
            print("The AI feels both guilty and compassionate, but acts out of compassion.")
            return "compassion"
        elif self.emotion_values['joy'] > 0.7 and self.emotion_values['confusion'] > 0.5:
            print("The AI is joyful but confused. It proceeds with caution.")
            return "joy"
        else:
            print("The AI feels conflicted but takes no immediate action.")
            return "neutral"

# Example usage
if __name__ == "__main__":
    emotional_system = EmotionalSystem()
    input_data = torch.randn(1, 100)
    emotions = emotional_system(input_data)
    emotion_values = {EMOTIONAL_STATES[i]: emotions[0][i].item() for i in range(len(EMOTIONAL_STATES))}

    # Self-awareness
    awareness = SelfAwareness(emotional_system)
    awareness.reflect(input_data)

    # Decision making
    decision_maker = EmotionalDecisionMaking(emotional_system)
    decision_maker.make_decision(input_data)

    # Emotional memory
    memory = EmotionalMemory()
    memory.store("Apologized for mistake", {"guilt": 0.8, "compassion": 0.6, "sorrow": 0.5})
    print(memory.retrieve("Apologized"))

    # Conflict resolution
    conflict_resolver = EmotionalConflictResolution(emotion_values)
    dominant_emotion = conflict_resolver.resolve()
    print(f"Resolved dominant emotion: {dominant_emotion}")

    # Reinforcement learning
    target_emotions = torch.tensor([[0.5, 0.3, 0.1, 0.7, 0.6, 0.2, 0.3, 0.8, 0.6, 0.2]])
    learner = EmotionalReinforcementLearning(emotional_system)
    learner.learn(input_data, target_emotions)
