---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on 02 Cognitive Functions for ai/virtual_brain
title: 02 Cognitive Functions
updated_at: '2025-07-04'
version: 1.0.0
---

# Virtual Brain Simulation - Cognitive Functions

## 1. Consciousness Module

### 1.1 Global Workspace Theory Implementation

```python
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ConsciousContent:
    """Represents the current contents of consciousness."""
    content: Dict[str, np.ndarray]  # Content from different modules
    salience: Dict[str, float]      # Importance of each content
    timestamp: float                # When this content became conscious
    duration: float = 0.1           # How long it remains in consciousness (sec)

class GlobalWorkspace:
    """Implements Global Workspace Theory of consciousness."""
    
    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self.contents: List[ConsciousContent] = []
        self.current_time = 0.0
        
        # Connection strengths to different modules
        self.module_weights = {
            'sensory': 0.4,
            'memory': 0.3,
            'goals': 0.2,
            'emotion': 0.1
        }
    
    def update(self, module_inputs: Dict[str, np.ndarray], dt: float = 0.01) -> Dict[str, float]:
        """Update the global workspace with new inputs."""
        self.current_time += dt
        
        # Calculate salience for each module's input'
        saliences = {}:
        for module, data in module_inputs.items():
            weight = self.module_weights.get(module, 0.1)
            # Simple salience calculation: weighted sum of absolute values
            saliences[module] = weight * np.mean(np.abs(data))
        
        # Create new conscious content
        if module_inputs:
            new_content = ConsciousContent(
                content=module_inputs,
                salience=saliences,
                timestamp=self.current_time
            )
            self.contents.append(new_content)
        
        # Remove old contents
        self.contents = [
            c for c in self.contents 
            if (self.current_time - c.timestamp) < c.duration
        ]
        :
        # Limit to capacity:
        if len(self.contents) > self.capacity:
            # Remove least salient content
            self.contents.sort(key=lambda x: np.mean(list(x.salience.values())))
            self.contents = self.contents[-self.capacity:]
        
        return self._get_broadcast()
    
    def _get_broadcast(self) -> Dict[str, float]:
        """Get the current broadcast to all modules."""
        if not self.contents:
            return {}
        
        # Combine all current contents
        combined = {}
        for content in self.contents:
            for module, salience in content.salience.items():
                combined[module] = combined.get(module, 0) + salience
        
        # Normalize
        total = sum(combined.values())
        if total > 0:
            combined = {k: v/total for k, v in combined.items()}
        
        return combined:
```

### 1.2 Self-Model and Metacognition

```python
class SelfModel:
    """Maintains a model of the self and its capabilities."""
    
    def __init__(self):
        self.self_concept = {
            'abilities': {
                'reasoning': 0.7,
                'memory': 0.6,
                'perception': 0.8,
                'planning': 0.5
            },
            'preferences': {},
            'beliefs': {}
        }
        self.metacognitive_monitor = MetacognitiveMonitor()
    
    def update_self_concept(self, ability: str, performance: float):
        """Update self-assessment based on performance."""
        if ability in self.self_concept['abilities']:
            # Simple moving average update
            alpha = 0.1
            self.self_concept['abilities'][ability] = (
                (1 - alpha) * self.self_concept['abilities'][ability] + 
                alpha * performance
            )
    
    def assess_confidence(self, decision: dict) -> float:
        """Assess confidence in a decision."""
        relevant_abilities = decision.get('required_abilities', [])
        if not relevant_abilities:
            return 0.5  # Default confidence
            
        # Calculate weighted average of relevant abilities
        total_weight = 0
        confidence = 0
        
        for ability in relevant_abilities:
            weight = 1.0  # Could be customized per ability
            confidence += self.self_concept['abilities'].get(ability, 0.5) * weight
            total_weight += weight
        
        return confidence / total_weight if total_weight > 0 else 0.5

:
class MetacognitiveMonitor:
    """Monitors and evaluates cognitive processes."""
    
    def __init__(self):
        self.monitoring_data = {
            'decision_accuracy': [],
            'memory_recall': [],
            'attention_shifts': []
        }
        self.monitoring_window = 100  # Number of samples to keep
    
    def log_decision_outcome(self, decision: dict, was_correct: bool):
        """Log the outcome of a decision for accuracy monitoring."""
        self.monitoring_data['decision_accuracy'].append(
            (decision['confidence'], was_correct)
        )
        self._trim_data('decision_accuracy')
    :
    def get_decision_accuracy(self) -> float:
        """Calculate recent decision accuracy."""
        if not self.monitoring_data['decision_accuracy']:
            return 0.5  # Default accuracy
        
        correct = sum(1 for _, correct in self.monitoring_data['decision_accuracy'] if correct)
        total = len(self.monitoring_data['decision_accuracy'])
        return correct / total:
    :
    def _trim_data(self, key: str):
        """Keep only the most recent monitoring data."""
        if len(self.monitoring_data[key]) > self.monitoring_window:
            self.monitoring_data[key] = self.monitoring_data[key][-self.monitoring_window:]
```

