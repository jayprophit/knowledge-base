"""
Metadata Service for Knowledge Base Assistant
Provides CRUD and advanced operations for metadata management (SEO, deduplication, cross-linking)
"""

from typing import Dict, Any, Optional, List
import uuid
import logging
from ..metadata.metadata_manager import MetadataManager

logger = logging.getLogger(__name__)

class MetadataService:
    """
    Service for managing metadata for documents, code, and assets.
    Supports CRUD, SEO, deduplication, and cross-linking.
    """
    def __init__(self, manager: Optional[MetadataManager] = None):
        self.manager = manager or MetadataManager()

    def create_metadata(self, item_id: str, metadata: Dict[str, Any]) -> str:
        """Create metadata for an item."""
        return self.manager.create(item_id, metadata)

    def get_metadata(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for an item."""
        return self.manager.get(item_id)

    def update_metadata(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """Update metadata for an item."""
        return self.manager.update(item_id, updates)

    def delete_metadata(self, item_id: str) -> bool:
        """Delete metadata for an item."""
        return self.manager.delete(item_id)

    def search_metadata(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search metadata records matching query."""
        return self.manager.search(query)

    def deduplicate_metadata(self) -> int:
        """Deduplicate metadata records."""
        return self.manager.deduplicate()

    def cross_link(self, item_id: str, related_ids: List[str]) -> bool:
        """Cross-link metadata between items."""
        return self.manager.cross_link(item_id, related_ids)
