"""
Advanced Engineering AI System
-----------------------------
Integrates knowledge access, knowledge graph, and reasoning for professional-level engineering, science, and patent knowledge.
"""
from .knowledge_access import KnowledgeAccess

class AdvancedEngineeringAI:
    def __init__(self):
        self.knowledge_access = KnowledgeAccess()

    def handle_query(self, user_query: str):
        """
        Fetch information and related topics for a user query.
        """
        return self.knowledge_access.search(user_query)
