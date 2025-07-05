"""
Metadata Manager for Knowledge Base Assistant
Handles CRUD, search, deduplication, and cross-linking of metadata records.
"""
from typing import Dict, Any, Optional, List
import uuid
import logging

logger = logging.getLogger(__name__)

class MetadataManager:
    """
    In-memory metadata manager for demonstration and testing.
    Replace with persistent storage for production.
    """
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def create(self, item_id: str, metadata: Dict[str, Any]) -> str:
        if not item_id:
            item_id = str(uuid.uuid4())
        self._store[item_id] = metadata
        return item_id

    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(item_id)

    def update(self, item_id: str, updates: Dict[str, Any]) -> bool:
        if item_id not in self._store:
            return False
        self._store[item_id].update(updates)
        return True

    def delete(self, item_id: str) -> bool:
        if item_id in self._store:
            del self._store[item_id]
            return True
        return False

    def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        for metadata in self._store.values():
            if all(metadata.get(k) == v for k, v in query.items()):
                results.append(metadata)
        return results

    def deduplicate(self) -> int:
        seen = set()
        to_remove = []
        for item_id, metadata in self._store.items():
            sig = tuple(sorted(metadata.items()))
            if sig in seen:
                to_remove.append(item_id)
            else:
                seen.add(sig)
        for item_id in to_remove:
            del self._store[item_id]
        return len(to_remove)

    def cross_link(self, item_id: str, related_ids: List[str]) -> bool:
        if item_id not in self._store:
            return False
        self._store[item_id]['related'] = related_ids
        return True