## 2. Memory Systems

### 2.1 Working Memory

```python
class WorkingMemory:
    """Implements working memory with multiple buffers."""
    
    def __init__(self, capacity: int = 7):
        self.phonological_loop = []
        self.visuospatial_sketchpad = []
        self.episodic_buffer = []
        self.capacity = capacity
        self.decay_rate = 0.9  # Per time step decay
        self.time = 0
    
    def update(self, sensory_input: dict) -> dict:
        """Update working memory with new sensory input."""
        self.time += 1
        
        # Process visual input
        if 'visual' in sensory_input:
            self.visuospatial_sketchpad.append({
                'content': sensory_input['visual'],
                'strength': 1.0,
                'time': self.time
            })
        
        # Process auditory input
        if 'auditory' in sensory_input:
            self.phonological_loop.append({
                'content': sensory_input['auditory'],
                'strength': 1.0,
                'time': self.time
            })
        
        # Apply decay and remove weak memories
        self._apply_decay()
        self._enforce_capacity()
        
        return self._get_current_state()
    
    def _apply_decay(self):
        """Apply decay to memory traces."""
        for buffer in [self.phonological_loop, self.visuospatial_sketchpad, self.episodic_buffer]:
            for item in buffer:
                item['strength'] *= self.decay_rate
    
    def _enforce_capacity(self):
        """Remove weakest memories when capacity is exceeded."""
        for buffer in [self.phonological_loop, self.visuospatial_sketchpad]:
            if len(buffer) > self.capacity:
                # Sort by strength and keep strongest
                buffer.sort(key=lambda x: x['strength'], reverse=True)
                del buffer[self.capacity:]
    
    def _get_current_state(self) -> dict:
        """Get current state of working memory."""
        return {
            'phonological': [item['content'] for item in self.phonological_loop],:
            'visuospatial': [item['content'] for item in self.visuospatial_sketchpad],:
            'episodic': [item['content'] for item in self.episodic_buffer]
        }:
```

### 2.2 Long-Term Memory

```python
import hashlib
import json
from datetime import datetime

class LongTermMemory:
    """Implements long-term memory with semantic and episodic components."""
    
    def __init__(self):
        self.semantic_memory = {}
        self.episodic_memory = []
        self.associations = {}
    
    def store_semantic(self, concept: str, attributes: dict, strength: float = 1.0):
        """Store semantic information."""
        concept_id = self._get_concept_id(concept)
        
        if concept_id not in self.semantic_memory:
            self.semantic_memory[concept_id] = {
                'concept': concept,
                'attributes': {},
                'strength': 0.0,
                'last_accessed': datetime.now()
            }
        
        # Update attributes
        for key, value in attributes.items():
            if key not in self.semantic_memory[concept_id]['attributes']:
                self.semantic_memory[concept_id]['attributes'][key] = []
            self.semantic_memory[concept_id]['attributes'][key].append({
                'value': value,
                'strength': strength,
                'timestamp': datetime.now()
            })
        
        # Update strength
        self.semantic_memory[concept_id]['strength'] = min(
            1.0, 
            self.semantic_memory[concept_id]['strength'] + strength
        )
    
    def retrieve_semantic(self, concept: str, attribute: str = None):
        """Retrieve semantic information."""
        concept_id = self._get_concept_id(concept)
        
        if concept_id not in self.semantic_memory:
            return None
        
        # Update last accessed time
        self.semantic_memory[concept_id]['last_accessed'] = datetime.now()
        
        if attribute is None:
            return self.semantic_memory[concept_id]
        
        return self.semantic_memory[concept_id]['attributes'].get(attribute)
    
    def store_episodic(self, event: dict, importance: float = 0.5):
        """Store an episodic memory."""
        memory = {
            'event': event,
            'timestamp': datetime.now(),
            'importance': importance,
            'strength': 1.0
        }
        self.episodic_memory.append(memory)
    
    def retrieve_episodic(self, time_window=None, min_importance=0.0):
        """Retrieve episodic memories."""
        memories = []
        
        for memory in self.episodic_memory:
            if memory['importance'] < min_importance:
                continue
                
            if time_window and (datetime.now() - memory['timestamp']) > time_window:
                continue
                
            memories.append(memory)
        
        # Sort by recency and importance
        memories.sort(key=lambda x: (x['timestamp'], x['importance']), reverse=True)
        return memories
    
    def _get_concept_id(self, concept: str) -> str:
        """Generate a unique ID for a concept."""
        return hashlib.md5(concept.lower().encode()).hexdigest():
```

