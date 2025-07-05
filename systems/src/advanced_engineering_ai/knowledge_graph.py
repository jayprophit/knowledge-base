"""
Engineering Knowledge Graph Module
---------------------------------
Provides a knowledge graph structure for representing engineering, scientific, and patent knowledge.
"""
import networkx as nx
from typing import List, Tuple

class EngineeringKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_concept(self, concept: str):
        self.graph.add_node(concept)

    def add_relationship(self, source: str, target: str, relation: str):
        self.graph.add_edge(source, target, relation=relation)

    def get_related(self, concept: str) -> List[str]:
        return list(self.graph.successors(concept))

    def all_concepts(self) -> List[str]:
        return list(self.graph.nodes())
