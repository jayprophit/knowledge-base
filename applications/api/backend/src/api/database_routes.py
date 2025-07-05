"""
FastAPI routes for database operations in the Knowledge Base Assistant.
Provides API endpoints for document store, vector database, and relational database operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import logging
import os
from datetime import datetime

# Import database modules
from ..database.document_store import DocumentStore, DocumentStoreType
from ..database.vector_db import VectorDB, VectorDBType
from ..database.relational_db import RelationalDB, RelationalDBType

# Import dependencies
from .dependencies import get_document_store, get_vector_db, get_relational_db

logger = logging.getLogger(__name__)

# Define router
router = APIRouter(
    prefix="/db",
    tags=["database"],
    responses={404: {"description": "Not found"}},
)

# ----- Pydantic Models -----

class DocumentModel(BaseModel):
    """Document data model for document store operations"""
    id: Optional[str] = None
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
class VectorDocumentModel(BaseModel):
    """Vector document model for semantic search operations"""
    id: Optional[str] = None
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
class SearchQueryModel(BaseModel):
    """Search query model for database searches"""
    query: str
    collection: Optional[str] = "default"
    limit: int = 5
    filter: Optional[Dict[str, Any]] = None
    
class UserModel(BaseModel):
    """User model for relational database operations"""
    id: Optional[str] = None
    username: str
    email: Optional[str] = None
    password: str  # Will be hashed before storage

class SettingModel(BaseModel):
    """Setting model for user settings operations"""
    key: str
    value: str

# ----- Document Store Routes -----

@router.post("/documents/{collection}", response_model=Dict[str, Any])
async def create_document(
    collection: str,
    document: DocumentModel,
    doc_store: DocumentStore = Depends(get_document_store)
):
    """Create a document in the document store"""
    try:
        doc_id = doc_store.create_document(collection, document.id, {
            "content": document.content,
            "metadata": document.metadata
        })
        return {"id": doc_id, "status": "created"}
    except Exception as e:
        logger.error(f"Failed to create document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")

@router.get("/documents/{collection}/{document_id}", response_model=DocumentModel)
async def get_document(
    collection: str,
    document_id: str,
    doc_store: DocumentStore = Depends(get_document_store)
):
    """Get a document from the document store"""
    doc = doc_store.get_document(collection, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    return DocumentModel(
        id=document_id,
        content=doc.get("content", {}),
        metadata=doc.get("metadata", {})
    )

@router.put("/documents/{collection}/{document_id}", response_model=Dict[str, Any])
async def update_document(
    collection: str,
    document_id: str,
    document: DocumentModel,
    doc_store: DocumentStore = Depends(get_document_store)
):
    """Update a document in the document store"""
    success = doc_store.update_document(collection, document_id, {
        "content": document.content,
        "metadata": document.metadata
    })
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found or update failed")
    
    return {"id": document_id, "status": "updated"}

@router.delete("/documents/{collection}/{document_id}", response_model=Dict[str, Any])
async def delete_document(
    collection: str,
    document_id: str,
    doc_store: DocumentStore = Depends(get_document_store)
):
    """Delete a document from the document store"""
    success = doc_store.delete_document(collection, document_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found or deletion failed")
    
    return {"id": document_id, "status": "deleted"}

@router.post("/documents/{collection}/query", response_model=List[DocumentModel])
async def query_documents(
    collection: str,
    query: Dict[str, Any],
    limit: int = Query(100, ge=1, le=1000),
    doc_store: DocumentStore = Depends(get_document_store)
):
    """Query documents from the document store"""
    docs = doc_store.query_documents(collection, query, limit)
    
    return [
        DocumentModel(
            id=doc.get("id", ""),
            content=doc.get("content", {}),
            metadata=doc.get("metadata", {})
        ) for doc in docs
    ]

# ----- Vector Database Routes -----

@router.post("/vectors/add", response_model=Dict[str, Any])
async def add_vector_documents(
    documents: List[VectorDocumentModel],
    collection: str = Query("knowledge_base"),
    vector_db: VectorDB = Depends(get_vector_db)
):
    """Add documents with embeddings to the vector database"""
    # In a real implementation, we would generate embeddings here if not provided
    # For now, we'll assume embeddings are provided or use mock ones
    
    docs = []
    embeddings = []
    
    for doc in documents:
        doc_dict = {
            "id": doc.id or f"doc_{len(docs)}",
            "content": doc.content,
            "metadata": doc.metadata
        }
        docs.append(doc_dict)
        
        # Use provided embedding or mock one (in production, we'd generate real embeddings)
        if doc.embedding:
            embeddings.append(doc.embedding)
        else:
            # Mock embedding (in production, we'd use a text embedding model)
            mock_embedding = [0.1, 0.2, 0.3] * 512  # 1536 dim
            embeddings.append(mock_embedding)
    
    success = vector_db.add_documents(docs, embeddings)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add documents to vector database")
    
    return {"status": "success", "count": len(docs)}

@router.post("/vectors/search", response_model=List[Dict[str, Any]])
async def search_vectors(
    query: SearchQueryModel,
    vector_db: VectorDB = Depends(get_vector_db)
):
    """Search for similar documents in the vector database"""
    # In a real implementation, we would generate query embedding here
    # For now, we'll use a mock embedding
    
    # Mock query embedding (in production, we'd use a text embedding model)
    query_embedding = [0.1, 0.2, 0.3] * 512  # 1536 dim
    
    results = vector_db.search(query_embedding, limit=query.limit)
    
    return results

@router.delete("/vectors/{document_id}", response_model=Dict[str, Any])
async def delete_vector_document(
    document_id: str,
    vector_db: VectorDB = Depends(get_vector_db)
):
    """Delete a document from the vector database"""
    success = vector_db.delete_document(document_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found or deletion failed")
    
    return {"id": document_id, "status": "deleted"}

# ----- Relational Database Routes -----

@router.post("/users", response_model=Dict[str, Any])
async def create_user(
    user: UserModel,
    db: RelationalDB = Depends(get_relational_db)
):
    """Create a new user in the relational database"""
    # In a real implementation, we would hash the password here
    password_hash = f"hashed_{user.password}"  # Mock hash - NEVER do this in production
    
    user_id = user.id or f"user_{int(datetime.now().timestamp())}"
    
    success = db.create_user(user_id, user.username, password_hash, user.email)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return {"id": user_id, "username": user.username, "status": "created"}

@router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user(
    user_id: str,
    db: RelationalDB = Depends(get_relational_db)
):
    """Get user details from the relational database"""
    user = db.get_user(user_id=user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    # Remove sensitive fields
    if "password_hash" in user:
        del user["password_hash"]
    
    return user

@router.put("/users/{user_id}", response_model=Dict[str, Any])
async def update_user(
    user_id: str,
    user_data: Dict[str, Any],
    db: RelationalDB = Depends(get_relational_db)
):
    """Update user details in the relational database"""
    # If password is in the update data, hash it
    if "password" in user_data:
        user_data["password_hash"] = f"hashed_{user_data['password']}"  # Mock hash
        del user_data["password"]
    
    success = db.update_user(user_id, user_data)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found or update failed")
    
    return {"id": user_id, "status": "updated"}

@router.post("/users/{user_id}/settings", response_model=Dict[str, Any])
async def save_user_setting(
    user_id: str,
    setting: SettingModel,
    db: RelationalDB = Depends(get_relational_db)
):
    """Save a user setting in the relational database"""
    success = db.create_or_update_setting(user_id, setting.key, setting.value)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save setting")
    
    return {"user_id": user_id, "key": setting.key, "value": setting.value, "status": "saved"}

@router.get("/users/{user_id}/settings", response_model=Dict[str, str])
async def get_user_settings(
    user_id: str,
    db: RelationalDB = Depends(get_relational_db)
):
    """Get all settings for a user from the relational database"""
    settings = db.get_settings(user_id)
    
    return settings