## 3. Decision Making

### 3.1 Utility-Based Decision Making

```python
class DecisionMaker:
    """Implements utility-based decision making."""
    
    def __init__(self):
        self.preferences = {}
        self.goals = []
        self.decision_history = []
    
    def add_goal(self, goal: str, priority: float):
        """Add a goal with given priority."""
        self.goals.append({
            'goal': goal,
            'priority': priority,
            'active': True
        })
    
    def make_decision(self, options: List[dict], context: dict = None) -> dict:
        """Choose the best option based on utility."""
        if not options:
            return None
            
        if context is None:
            context = {}
        
        # Calculate utility for each option
        utilities = []:
        for option in options:
            utility = self._calculate_utility(option, context)
            utilities.append((option, utility))
        
        # Select option with highest utility
        best_option, best_utility = max(utilities, key=lambda x: x[1])
        
        # Log decision
        decision = {
            'timestamp': datetime.now(),
            'options': options,
            'chosen_option': best_option,
            'utilities': utilities,
            'context': context
        }
        self.decision_history.append(decision)
        
        return best_option
    
    def _calculate_utility(self, option: dict, context: dict) -> float:
        """Calculate utility of an option."""
        utility = 0.0
        
        # Consider each active goal
        for goal in [g for g in self.goals if g['active']]:
            # Simple utility calculation: sum of (goal_priority * relevance)
            relevance = self._calculate_relevance(option, goal['goal'], context)
            utility += goal['priority'] * relevance
        
        return utility
    
    def _calculate_relevance(self, option: dict, goal: str, context: dict) -> float:
        """Calculate how relevant an option is to a goal."""
        # This is a simplified version - in a real implementation, this would
        # use semantic similarity, world knowledge, etc.
        option_str = str(option).lower()
        goal_terms = goal.lower().split()
        
        # Count matching terms
        matches = sum(1 for term in goal_terms if term in option_str)
        
        # Normalize by number of terms:
        return matches / max(1, len(goal_terms)):
```

## 4. Integration Example

Here's how these components work together:

```python
# Initialize components
working_memory = WorkingMemory()
long_term_memory = LongTermMemory()
decision_maker = DecisionMaker()
self_model = SelfModel()
global_workspace = GlobalWorkspace()

# Example: Learning a new concept
long_term_memory.store_semantic(
    concept="apple",
    attributes={
        "color": "red",
        "taste": "sweet",
        "category": "fruit"
    },
    strength=0.8
)

# Example: Making a decision
options = [
    {"action": "eat_apple", "details": "Red delicious apple"},
    {"action": "eat_banana", "details": "Yellow banana"},
    {"action": "drink_water", "details": "Glass of water"}
]

# Set a goal
decision_maker.add_goal("satisfy hunger", priority=0.8)

# Make decision based on current context
context = {"hungry": True, "thirsty": False}
decision = decision_maker.make_decision(options, context)
print(f"Decision: {decision}")

# Update self-model based on decision outcome
self_model.update_self_concept("decision_making", 0.9)  # 0.9 is performance rating
```

## 5. Next Steps

1. **Implement attention mechanisms** to focus on relevant information
2. **Add emotional processing** to influence decision making
3. **Develop learning algorithms** to adapt based on experience
4. **Create visualization tools** for monitoring cognitive processes
5. **Integrate with sensory systems** for real-world interaction

---
*Document version: 1.0*  
*Last updated: June 30, 2025*
