"""
Knowledge Access Module
----------------------
Provides access to external data sources (APIs, databases, web scraping) for the Advanced Engineering AI system.
"""
import requests
import networkx as nx
from typing import List, Dict

class KnowledgeAccess:
    def __init__(self):
        self.knowledge_graph = nx.DiGraph()

    def fetch_wikipedia_summary(self, topic: str) -> str:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('extract', '')
        return "Error fetching data."

    def add_knowledge_edge(self, source: str, target: str):
        self.knowledge_graph.add_edge(source, target)

    def related_topics(self, topic: str) -> List[str]:
        return list(self.knowledge_graph.successors(topic))

    def search(self, query: str) -> Dict:
        summary = self.fetch_wikipedia_summary(query)
        related = self.related_topics(query)
        return {"summary": summary, "related_topics": related}
