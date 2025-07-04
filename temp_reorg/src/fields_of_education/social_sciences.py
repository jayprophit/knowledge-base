"""
Social Sciences Integration: Sociology, Psychology, Political Science, Economics
"""
import networkx as nx

class SocialSciencesModule:
    def analyze_network(self, edges):
        social_network = nx.Graph()
        social_network.add_edges_from(edges)
        centrality = nx.degree_centrality(social_network)
        return centrality
