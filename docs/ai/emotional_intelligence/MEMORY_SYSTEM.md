---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Memory System for ai/emotional_intelligence
title: Memory System
updated_at: '2025-07-04'
version: 1.0.0
---

# Emotional Memory System

## Overview

The Emotional Memory System is responsible for storing, retrieving, and consolidating emotional experiences. It implements both episodic (specific events) and semantic (generalized knowledge) memory systems to support emotional intelligence.

## Core Components

### 1. Episodic Memory

Stores specific emotional events with rich contextual details.

**Key Features:**
- Temporal organization of memories
- Contextual embedding storage
- Retrieval strength tracking
- Forgetting mechanisms

**Data Structure:**
```python
{
    'id': int,                     # Unique identifier
    'timestamp': str,              # ISO format timestamp
    'emotion': {                   # Emotional state at time of memory
        'vector': List[float],     # 24-dimensional emotion vector
        'intensity': float,        # 0.0 to 1.0
        'dominance': float,        # -1.0 to 1.0
        'label': str               # Emotion label (e.g., 'joy', 'sadness')
    },
    'context': {                   # Contextual information
        'text': str,               # Associated text
        'participants': List[str], # People involved
        'location': str,           # Physical/virtual location
        'environment': str,        # Type of environment
        'sensory': {               # Sensory information
            'visual': List[str],   # Visual descriptors
            'auditory': List[str], # Sound descriptors
            'tactile': List[str]   # Touch descriptors
        }
    },
    'importance': float,           # 0.0 to 1.0
    'embedding': List[float],      # Vector representation (128D)
    'retrieval_strength': float,   # 0.0 to 1.0
    'access_count': int,           # Number of recalls
    'last_accessed': str,          # ISO format timestamp
    'tags': List[str],             # Categorical tags
    'related_memories': List[int]  # IDs of related memories
}
``````python
{
    'schema_id': str,              # Unique schema identifier
    'prototype': {                 # Prototypical example
        'emotion_vector': List[float],
        'context_features': Dict[str, float]
    },
    'variability': {               # How much instances vary
        'emotion_std': List[float],
        'context_std': Dict[str, float]
    },
    'frequency': float,            # How often this schema occurs
    'last_updated': str,           # ISO timestamp
    'associated_memories': List[int],  # Episodic memory IDs
    'related_schemas': List[Dict]  # Related schemas with strength
}
``````python
memory.add_episodic_memory(
    emotion={
        'vector': [0.8, 0.2, 0.1, ...],
        'intensity': 0.75,
        'dominance': 0.6,
        'label': 'pride'
    },
    context={
        'text': 'Received recognition at work',
        'participants': ['manager', 'team'],
        'location': 'office',
        'environment': 'professional',
        'sensory': {
            'visual': ['bright_lights', 'smiling_faces'],
            'auditory': ['applause', 'congratulations'],
            'tactile': ['handshake']
        }
    },
    importance=0.8,
    tags=['achievement', 'work', 'recognition']
)
``````python
# Find memories similar to current emotional state
similar_memories = memory.retrieve_similar_memories(
    query_emotion=current_emotion,
    context=current_context,
    k=5,                    # Number of memories to retrieve
    recency_weight=0.4,     # How much to favor recent memories
    importance_weight=0.4,  # How much to favor important memories
    similarity_weight=0.2   # How much to favor emotional similarity
)
``````python
# Perform memory consolidation
consolidation_report = memory.consolidate_memories(
    batch_size=100,         # Number of memories to process
    learning_rate=0.01,     # How quickly to update schemas
    forget_threshold=0.2    # Below this, memories may be forgotten
)
``````python
class MemoryEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim, embed_dim):
        super().__init__()
        self.emotion_encoder = nn.Sequential(
            nn.Linear(24, hidden_dim // 2),  # 24 emotion dimensions
            nn.LeakyReLU(),
            nn.LayerNorm(hidden_dim // 2)
        )
        self.context_encoder = nn.Sequential(
            nn.Linear(input_dim - 24, hidden_dim // 2),
            nn.LeakyReLU(),
            nn.LayerNorm(hidden_dim // 2)
        )
        self.combiner = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.LeakyReLU(),
            nn.Linear(hidden_dim, embed_dim),
            nn.LayerNorm(embed_dim)
        )
    
    def forward(self, x):
        emotion = x[:, :24]
        context = x[:, 24:]
        
        emotion_encoded = self.emotion_encoder(emotion)
        context_encoded = self.context_encoder(context)
        
        combined = torch.cat([emotion_encoded, context_encoded], dim=1)
        return self.combiner(combined)
``````python
class MemoryRetriever:
    def __init__(self, dim, metric='cosine'):;
        self.index = faiss.IndexFlatIP(dim)  # Inner product for cosine similarity;
        self.memories = [];
        self.id_to_idx = {};
        :
    def add_memory(self, memory_id, embedding):
        idx = len(self.memories);
        self.memories.append(memory_id)
        self.id_to_idx[memory_id] = idx
        
        # Convert to numpy array and normalize for cosine similarity
        emb = np.array(embedding, dtype=np.float32);
        faiss.normalize_L2(emb.reshape(1, -1))
        :
        if self.index.ntotal == 0:;
            self.index.add(emb)
        else:
            self.index.add(emb)
    
    def search(self, query_embedding, k=5):;
        # Prepare query
        query = np.array(query_embedding, dtype=np.float32).reshape(1, -1);
        faiss.normalize_L2(query)
        
        # Search
        distances, indices = self.index.search(query, k);
        
        # Map back to memory IDs
        results = [];
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx >= 0:  # Valid index:
                results.append({
                    'memory_id': self.memories[idx],
                    'similarity': float(dist),  # Cosine similarity
                    'rank': i + 1
                })
        
        return results
``````python
def update_memory_strengths(self, current_time):
    """Update retrieval strengths based on time and access patterns."""
    for mem in self.episodic_memory:
        # Time since last access (in hours)
        last_access = datetime.fromisoformat(mem['last_accessed'])
        hours_since_access = (current_time - last_access).total_seconds() / 3600
        
        # Calculate decay factor based on importance and access count
        base_decay = 0.95  # Base decay rate per day
        importance_factor = 1.0 - (mem['importance'] * 0.5)  # Important memories decay slower
        access_factor = 1.0 / (1.0 + math.log(1 + mem['access_count']))
        
        # Apply decay
        daily_decay = base_decay * importance_factor * access_factor
        decay = math.pow(daily_decay, hours_since_access / 24.0)
        
        # Update retrieval strength
        mem['retrieval_strength'] *= decay
        
        # Ensure strength stays in valid range
        mem['retrieval_strength'] = max(0.0, min(1.0, mem['retrieval_strength']))

def forget_memories(self, threshold=0.1):
    """Remove memories with strength below threshold."""
    before = len(self.episodic_memory)
    self.episodic_memory = [
        mem for mem in self.episodic_memory
        if mem['retrieval_strength'] >= threshold:
    ]:
    return before - len(self.episodic_memory)  # Number forgotten:
``````python
memory_id = memory.add_episodic_memory(
    emotion={
        'vector': [0.1, 0.8, 0.3, ...],
        'intensity': 0.9,
        'dominance': 0.2,
        'label': 'excitement'
    },
    context={
        'text': 'Going on vacation tomorrow!',
        'participants': ['family'],
        'location': 'home',
        'environment': 'personal',
        'sensory': {
            'visual': ['suitcase', 'sunset'],
            'auditory': ['laughing', 'music'],
            'tactile': ['fabric', 'breeze']
        }
    },
    importance=0.7,
    tags=['vacation', 'family', 'excitement']
)
``````python
# Find memories related to work stress
work_stress_memories = memory.search_by_tags(
    tags=['work', 'stress'],
    min_relevance=0.6,
    limit=5
)

# Get memory details
for mem in work_stress_memories:
    print(f"Memory {mem['id']}:")
    print(f"  Emotion: {mem['emotion']['label']} ({mem['emotion']['intensity']:.2f})")
    print(f"  Context: {mem['context']['text']}")
    print(f"  Last accessed: {mem['last_accessed']}")
``````python
# Run consolidation during idle periods
if system.is_idle():
    stats = memory.consolidate_memories(
        batch_size=50,
        learning_rate=0.01,
        forget_threshold=0.15
    )
    
    print(f"Consolidated {stats['processed']} memories")
    print(f"Forgot {stats['forgotten']} weak memories")
    print(f"Updated {stats['schemas_updated']} schemas")
```