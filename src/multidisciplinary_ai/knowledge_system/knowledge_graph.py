"""
Knowledge Graph Module
=====================

Implements a temporal knowledge graph for storing and querying cross-disciplinary
knowledge across different time periods, from ancient to future concepts.
"""

import networkx as nx
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

class KnowledgeType(Enum):
    """Types of knowledge that can be represented in the graph."""
    CONCEPT = "concept"
    ENTITY = "entity"
    EVENT = "event"
    THEORY = "theory"
    INNOVATION = "innovation"
    PATENT = "patent"
    PAPER = "paper"
    PERSON = "person"
    ORGANIZATION = "organization"
    TECHNOLOGY = "technology"

@dataclass
class TemporalContext:
    """Temporal context for knowledge graph nodes and edges."""
    start_time: Optional[Union[datetime, float]] = None  # None means beginning of time
    end_time: Optional[Union[datetime, float]] = None    # None means present/future
    confidence: float = 1.0
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

class KnowledgeGraph:
    """
    A temporal knowledge graph for cross-disciplinary knowledge representation.
    
    This graph supports:
    - Temporal reasoning (ancient → future concepts)
    - Multi-disciplinary knowledge integration
    - Confidence scoring and source tracking
    - Complex relationship modeling
    """
    
    def __init__(self):
        """Initialize an empty knowledge graph."""
        self.graph = nx.MultiDiGraph()
        self.node_types: Dict[str, KnowledgeType] = {}
        self.temporal_contexts = nx.Graph()  # Stores temporal data for nodes and edges
        self.node_counter = 0
        
    def add_node(self, 
                name: str, 
                node_type: KnowledgeType,
                temporal_context: Optional[TemporalContext] = None,
                **attrs) -> str:
        """
        Add a node to the knowledge graph.
        
        Args:
            name: Name/identifier of the node
            node_type: Type of knowledge this node represents
            temporal_context: Temporal context for this node
            **attrs: Additional node attributes
            
        Returns:
            str: The node ID
        """
        node_id = f"{node_type.value}_{self.node_counter}"
        self.node_counter += 1
        
        # Add node with attributes
        self.graph.add_node(node_id, name=name, type=node_type, **attrs)
        self.node_types[node_id] = node_type
        
        # Store temporal context if provided
        if temporal_context:
            self.temporal_contexts.add_node(node_id, **temporal_context.__dict__)
            
        return node_id
    
    def add_edge(self, 
                source_id: str, 
                target_id: str,
                relation_type: str,
                temporal_context: Optional[TemporalContext] = None,
                **attrs) -> None:
        """
        Add a directed edge between two nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            relation_type: Type of relationship
            temporal_context: Temporal context for this edge
            **attrs: Additional edge attributes
        """
        if source_id not in self.graph or target_id not in self.graph:
            raise ValueError("Source and target nodes must exist in the graph")
            
        # Add edge with attributes
        edge_key = f"{relation_type}_{len(self.graph[source_id][target_id])}"
        self.graph.add_edge(source_id, target_id, key=edge_key, 
                          relation_type=relation_type, **attrs)
        
        # Store temporal context if provided
        if temporal_context:
            edge_data = temporal_context.__dict__
            if not self.temporal_contexts.has_edge(source_id, target_id):
                self.temporal_contexts.add_edge(source_id, target_id, **{edge_key: edge_data})
            else:
                self.temporal_contexts[source_id][target_id][edge_key] = edge_data
    
    def query(self, 
             query: str,
             time_period: Optional[Tuple[Optional[float], Optional[float]]] = None,
             max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Query the knowledge graph.
        
        Args:
            query: Natural language query or node name pattern
            time_period: Optional (start_time, end_time) tuple to filter by time
            max_results: Maximum number of results to return
            
        Returns:
            List of matching nodes with their relationships
        """
        # Simple implementation - can be enhanced with NLP
        results = []
        
        # Search nodes by name or attributes
        for node_id, attrs in self.graph.nodes(data=True):
            if query.lower() in attrs.get('name', '').lower():
                result = {
                    'id': node_id,
                    'name': attrs['name'],
                    'type': attrs['type'].value,
                    'relationships': []
                }
                
                # Get temporal context if available
                if node_id in self.temporal_contexts.nodes:
                    result['temporal_context'] = self.temporal_contexts.nodes[node_id]
                
                # Get relationships
                for _, neighbor, edge_data in self.graph.out_edges(node_id, data=True):
                    target_name = self.graph.nodes[neighbor].get('name', neighbor)
                    result['relationships'].append({
                        'relation': edge_data['relation_type'],
                        'target': target_name,
                        'target_type': self.graph.nodes[neighbor].get('type', '').value
                    })
                
                results.append(result)
                
                if len(results) >= max_results:
                    break
        
        return results
    
    def get_temporal_snapshot(self, 
                            time_point: Optional[float] = None) -> 'KnowledgeGraph':
        """
        Get a snapshot of the knowledge graph valid at a specific time.
        
        Args:
            time_point: Time point for the snapshot (None for all time)
            
        Returns:
            A new KnowledgeGraph containing only nodes and edges valid at time_point
        """
        snapshot = KnowledgeGraph()
        
        # Add nodes valid at time_point
        for node_id, attrs in self.graph.nodes(data=True):
            node_valid = True
            
            # Check temporal validity if temporal context exists
            if node_id in self.temporal_contexts.nodes:
                tc = self.temporal_contexts.nodes[node_id]
                if time_point is not None:
                    if tc.get('start_time') is not None and time_point < tc['start_time']:
                        node_valid = False
                    if tc.get('end_time') is not None and time_point > tc['end_time']:
                        node_valid = False
            
            if node_valid:
                snapshot.graph.add_node(node_id, **attrs)
                snapshot.node_types[node_id] = attrs['type']
        
        # Add edges valid at time_point
        for src, tgt, edge_data in self.graph.edges(data=True):
            if src in snapshot.graph and tgt in snapshot.graph:
                edge_valid = True
                edge_key = edge_data.get('key', '')
                
                # Check temporal validity if temporal context exists for this edge
                if (src, tgt) in self.temporal_contexts.edges and edge_key:
                    tc = self.temporal_contexts[src][tgt].get(edge_key, {})
                    if time_point is not None:
                        if tc.get('start_time') is not None and time_point < tc['start_time']:
                            edge_valid = False
                        if tc.get('end_time') is not None and time_point > tc['end_time']:
                            edge_valid = False
                
                if edge_valid:
                    snapshot.graph.add_edge(src, tgt, **edge_data)
        
        return snapshot
    
    def integrate_external_knowledge(self, 
                                   source: str,
                                   knowledge_data: List[Dict[str, Any]],
                                   confidence: float = 0.9) -> None:
        """
        Integrate knowledge from an external source into the graph.
        
        Args:
            source: Source identifier (e.g., 'wikipedia', 'arxiv', 'patent_office')
            knowledge_data: List of knowledge items to integrate
            confidence: Confidence score for this source (0.0 to 1.0)
        """
        for item in knowledge_data:
            # This is a simplified example - would be customized based on source format
            node_type = KnowledgeType(item.get('type', 'concept').upper())
            
            # Create temporal context
            tc = TemporalContext(
                start_time=item.get('start_time'),
                end_time=item.get('end_time'),
                confidence=confidence,
                source=source,
                metadata=item.get('metadata', {})
            )
            
            # Add node
            node_id = self.add_node(
                name=item['name'],
                node_type=node_type,
                temporal_context=tc,
                **item.get('attributes', {})
            )
            
            # Add relationships
            for rel in item.get('relationships', []):
                target_name = rel['target']
                target_type = KnowledgeType(rel.get('target_type', 'concept').upper())
                
                # Find or create target node
                target_id = None
                for nid, attrs in self.graph.nodes(data=True):
                    if attrs.get('name') == target_name and self.node_types.get(nid) == target_type:
                        target_id = nid
                        break
                
                if not target_id:
                    target_id = self.add_node(
                        name=target_name,
                        node_type=target_type,
                        temporal_context=TemporalContext(confidence=0.7)  # Lower confidence for inferred nodes
                    )
                
                # Add relationship edge
                self.add_edge(
                    source_id=node_id,
                    target_id=target_id,
                    relation_type=rel['type'],
                    temporal_context=tc
                )
    
    def visualize(self, max_nodes: int = 100) -> None:
        """
        Generate a visualization of the knowledge graph.
        
        Note: This is a simplified implementation. For large graphs, consider
        using specialized visualization tools like Gephi or Neo4j.
        
        Args:
            max_nodes: Maximum number of nodes to include in the visualization
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.colors import to_rgba
            
            # Create a subgraph if needed to limit size
            if len(self.graph) > max_nodes:
                nodes = list(self.graph.nodes())[:max_nodes]
                G = self.graph.subgraph(nodes)
            else:
                G = self.graph
            
            # Set up plot
            plt.figure(figsize=(12, 12))
            pos = nx.spring_layout(G, k=0.3, iterations=50)
            
            # Draw nodes with different colors by type
            node_colors = {
                KnowledgeType.CONCEPT: 'lightblue',
                KnowledgeType.ENTITY: 'lightgreen',
                KnowledgeType.EVENT: 'lightcoral',
                KnowledgeType.THEORY: 'plum',
                KnowledgeType.INNOVATION: 'gold',
                KnowledgeType.PATENT: 'orange',
                KnowledgeType.PAPER: 'lightgray',
                KnowledgeType.PERSON: 'lightpink',
                KnowledgeType.ORGANIZATION: 'lightseagreen',
                KnowledgeType.TECHNOLOGY: 'lightsalmon'
            }
            
            # Draw nodes
            for node_type in KnowledgeType:
                nodes_of_type = [n for n, attrs in G.nodes(data=True) 
                               if attrs.get('type') == node_type]
                if nodes_of_type:
                    nx.draw_networkx_nodes(
                        G, pos, 
                        nodelist=nodes_of_type,
                        node_color=node_colors.get(node_type, 'gray'),
                        node_size=500,
                        alpha=0.8,
                        label=node_type.value
                    )
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
            
            # Draw labels
            labels = {n: attrs['name'] for n, attrs in G.nodes(data=True)}
            nx.draw_networkx_labels(G, pos, labels, font_size=8)
            
            # Add legend
            plt.legend(scatterpoints=1, frameon=False, labelspacing=1)
            plt.axis('off')
            plt.title("Knowledge Graph Visualization")
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("Visualization requires matplotlib. Install with: pip install matplotlib")
    
    def save_to_file(self, filename: str) -> None:
        """Save the knowledge graph to a file."""
        import pickle
        
        data = {
            'graph': nx.node_link_data(self.graph),
            'node_types': self.node_types,
            'temporal_contexts': nx.node_link_data(self.temporal_contexts),
            'node_counter': self.node_counter
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'KnowledgeGraph':
        """Load a knowledge graph from a file."""
        import pickle
        
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        
        kg = cls()
        kg.graph = nx.node_link_graph(data['graph'])
        kg.node_types = data['node_types']
        kg.temporal_contexts = nx.node_link_graph(data['temporal_contexts'])
        kg.node_counter = data['node_counter']
        
        return kg
