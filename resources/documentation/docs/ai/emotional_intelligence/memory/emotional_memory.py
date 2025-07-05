"""
Emotional Memory System

Implements episodic and semantic memory for emotional experiences,
allowing the AI to learn from past emotional interactions and patterns.
"""

import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import torch
import torch.nn as nn
from sklearn.cluster import KMeans

class EmotionalMemory:
    """
    Manages storage and retrieval of emotional experiences with the following features:
    - Episodic memory for specific emotional events
    - Semantic memory for generalized emotional knowledge
    - Memory consolidation and forgetting mechanisms
    - Emotional pattern recognition
    - Contextual retrieval
    """
    
    def __init__(self, 
                 embedding_dim: int = 128,
                 max_episodic_memories: int = 1000,
                 consolidation_interval: int = 100):
        """Initialize the emotional memory system."""
        self.embedding_dim = embedding_dim
        self.max_episodic_memories = max_episodic_memories
        self.consolidation_interval = consolidation_interval
        
        # Episodic memory: stores specific emotional events
        self.episodic_memory = deque(maxlen=max_episodic_memories)
        self.episodic_index = 0
        
        # Semantic memory: stores generalized emotional knowledge
        self.semantic_memory = {
            'emotional_patterns': [],
            'coping_strategies': {},
            'relationship_models': {}
        }
        
        # Memory networks
        self.encoder = self._build_encoder()
        self.retrieval_network = self._build_retrieval_network()
        
        # Memory consolidation counters
        self.consolidation_counter = 0
        
        # Emotional schemas (generalized representations)
        self.emotional_schemas = {}
        
        # Initialize with basic emotional knowledge
        self._initialize_basic_knowledge()
    
    def _build_encoder(self) -> nn.Module:
        """Build neural network for encoding memories."""
        return nn.Sequential(
            nn.Linear(256, 256),  # Input: combined context + emotion features
            nn.LeakyReLU(),
            nn.Linear(256, self.embedding_dim),
            nn.LayerNorm(self.embedding_dim)
        )
    
    def _build_retrieval_network(self) -> nn.Module:
        """Build neural network for memory retrieval."""
        return nn.Sequential(
            nn.Linear(self.embedding_dim * 2, 256),  # Query + memory embeddings
            nn.LeakyReLU(),
            nn.Linear(256, 1),  # Relevance score
            nn.Sigmoid()
        )
    
    def _initialize_basic_knowledge(self) -> None:
        """Initialize with basic emotional knowledge."""
        basic_emotions = {
            'joy': {'valence': 0.9, 'arousal': 0.7, 'dominance': 0.7},
            'sadness': {'valence': 0.1, 'arousal': -0.3, 'dominance': -0.5},
            'anger': {'valence': -0.7, 'arousal': 0.8, 'dominance': 0.6},
            'fear': {'valence': -0.6, 'arousal': 0.9, 'dominance': -0.7},
            'disgust': {'valence': -0.8, 'arousal': 0.5, 'dominance': -0.3},
            'surprise': {'valence': 0.3, 'arousal': 0.9, 'dominance': 0.1}
        }
        
        # Store as semantic memory
        self.semantic_memory['basic_emotions'] = basic_emotions
        
        # Initialize some basic coping strategies
        self.semantic_memory['coping_strategies'] = {
            'anger': ['deep_breathing', 'timeout', 'physical_activity'],
            'sadness': ['social_support', 'pleasant_activity', 'self_compassion'],
            'fear': ['reality_check', 'gradual_exposure', 'relaxation'],
            'stress': ['mindfulness', 'prioritization', 'delegation']
        }
    
    def add_episodic_memory(self, 
                          emotion: Dict[str, Any],
                          context: Dict[str, Any],
                          importance: float = 0.5) -> int:
        """
        Add a new episodic memory.
        
        Args:
            emotion: Dictionary containing emotional state
            context: Contextual information about the event
            importance: Subjective importance of the memory (0-1)
            
        Returns:
            Memory ID for the stored memory
        """
        # Generate memory embedding
        memory_features = self._extract_memory_features(emotion, context)
        memory_embedding = self.encoder(
            torch.tensor(memory_features, dtype=torch.float32).unsqueeze(0)
        ).squeeze().detach().numpy()
        
        # Create memory entry
        memory = {
            'id': self.episodic_index,
            'timestamp': datetime.now().isoformat(),
            'emotion': emotion,
            'context': context,
            'importance': importance,
            'embedding': memory_embedding,
            'retrieval_strength': 1.0,  # New memories start strong
            'access_count': 0,
            'last_accessed': datetime.now().isoformat()
        }
        
        # Add to episodic memory
        self.episodic_memory.append(memory)
        self.episodic_index += 1
        
        # Check if it's time to consolidate memories
        self.consolidation_counter += 1
        if self.consolidation_counter >= self.consolidation_interval:
            self.consolidate_memories()
            self.consolidation_counter = 0
        
        return memory['id']
    
    def retrieve_relevant_memories(self, 
                                 query: Dict[str, Any],
                                 k: int = 5,
                                 recency_weight: float = 0.3,
                                 importance_weight: float = 0.4,
                                 emotional_similarity_weight: float = 0.3) -> List[Dict]:
        """
        Retrieve memories relevant to the current context and emotional state.
        
        Args:
            query: Dictionary containing current emotional state and context
            k: Number of memories to retrieve
            recency_weight: Weight for recency in retrieval
            importance_weight: Weight for importance in retrieval
            emotional_similarity_weight: Weight for emotional similarity
            
        Returns:
            List of relevant memories, sorted by relevance
        """
        if not self.episodic_memory:
            return []
        
        # Encode query
        query_features = self._extract_memory_features(
            query.get('emotion', {}), 
            query.get('context', {})
        )
        query_embedding = self.encoder(
            torch.tensor(query_features, dtype=torch.float32).unsqueeze(0)
        ).squeeze().detach().numpy()
        
        # Calculate relevance scores for each memory
        memories = list(self.episodic_memory)  # Create a copy
        
        # Get current time for recency calculations
        now = datetime.now()
        
        # Calculate scores for each memory
        scored_memories = []
        for mem in memories:
            # Calculate recency score (exponential decay)
            last_accessed = datetime.fromisoformat(mem['last_accessed'])
            hours_since_access = (now - last_accessed).total_seconds() / 3600
            recency_score = np.exp(-0.1 * hours_since_access)  # Half-life ~7 hours
            
            # Get importance score
            importance_score = mem['importance']
            
            # Calculate emotional similarity
            emotional_similarity = self._calculate_emotional_similarity(
                query['emotion'], 
                mem['emotion']
            )
            
            # Calculate embedding similarity
            embedding_similarity = np.dot(
                query_embedding, 
                mem['embedding']
            ) / (np.linalg.norm(query_embedding) * np.linalg.norm(mem['embedding']) + 1e-8)
            
            # Combine scores
            total_score = (
                recency_weight * recency_score +
                importance_weight * importance_score +
                emotional_similarity_weight * (0.7 * emotional_similarity + 0.3 * embedding_similarity)
            )
            
            scored_memories.append((total_score, mem))
        
        # Sort by total score and return top k
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        # Update access metadata for retrieved memories
        for _, mem in scored_memories[:k]:
            mem['access_count'] += 1
            mem['last_accessed'] = now.isoformat()
            
            # Update retrieval strength (spaced repetition effect)
            mem['retrieval_strength'] = min(
                1.0,
                mem['retrieval_strength'] + 0.1 * (1.0 - mem['retrieval_strength'])
            )
        
        return [m[1] for m in scored_memories[:k]]
    
    def _extract_memory_features(self, 
                               emotion: Dict[str, Any], 
                               context: Dict[str, Any]) -> np.ndarray:
        """Extract features for memory encoding."""
        # Extract emotion features
        emotion_vec = [
            emotion.get('valence', 0.0),
            emotion.get('arousal', 0.0),
            emotion.get('dominance', 0.0),
            emotion.get('intensity', 0.0)
        ]
        
        # Extract context features (simplified)
        context_features = [
            len(context.get('text', '')),  # Length of context text
            len(context.get('participants', [])),  # Number of participants
            1.0 if context.get('is_goal_related', False) else 0.0,
            1.0 if context.get('is_social', False) else 0.0
        ]
        
        # Combine features
        return np.concatenate([
            emotion_vec,
            context_features,
            np.zeros(256 - len(emotion_vec) - len(context_features))  # Pad to 256
        ])
    
    def _calculate_emotional_similarity(self, 
                                      emotion1: Dict[str, float], 
                                      emotion2: Dict[str, float]) -> float:
        """Calculate similarity between two emotional states."""
        # Simple Euclidean distance in VAD space
        v1 = np.array([
            emotion1.get('valence', 0.0),
            emotion1.get('arousal', 0.0),
            emotion1.get('dominance', 0.0)
        ])
        
        v2 = np.array([
            emotion2.get('valence', 0.0),
            emotion2.get('arousal', 0.0),
            emotion2.get('dominance', 0.0)
        ])
        
        # Convert distance to similarity (0-1)
        distance = np.linalg.norm(v1 - v2)
        return np.exp(-distance)
    
    def consolidate_memories(self) -> None:
        """
        Perform memory consolidation:
        - Strengthen important memories
        - Weaken/forget less important ones
        - Extract semantic knowledge
        """
        if not self.episodic_memory:
            return
        
        # Update retrieval strengths based on usage
        now = datetime.now()
        for mem in self.episodic_memory:
            # Decay based on time since last access
            last_accessed = datetime.fromisoformat(mem['last_accessed'])
            hours_since_access = (now - last_accessed).total_seconds() / 3600
            
            # More frequently accessed memories decay more slowly
            decay_rate = 0.1 / (1.0 + np.log1p(mem['access_count']))
            decay = np.exp(-decay_rate * hours_since_access / 24)  # Daily decay
            
            # Update retrieval strength
            mem['retrieval_strength'] *= decay
        
        # Extract semantic knowledge (clustering of similar memories)
        self._extract_semantic_knowledge()
        
        # Forget weak memories if we're approaching capacity
        if len(self.episodic_memory) > self.max_episodic_memories * 0.9:
            self._forget_memories()
    
    def _extract_semantic_knowledge(self) -> None:
        """Extract generalized knowledge from episodic memories."""
        if len(self.episodic_memory) < 10:  # Need enough memories
            return
        
        # Cluster memories by emotional similarity
        memory_embeddings = np.array([m['embedding'] for m in self.episodic_memory])
        
        # Use k-means to find emotional patterns
        k = min(5, len(self.episodic_memory) // 10)  # Roughly 10 memories per cluster
        kmeans = KMeans(n_clusters=k, random_state=42)
        clusters = kmeans.fit_predict(memory_embeddings)
        
        # Update emotional schemas
        self.emotional_schemas = {}
        for i in range(k):
            cluster_memories = [m for m, c in zip(self.episodic_memory, clusters) if c == i]
            if not cluster_memories:
                continue
                
            # Create schema from cluster center
            center = kmeans.cluster_centers_[i]
            
            # Find most representative memory
            distances = [
                np.linalg.norm(mem['embedding'] - center)
                for mem in cluster_memories
            ]
            representative = cluster_memories[np.argmin(distances)]
            
            # Store schema
            self.emotional_schemas[f'schema_{i}'] = {
                'center': center.tolist(),
                'representative_memory': representative['id'],
                'common_emotions': self._extract_common_features(
                    [m['emotion'] for m in cluster_memories]
                ),
                'common_contexts': self._extract_common_features(
                    [m['context'] for m in cluster_memories],
                    is_context=True
                ),
                'size': len(cluster_memories),
                'average_importance': np.mean([m['importance'] for m in cluster_memories])
            }
    
    def _extract_common_features(self, 
                               items: List[Dict], 
                               is_context: bool = False) -> Dict[str, Any]:
        """Extract common features from a list of items."""
        if not items:
            return {}
            
        if is_context:
            # For contexts, look for common keys and values
            key_counts = defaultdict(int)
            value_counts = defaultdict(int)
            
            for item in items:
                for k, v in item.items():
                    key_counts[k] += 1
                    value_counts[(k, str(v))] += 1
            
            # Get most common keys
            common_keys = [
                k for k, count in key_counts.items()
                if count >= len(items) * 0.5  # Appears in at least 50% of items
            ]
            
            # Get most common values for common keys
            common_features = {}
            for k in common_keys:
                values = [
                    (val, count) for (key, val), count in value_counts.items()
                    if key == k and count >= len(items) * 0.3  # At least 30% for this value
                ]
                if values:
                    common_features[k] = [
                        {'value': val, 'frequency': count/len(items)}
                        for val, count in values
                    ]
            
            return common_features
        else:
            # For emotions, calculate average values
            emotion_vectors = []
            for item in items:
                vec = [
                    item.get('valence', 0.0),
                    item.get('arousal', 0.0),
                    item.get('dominance', 0.0),
                    item.get('intensity', 0.0)
                ]
                if any(v != 0 for v in vec):
                    emotion_vectors.append(vec)
            
            if not emotion_vectors:
                return {}
                
            avg_emotion = np.mean(emotion_vectors, axis=0)
            std_emotion = np.std(emotion_vectors, axis=0)
            
            return {
                'valence': {'mean': float(avg_emotion[0]), 'std': float(std_emotion[0])},
                'arousal': {'mean': float(avg_emotion[1]), 'std': float(std_emotion[1])},
                'dominance': {'mean': float(avg_emotion[2]), 'std': float(std_emotion[2])},
                'intensity': {'mean': float(avg_emotion[3]), 'std': float(std_emotion[3])}
            }
    
    def _forget_memories(self) -> None:
        """Forget less important memories to free up space."""
        if not self.episodic_memory:
            return
        
        # Calculate forget scores for each memory
        forget_scores = []
        now = datetime.now()
        
        for i, mem in enumerate(self.episodic_memory):
            # Higher score = more likely to forget
            last_accessed = datetime.fromisoformat(mem['last_accessed'])
            hours_since_access = (now - last_accessed).total_seconds() / 3600
            
            # Score based on recency, importance, and access count
            score = (
                0.6 * (1.0 - mem['importance']) +  # Less important = more likely to forget
                0.3 * np.exp(-0.1 * mem['access_count']) +  # Rarely accessed = more likely to forget
                0.1 * np.tanh(hours_since_access / 24)  # Older = more likely to forget (with diminishing returns)
            )
            
            forget_scores.append((i, score))
        
        # Sort by forget score (highest first)
        forget_scores.sort(key=lambda x: -x[1])
        
        # Forget a portion of the least important memories
        num_to_forget = max(10, len(self.episodic_memory) - self.max_episodic_memories)
        to_forget = set(i for i, _ in forget_scores[:num_to_forget])
        
        # Create new memory list without forgotten memories
        self.episodic_memory = deque(
            mem for i, mem in enumerate(self.episodic_memory)
            if i not in to_forget
        )
    
    def get_emotional_patterns(self) -> List[Dict]:
        """Get learned emotional patterns and schemas."""
        return list(self.emotional_schemas.values())
    
    def get_coping_strategies(self, emotion: str) -> List[str]:
        """Get suggested coping strategies for an emotion."""
        return self.semantic_memory['coping_strategies'].get(emotion, [])
    
    def to_json(self) -> str:
        """Serialize emotional memory to JSON."""
        return json.dumps({
            'episodic_memory': list(self.episodic_memory),
            'semantic_memory': self.semantic_memory,
            'emotional_schemas': self.emotional_schemas,
            'episodic_index': self.episodic_index,
            'consolidation_counter': self.consolidation_counter,
            'model_state': {
                'encoder': {k: v.tolist() for k, v in self.encoder.state_dict().items()},
                'retrieval_network': {k: v.tolist() for k, v in self.retrieval_network.state_dict().items()}
            }
        }, default=lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EmotionalMemory':
        """Deserialize emotional memory from JSON."""
        data = json.loads(json_str)
        instance = cls()
        
        # Restore basic attributes
        instance.episodic_memory = deque(data['episodic_memory'], maxlen=instance.max_episodic_memories)
        instance.semantic_memory = data['semantic_memory']
        instance.emotional_schemas = data.get('emotional_schemas', {})
        instance.episodic_index = data['episodic_index']
        instance.consolidation_counter = data['consolidation_counter']
        
        # Restore model states
        if 'model_state' in data:
            encoder_state = {
                k: torch.tensor(v) 
                for k, v in data['model_state']['encoder'].items()
            }
            instance.encoder.load_state_dict(encoder_state)
            
            retrieval_state = {
                k: torch.tensor(v)
                for k, v in data['model_state']['retrieval_network'].items()
            }
            instance.retrieval_network.load_state_dict(retrieval_state)
        
        return instance

# Example usage
if __name__ == "__main__":
    # Initialize emotional memory
    memory = EmotionalMemory()
    
    # Add some example memories
    memory.add_episodic_memory(
        emotion={
            'valence': 0.8,
            'arousal': 0.7,
            'dominance': 0.6,
            'intensity': 0.9,
            'label': 'joy'
        },
        context={
            'text': 'Received praise from supervisor',
            'participants': ['supervisor'],
            'location': 'office',
            'is_goal_related': True,
            'is_social': True
        },
        importance=0.9
    )
    
    memory.add_episodic_memory(
        emotion={
            'valence': -0.6,
            'arousal': 0.8,
            'dominance': -0.3,
            'intensity': 0.7,
            'label': 'fear'
        },
        context={
            'text': 'Made a mistake in the presentation',
            'participants': ['team', 'manager'],
            'location': 'meeting_room',
            'is_goal_related': True,
            'is_social': True
        },
        importance=0.8
    )
    
    # Retrieve relevant memories
    query = {
        'emotion': {
            'valence': 0.7,
            'arousal': 0.6,
            'dominance': 0.5,
            'label': 'happiness'
        },
        'context': {
            'text': 'Working on an important project',
            'is_goal_related': True
        }
    }
    
    relevant_memories = memory.retrieve_relevant_memories(query, k=2)
    print(f"Retrieved {len(relevant_memories)} relevant memories:")
    for i, mem in enumerate(relevant_memories, 1):
        print(f"{i}. {mem['context'].get('text', 'No text')} "
              f"(Emotion: {mem['emotion'].get('label', 'unknown')}, "
              f"Importance: {mem['importance']:.2f})")
