"""
Dependencies for FastAPI endpoints in the Knowledge Base Assistant.
Provides dependency injection functions for database connections and other services.
"""

from fastapi import Depends
from functools import lru_cache
import os
from typing import Optional

# Import database modules
from ..database.document_store import DocumentStore, DocumentStoreType
from ..database.vector_db import VectorDB, VectorDBType
from ..database.relational_db import RelationalDB, RelationalDBType

@lru_cache(maxsize=1)
def get_document_store() -> DocumentStore:
    """
    Get a singleton instance of DocumentStore.
    Uses environment variables for configuration, falling back to defaults.
    
    Returns:
        DocumentStore: Initialized document store
    """
    store_type = os.getenv("DOCUMENT_STORE_TYPE", "local_json")
    connection_string = os.getenv("DOCUMENT_STORE_CONNECTION", None)
    database_name = os.getenv("DOCUMENT_STORE_DATABASE", "knowledge_assistant")
    
    return DocumentStore(
        store_type=store_type,
        connection_string=connection_string,
        database_name=database_name
    )

@lru_cache(maxsize=1)
def get_vector_db() -> VectorDB:
    """
    Get a singleton instance of VectorDB.
    Uses environment variables for configuration, falling back to defaults.
    
    Returns:
        VectorDB: Initialized vector database
    """
    db_type = os.getenv("VECTOR_DB_TYPE", "faiss")
    connection_string = os.getenv("VECTOR_DB_CONNECTION", None)
    collection_name = os.getenv("VECTOR_DB_COLLECTION", "knowledge_base")
    embedding_dim = int(os.getenv("VECTOR_DB_EMBEDDING_DIM", "1536"))
    
    return VectorDB(
        db_type=db_type,
        connection_string=connection_string,
        collection_name=collection_name,
        embedding_dim=embedding_dim
    )

@lru_cache(maxsize=1)
def get_relational_db() -> RelationalDB:
    """
    Get a singleton instance of RelationalDB.
    Uses environment variables for configuration, falling back to defaults.
    
    Returns:
        RelationalDB: Initialized relational database
    """
    db_type = os.getenv("RELATIONAL_DB_TYPE", "sqlite")
    connection_string = os.getenv("RELATIONAL_DB_CONNECTION", None)
    
    return RelationalDB(
        db_type=db_type,
        connection_string=connection_string
    )

def get_api_key() -> Optional[str]:
    """
    Get API key from request header or query parameter.
    Used for authorization middleware.
    
    Returns:
        Optional[str]: API key if present
    """
    # In a real implementation, this would check headers, etc.
    return None  # Placeholder for actual authentication logic
