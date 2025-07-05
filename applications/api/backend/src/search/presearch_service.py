"""
Presearch Integration Service for Knowledge Base Assistant
Provides interface for querying Presearch decentralized search engine.
"""
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PresearchService:
    """
    Service for integrating with Presearch decentralized search engine.
    """
    BASE_URL = "https://api.presearch.com/search"

    def search(self, query: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = {"q": query}
        if options:
            params.update(options)
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Presearch query failed: {e}")
            return {"error": str(e)}
