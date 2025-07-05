"""
Decentralized Search Integration Service for Knowledge Base Assistant
Supports YaCy, Presearch, and other decentralized web search engines.
"""
from typing import Dict, Any, Optional
import logging
import requests

logger = logging.getLogger(__name__)

class DecentralizedSearchService:
    """
    Service for integrating with decentralized search engines (YaCy, Presearch, etc.).
    """
    YACY_URL = "http://localhost:8090/yacysearch.json"
    PRESEARCH_URL = "https://api.presearch.com/search"

    def search_yacy(self, query: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = {"query": query, "maximumRecords": 10}
        if options:
            params.update(options)
        try:
            response = requests.get(self.YACY_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"YaCy query failed: {e}")
            return {"error": str(e)}

    def search_presearch(self, query: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = {"q": query}
        if options:
            params.update(options)
        try:
            response = requests.get(self.PRESEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Presearch query failed: {e}")
            return {"error": str(e)}
