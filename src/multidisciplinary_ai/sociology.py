"""
Sociology Module
===============

Implements social dynamics, group behavior, and cultural analysis.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import random
from collections import defaultdict, Counter
import networkx as nx
import numpy as np

class SocialGroupType(Enum):
    """Types of social groups."""
    FAMILY = "family"
    FRIENDS = "friends"
    WORK = "work"
    COMMUNITY = "community"
    ORGANIZATION = "organization"
    ONLINE = "online_community"

class SocialTieStrength(Enum):
    """Strength of social ties."""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"

@dataclass
class SocialGroup:
    """Represents a social group with members and relationships."""
    group_id: str
    group_type: SocialGroupType
    members: Set[str]
    relationships: Dict[Tuple[str, str], SocialTieStrength]  # (member1, member2) -> strength
    attributes: Dict[str, Any]  # Additional group attributes

class SociologyModule:
    """
    Analyzes social structures, group dynamics, and cultural patterns.
    """
    
    def __init__(self):
        """Initialize the sociology module."""
        self.groups: Dict[str, SocialGroup] = {}
        self.individuals: Set[str] = set()
        self.social_graph = nx.Graph()
        self.cultural_norms = {}
        self.historical_interactions = []
        
        # Initialize with some default cultural dimensions
        self.cultural_dimensions = {
            'individualism_collectivism': 0.5,  # 0=collectivist, 1=individualist
            'power_distance': 0.5,  # 0=low, 1=high
            'uncertainty_avoidance': 0.5,  # 0=low, 1=high
            'masculinity_femininity': 0.5,  # 0=feminine, 1=masculine
            'long_term_orientation': 0.5,  # 0=short-term, 1=long-term
            'indulgence_restraint': 0.5  # 0=restraint, 1=indulgence
        }
    
    def add_group(self, 
                 group_id: str, 
                 group_type: SocialGroupType, 
                 members: List[str],
                 relationships: Optional[Dict[Tuple[str, str], SocialTieStrength]] = None,
                 attributes: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a social group to the analysis.
        
        Args:
            group_id: Unique identifier for the group
            group_type: Type of social group
            members: List of member IDs
            relationships: Optional dictionary of relationships between members
            attributes: Additional attributes of the group
        """
        members_set = set(members)
        self.individuals.update(members_set)
        
        # Initialize relationships if not provided
        if relationships is None:
            relationships = {}
            # Create some default relationships
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    relationships[(members[i], members[j])] = random.choice(list(SocialTieStrength))
        
        # Add to social graph
        for member in members:
            self.social_graph.add_node(member)
        
        for (m1, m2), strength in relationships.items():
            weight = {
                SocialTieStrength.WEAK: 1,
                SocialTieStrength.MODERATE: 2,
                SocialTieStrength.STRONG: 3
            }.get(strength, 1)
            self.social_graph.add_edge(m1, m2, weight=weight)
        
        # Create and store the group
        self.groups[group_id] = SocialGroup(
            group_id=group_id,
            group_type=group_type,
            members=members_set,
            relationships=relationships,
            attributes=attributes or {}
        )
    
    def analyze_group_dynamics(self, group_id: str) -> Dict[str, Any]:
        """
        Analyze the dynamics of a specific group.
        
        Args:
            group_id: ID of the group to analyze
            
        Returns:
            Dictionary containing group analysis
        """
        if group_id not in self.groups:
            return {"error": f"Group {group_id} not found"}
        
        group = self.groups[group_id]
        
        # Calculate basic metrics
        member_count = len(group.members)
        
        # Calculate relationship strengths
        tie_strengths = [
            strength for strength in group.relationships.values()
        ]
        
        strong_ties = sum(1 for s in tie_strengths 
                         if s == SocialTieStrength.STRONG)
        weak_ties = sum(1 for s in tie_strengths 
                       if s == SocialTieStrength.WEAK)
        
        # Calculate density (actual connections / possible connections)
        possible_connections = member_count * (member_count - 1) / 2
        actual_connections = len(tie_strengths)
        density = actual_connections / possible_connections if possible_connections > 0 else 0
        
        # Identify central members
        subgraph = self.social_graph.subgraph(group.members)
        try:
            centralities = nx.betweenness_centrality(subgraph)
            most_central = max(centralities.items(), key=lambda x: x[1])[0] if centralities else None
        except:
            most_central = None
        
        return {
            'group_id': group_id,
            'group_type': group.group_type.value,
            'member_count': member_count,
            'relationship_strength_distribution': {
                'strong': strong_ties,
                'moderate': len(tie_strengths) - strong_ties - weak_ties,
                'weak': weak_ties
            },
            'density': density,
            'most_central_member': most_central,
            'attributes': group.attributes
        }
    
    def analyze_social_network(self) -> Dict[str, Any]:
        """
        Analyze the overall social network structure.
        
        Returns:
            Dictionary containing network analysis
        """
        if len(self.social_graph) == 0:
            return {"error": "No social network data available"}
        
        # Calculate network metrics
        metrics = {
            'total_individuals': len(self.social_graph.nodes()),
            'total_relationships': len(self.social_graph.edges()),
            'average_degree': sum(dict(self.social_graph.degree()).values()) / len(self.social_graph) \
                            if len(self.social_graph) > 0 else 0,
            'is_connected': nx.is_connected(self.social_graph) if len(self.social_graph) > 0 else False,
            'clustering_coefficient': nx.average_clustering(self.social_graph) \
                                    if len(self.social_graph) > 0 else 0,
            'density': nx.density(self.social_graph) if len(self.social_graph) > 1 else 0
        }
        
        # Identify communities
        try:
            communities = nx.algorithms.community.greedy_modularity_communities(self.social_graph)
            metrics['detected_communities'] = len(communities)
            metrics['modularity'] = nx.algorithms.community.modularity(
                self.social_graph, communities
            )
        except:
            metrics['detected_communities'] = 0
            metrics['modularity'] = 0.0
        
        return metrics
    
    def predict_group_behavior(self, 
                             group_id: str, 
                             scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict how a group might behave in a given scenario.
        
        Args:
            group_id: ID of the group
            scenario: Description of the scenario
            
        Returns:
            Predicted group behavior
        """
        if group_id not in self.groups:
            return {"error": f"Group {group_id} not found"}
        
        group = self.groups[group_id]
        analysis = self.analyze_group_dynamics(group_id)
        
        # Simple prediction based on group characteristics
        # In a real system, this would be much more sophisticated
        
        # Get scenario parameters
        stress_level = scenario.get('stress_level', 0.5)  # 0-1
        novelty = scenario.get('novelty', 0.5)  # 0-1
        
        # Base response on group characteristics
        density = analysis.get('density', 0.5)
        avg_tie_strength = (
            analysis['relationship_strength_distribution']['strong'] * 1.0 +
            analysis['relationship_strength_distribution']['moderate'] * 0.5
        ) / len(group.relationships) if len(group.relationships) > 0 else 0.5
        
        # Calculate cohesion (simplified)
        cohesion = (density + avg_tie_strength) / 2
        
        # Predict response to scenario
        if stress_level > 0.7:
            if cohesion > 0.7:
                response = "The group will likely respond cohesively to the stressor, with strong in-group support."
            else:
                response = "The group may fragment under stress, with potential for conflict or disengagement."
        else:
            if novelty > 0.7:
                if cohesion > 0.7:
                    response = "The group will likely explore the novel situation together, with shared decision-making."
                else:
                    response = "Individual group members may respond differently to the novel situation."
            else:
                response = "The group will likely respond in a stable, predictable manner."
        
        return {
            'group_id': group_id,
            'scenario': scenario,
            'predicted_response': response,
            'key_factors': {
                'group_cohesion': cohesion,
                'stress_level': stress_level,
                'novelty': novelty
            },
            'confidence': 0.7  # Confidence in prediction
        }
    
    def analyze_cultural_factors(self, 
                               group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze cultural factors for a group or the entire network.
        
        Args:
            group_id: Optional ID of a specific group
            
        Returns:
            Cultural analysis
        """
        if group_id and group_id in self.groups:
            # Analyze specific group
            group = self.groups[group_id]
            cultural_profile = {
                'group_id': group_id,
                'cultural_dimensions': self.cultural_dimensions,
                'norms': group.attributes.get('norms', {}),
                'values': group.attributes.get('values', {})
            }
        else:
            # Analyze entire network
            cultural_profile = {
                'cultural_dimensions': self.cultural_dimensions,
                'group_count': len(self.groups),
                'individual_count': len(self.individuals)
            }
        
        return cultural_profile
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method that processes sociological input data.
        
        Args:
            input_data: Dictionary containing 'groups', 'individuals', or 'scenario'
            
        Returns:
            Analysis results including group dynamics and social network analysis
        """
        result = {}
        
        # Add groups if provided
        if 'groups' in input_data:
            for group_data in input_data['groups']:
                self.add_group(
                    group_id=group_data['id'],
                    group_type=SocialGroupType(group_data.get('type', 'community')),
                    members=group_data.get('members', []),
                    relationships={
                        (r['from'], r['to']): SocialTieStrength(r['strength'])
                        for r in group_data.get('relationships', [])
                    },
                    attributes=group_data.get('attributes', {})
                )
        
        # Add individuals if provided
        if 'individuals' in input_data:
            for individual in input_data['individuals']:
                self.individuals.add(individual)
                self.social_graph.add_node(individual)
        
        # Analyze specific group if requested
        if 'analyze_group' in input_data:
            group_id = input_data['analyze_group']
            result['group_analysis'] = self.analyze_group_dynamics(group_id)
        
        # Analyze social network
        if 'analyze_network' in input_data and input_data['analyze_network']:
            result['network_analysis'] = self.analyze_social_network()
        
        # Predict behavior for a scenario
        if 'scenario' in input_data:
            scenario = input_data['scenario']
            group_id = scenario.get('group_id')
            if group_id:
                result['behavior_prediction'] = self.predict_group_behavior(
                    group_id, scenario
                )
        
        # Analyze cultural factors
        if 'analyze_culture' in input_data:
            group_id = input_data['analyze_culture'].get('group_id')
            result['cultural_analysis'] = self.analyze_cultural_factors(group_id)
        
        return result
