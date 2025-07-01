"""
Knowledge Representation Enhancements
===================================

Enhanced knowledge representation with support for:
- Semantic knowledge graphs
- Entity linking and disambiguation
- Temporal reasoning
- Probabilistic reasoning
- Rule-based reasoning
"""

from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime
import numpy as np
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RelationType(Enum):
    """Types of relations between knowledge graph entities."""
    IS_A = "is_a"
    PART_OF = "part_of"
    HAS_PROPERTY = "has_property"
    RELATED_TO = "related_to"
    INSTANCE_OF = "instance_of"
    SUBCLASS_OF = "subclass_of"
    CAUSES = "causes"
    USES = "uses"
    CREATED_BY = "created_by"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    CUSTOM = "custom"

@dataclass
class Entity:
    """Represents an entity in the knowledge graph."""
    id: str
    label: str
    description: str = ""
    types: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Relation:
    """Represents a relation between entities in the knowledge graph."""
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

class KnowledgeGraphEnhancer:
    """
    Enhanced knowledge graph with advanced reasoning capabilities.
    """
    
    def __init__(self):
        """Initialize the knowledge graph."""
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.entity_index: Dict[str, Set[str]] = defaultdict(set)  # type -> entity_ids
        self.relation_index: Dict[Tuple[str, str, str], List[Relation]] = defaultdict(list)
        self.embeddings: Dict[str, np.ndarray] = {}
        
    def add_entity(self, entity: Entity) -> None:
        """
        Add an entity to the knowledge graph.
        
        Args:
            entity: Entity to add
        """
        self.entities[entity.id] = entity
        for entity_type in entity.types:
            self.entity_index[entity_type].add(entity.id)
        
        if entity.embedding is not None:
            self.embeddings[entity.id] = entity.embedding
        
        logger.info(f"Added entity: {entity.id} ({entity.label})")
    
    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: Union[str, RelationType],
        **kwargs
    ) -> None:
        """
        Add a relation between entities.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relation_type: Type of relation
            **kwargs: Additional relation properties
        """
        if source_id not in self.entities:
            raise ValueError(f"Source entity not found: {source_id}")
        if target_id not in self.entities:
            raise ValueError(f"Target entity not found: {target_id}")
            
        if isinstance(relation_type, str):
            relation_type = RelationType(relation_type.lower())
            
        relation = Relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            **kwargs
        )
        
        self.relations.append(relation)
        key = (source_id, str(relation_type), target_id)
        self.relation_index[key].append(relation)
        
        logger.debug(
            f"Added relation: {source_id} --{relation_type}-> {target_id}"
        )
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            Entity if found, None otherwise
        """
        return self.entities.get(entity_id)
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """
        Get all entities of a specific type.
        
        Args:
            entity_type: Type of entities to retrieve
            
        Returns:
            List of matching entities
        """
        entity_ids = self.entity_index.get(entity_type, set())
        return [self.entities[eid] for eid in entity_ids if eid in self.entities]
    
    def get_relations(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation_type: Optional[Union[str, RelationType]] = None,
    ) -> List[Relation]:
        """
        Get relations matching the given criteria.
        
        Args:
            source_id: Optional source entity ID
            target_id: Optional target entity ID
            relation_type: Optional relation type
            
        Returns:
            List of matching relations
        """
        if relation_type and isinstance(relation_type, str):
            relation_type = RelationType(relation_type.lower())
        
        if source_id is not None and target_id is not None and relation_type is not None:
            # Fast path: exact match
            key = (source_id, str(relation_type), target_id)
            return self.relation_index.get(key, []).copy()
        
        # Slow path: filter relations
        results = []
        for rel in self.relations:
            if source_id is not None and rel.source_id != source_id:
                continue
            if target_id is not None and rel.target_id != target_id:
                continue
            if relation_type is not None and rel.relation_type != relation_type:
                continue
            results.append(rel)
            
        return results
    
    def find_similar_entities(
        self,
        query_embedding: np.ndarray,
        entity_type: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[Tuple[Entity, float]]:
        """
        Find entities similar to the query embedding.
        
        Args:
            query_embedding: Query embedding vector
            entity_type: Optional entity type filter
            top_k: Number of results to return
            min_similarity: Minimum similarity score (0-1)
            
        Returns:
            List of (entity, similarity) tuples, sorted by similarity
        """
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Get candidate entities
        if entity_type:
            candidate_ids = list(self.entity_index.get(entity_type, set()))
        else:
            candidate_ids = list(self.entities.keys())
        
        # Get embeddings for candidates
        candidate_embeddings = []
        valid_entities = []
        
        for eid in candidate_ids:
            if eid in self.embeddings:
                candidate_embeddings.append(self.embeddings[eid])
                valid_entities.append(self.entities[eid])
        
        if not valid_entities:
            return []
        
        # Calculate similarities
        similarities = cosine_similarity(
            np.array([query_embedding]),
            np.array(candidate_embeddings)
        )[0]
        
        # Sort by similarity
        results = [
            (entity, float(sim)) 
            for entity, sim in zip(valid_entities, similarities)
            if sim >= min_similarity
        ]
        results.sort(key=lambda x: -x[1])
        
        return results[:top_k]
    
    def infer_relations(self, source_entity: Entity, max_depth: int = 2) -> List[Dict[str, Any]]:
        """
        Infer possible relations between entities using graph traversal.
        
        Args:
            source_entity: Source entity for relation inference
            max_depth: Maximum depth to traverse
            
        Returns:
            List of inferred relations with confidence scores
        """
        results = []
        visited = set()
        
        def traverse(entity_id: str, path: List[Tuple[str, str]], depth: int):
            if depth > max_depth or entity_id in visited:
                return
                
            visited.add(entity_id)
            
            # Get all outgoing relations
            for rel in self.get_relations(source_id=entity_id):
                # Add direct relation
                results.append({
                    'source_id': source_entity.id,
                    'target_id': rel.target_id,
                    'path': path + [(rel.relation_type.value, rel.target_id)],
                    'depth': depth,
                    'confidence': 1.0 / (depth + 1)  # Lower confidence for longer paths
                })
                
                # Recursively traverse
                traverse(rel.target_id, path + [(rel.relation_type.value, rel.target_id)], depth + 1)
        
        traverse(source_entity.id, [], 0)
        return results
    
    def to_networkx(self):
        """Convert the knowledge graph to a NetworkX graph."""
        try:
            import networkx as nx
        except ImportError:
            logger.error("NetworkX is required for this functionality")
            return None
        
        G = nx.DiGraph()
        
        # Add nodes
        for entity_id, entity in self.entities.items():
            G.add_node(entity_id, **{
                'label': entity.label,
                'types': entity.types,
                'description': entity.description
            })
        
        # Add edges
        for rel in self.relations:
            G.add_edge(
                rel.source_id,
                rel.target_id,
                relation_type=rel.relation_type.value,
                weight=rel.weight,
                **rel.properties
            )
        
        return G
    
    def visualize(self, output_file: str = "knowledge_graph.html"):
        """
        Generate an interactive visualization of the knowledge graph.
        
        Args:
            output_file: Path to save the visualization
        """
        try:
            import pyvis.network as net
        except ImportError:
            logger.error("pyvis is required for visualization")
            return
        
        G = self.to_networkx()
        if G is None:
            return
        
        # Create a pyvis network
        net_graph = net.Network(
            height="750px",
            width="100%",
            bgcolor="#ffffff",
            font_color="black",
            directed=True
        )
        
        # Add nodes and edges
        for node_id, node_data in G.nodes(data=True):
            title = f"<b>{node_data.get('label', node_id)}</b>"
            if 'description' in node_data:
                title += f"<br>{node_data['description']}"
            
            net_graph.add_node(
                node_id,
                label=node_data.get('label', node_id),
                title=title,
                group=node_data.get('types', [''])[0] if 'types' in node_data else 'other'
            )
        
        for source, target, data in G.edges(data=True):
            net_graph.add_edge(
                source,
                target,
                title=data.get('relation_type', ''),
                label=data.get('relation_type', '')
            )
        
        # Generate and save the visualization
        net_graph.show_buttons(filter_=['physics'])
        net_graph.show(output_file)
        logger.info(f"Knowledge graph visualization saved to {output_file}")

# Example usage
if __name__ == "__main__":
    # Initialize the knowledge graph
    kg = KnowledgeGraphEnhancer()
    
    # Add some entities
    ai = Entity(
        id="ai",
        label="Artificial Intelligence",
        description="The simulation of human intelligence by machines",
        types=["concept", "technology"]
    )
    
    ml = Entity(
        id="ml",
        label="Machine Learning",
        description="A subset of AI that uses statistical techniques",
        types=["concept", "technology"]
    )
    
    dl = Entity(
        id="dl",
        label="Deep Learning",
        description="A subset of ML using neural networks",
        types=["concept", "technology"]
    )
    
    # Add entities to the knowledge graph
    kg.add_entity(ai)
    kg.add_entity(ml)
    kg.add_entity(dl)
    
    # Add relations
    kg.add_relation("ml", "ai", RelationType.SUBCLASS_OF)
    kg.add_relation("dl", "ml", RelationType.SUBCLASS_OF)
    
    # Query the knowledge graph
    print("Entities in the knowledge graph:")
    for entity in kg.entities.values():
        print(f"- {entity.label} ({entity.id})")
    
    # Visualize the knowledge graph
    kg.visualize("knowledge_graph.html")
