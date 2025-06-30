# Emotional Intelligence and Self-Awareness System

A comprehensive implementation of emotional intelligence and self-awareness capabilities for AI systems, featuring emotion modeling, introspection, empathy, and emotional memory.

## Features

- **Full Emotional Spectrum**: Models 24 distinct human emotions with varying intensities
- **Neural Network-Based**: Deep learning models for emotion processing and regulation
- **Self-Reflection**: Metacognitive monitoring and introspection capabilities
- **Social Intelligence**: Empathy, perspective-taking, and social awareness
- **Emotional Memory**: Long-term storage and retrieval of emotional experiences
- **Adaptive Behavior**: Emotionally-intelligent responses and decision-making

## Core Components

### 1. Emotion Models (`/emotion_models/`)
- `core_emotion_model.py`: Neural network-based model for simulating human emotional spectrum
  - Dimensional model (Valence, Arousal, Dominance)
  - Basic and social emotions
  - Emotion blending and regulation

### 2. Self-Awareness (`/self_awareness/`)
- `introspection.py`: Implements self-reflection and metacognitive capabilities
  - Thought monitoring and analysis
  - Behavioral pattern recognition
  - Self-evaluation and critique
  - Goal alignment assessment

### 3. Empathy and Social Awareness (`/empathy/`)
- `social_awareness.py`: Implements theory of mind and social intelligence
  - Emotion recognition in others
  - Perspective taking
  - Empathic responding
  - Social norm understanding

### 4. Emotional Memory (`/memory/`)
- `emotional_memory.py`: Manages storage and retrieval of emotional experiences
  - Episodic memory for specific events
  - Semantic memory for generalized knowledge
  - Memory consolidation and forgetting
  - Emotional pattern recognition

### 5. Emotion Regulation (`/emotion_regulation/`)
- `regulator.py`: Implements emotional regulation strategies
  - Cognitive reappraisal
  - Response modulation
  - Situation selection
  - Attention deployment
  - Physiological regulation

## Getting Started

### Prerequisites
- Python 3.8+
- PyTorch 1.9.0+
- See `requirements.txt` for full dependencies

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/emotional-intelligence-ai.git
cd emotional-intelligence-ai

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
from emotion_models.core_emotion_model import CoreEmotionModel
from self_awareness.introspection import IntrospectionEngine
from empathy.social_awareness import EmpathyEngine
from memory.emotional_memory import EmotionalMemory

# Initialize components
emotion_model = CoreEmotionModel()
introspection = IntrospectionEngine(emotion_model)
empathy = EmpathyEngine()
memory = EmotionalMemory()

# Process an emotional event
current_emotion = torch.tensor([0.8, 0.6, 0.4])  # Example emotion vector
context = {
    'event': 'received_compliment',
    'source': 'colleague',
    'intensity': 0.8
}

# Get emotional response
response = emotion_model(current_emotion.unsqueeze(0))

# Engage in self-reflection
reflection = introspection.reflect({
    'emotion': response,
    'context': context,
    'goals': ['be_professional', 'build_relationships']
}, depth=2)

# Store in memory
memory_id = memory.add_episodic_memory(
    emotion=response,
    context=context,
    importance=0.7
)
```

## Documentation

### Emotion Representation
- Uses a hybrid model combining dimensional and categorical approaches
- Supports 24 distinct emotions with varying intensities
- Models emotional dynamics over time

### Self-Awareness Features
- Real-time thought monitoring
- Behavioral pattern analysis
- Metacognitive awareness
- Goal alignment tracking

### Social Intelligence
- Emotion recognition in text and voice
- Perspective taking
- Context-appropriate responses
- Relationship modeling

### Memory System
- Episodic memory for specific events
- Semantic memory for generalized knowledge
- Forgetting mechanisms
- Memory consolidation

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by psychological theories of emotion and cognition
- Built using PyTorch for deep learning capabilities
- Incorporates concepts from affective computing and cognitive science
