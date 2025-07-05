"""
Document store for unstructured data in the Knowledge Base Assistant.
Handles user data, conversation history, multimodal assets, etc.
Supports MongoDB, Firestore, and local JSON backends.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentStoreType(Enum):
    MONGODB = "mongodb"
    FIRESTORE = "firestore"
    LOCAL_JSON = "local_json"

class DocumentStore:
    """
    Document store for unstructured data like conversations, user data, etc.
    Supports MongoDB, Firestore, and local JSON file storage.
    """
    def __init__(self,
                 store_type: Union[DocumentStoreType, str] = DocumentStoreType.LOCAL_JSON,
                 connection_string: Optional[str] = None,
                 database_name: str = "knowledge_assistant"):
        if isinstance(store_type, str):
            try:
                store_type = DocumentStoreType(store_type.lower())
            except ValueError:
                logger.warning(f"Unknown store type {store_type}, falling back to LOCAL_JSON")
                store_type = DocumentStoreType.LOCAL_JSON
        self.store_type = store_type
        self.database_name = database_name
        self.client = None
        self.db = None
        if connection_string is None and store_type == DocumentStoreType.LOCAL_JSON:
            connection_string = os.path.join(os.path.dirname(__file__), "../../data/document_store")
        self.connection_string = connection_string
        self._connect()

    def _connect(self):
        try:
            if self.store_type == DocumentStoreType.MONGODB:
                self._connect_mongodb()
            elif self.store_type == DocumentStoreType.FIRESTORE:
                self._connect_firestore()
            elif self.store_type == DocumentStoreType.LOCAL_JSON:
                self._connect_local_json()
            else:
                raise ValueError(f"Unsupported document store type: {self.store_type}")
            logger.info(f"Connected to {self.store_type.value} document store")
        except Exception as e:
            logger.error(f"Failed to connect to document store: {e}")
            raise

    def _connect_mongodb(self):
        try:
            # Placeholder for actual MongoDB client initialization
            # from pymongo import MongoClient
            # self.client = MongoClient(self.connection_string)
            # self.db = self.client[self.database_name]
            logger.info("MongoDB client initialized")
        except ImportError:
            logger.error("MongoDB client not installed. Run: pip install pymongo")
            raise

    def _connect_firestore(self):
        try:
            # Placeholder for actual Firestore client initialization
            # from google.cloud import firestore
            # self.client = firestore.Client()
            # self.db = self.client
            logger.info("Firestore client initialized")
        except ImportError:
            logger.error("Firestore client not installed. Run: pip install google-cloud-firestore")
            raise

    def _connect_local_json(self):
        try:
            os.makedirs(self.connection_string, exist_ok=True)
            self.client = self.connection_string
            self.db = {}
            logger.info("Local JSON document store initialized")
        except Exception as e:
            logger.error(f"Failed to initialize local JSON store: {e}")
            raise

    def _get_collection_path(self, collection: str) -> str:
        return os.path.join(self.connection_string, f"{collection}.json")

    def _load_collection(self, collection: str) -> Dict[str, Any]:
        path = self._get_collection_path(collection)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in {path}, returning empty collection")
                return {}
        return {}

    def _save_collection(self, collection: str, data: Dict[str, Any]):
        path = self._get_collection_path(collection)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def create_document(self, collection: str, document_id: Optional[str], data: Dict[str, Any]) -> str:
        try:
            if 'created_at' not in data:
                data['created_at'] = datetime.now().isoformat()
            if 'updated_at' not in data:
                data['updated_at'] = data['created_at']
            if self.store_type == DocumentStoreType.MONGODB:
                # Placeholder for MongoDB insert
                pass
            elif self.store_type == DocumentStoreType.FIRESTORE:
                # Placeholder for Firestore add
                pass
            elif self.store_type == DocumentStoreType.LOCAL_JSON:
                if collection not in self.db:
                    self.db[collection] = self._load_collection(collection)
                if not document_id:
                    document_id = f"{int(datetime.now().timestamp())}_{len(self.db[collection])}"
                self.db[collection][document_id] = data
                self._save_collection(collection, self.db[collection])
                return document_id
            logger.info(f"Created document in {collection} with ID {document_id}")
            return document_id
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise

    def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        try:
            if self.store_type == DocumentStoreType.MONGODB:
                pass
            elif self.store_type == DocumentStoreType.FIRESTORE:
                pass
            elif self.store_type == DocumentStoreType.LOCAL_JSON:
                if collection not in self.db:
                    self.db[collection] = self._load_collection(collection)
                return self.db[collection].get(document_id)
            logger.info(f"Retrieved document from {collection} with ID {document_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None

    def update_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        try:
            data['updated_at'] = datetime.now().isoformat()
            if self.store_type == DocumentStoreType.MONGODB:
                pass
            elif self.store_type == DocumentStoreType.FIRESTORE:
                pass
            elif self.store_type == DocumentStoreType.LOCAL_JSON:
                if collection not in self.db:
                    self.db[collection] = self._load_collection(collection)
                if document_id not in self.db[collection]:
                    logger.warning(f"Document {document_id} not found in {collection}")
                    return False
                self.db[collection][document_id].update(data)
                self._save_collection(collection, self.db[collection])
                return True
            logger.info(f"Updated document in {collection} with ID {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False

    def delete_document(self, collection: str, document_id: str) -> bool:
        try:
            if self.store_type == DocumentStoreType.MONGODB:
                pass
            elif self.store_type == DocumentStoreType.FIRESTORE:
                pass
            elif self.store_type == DocumentStoreType.LOCAL_JSON:
                if collection not in self.db:
                    self.db[collection] = self._load_collection(collection)
                if document_id in self.db[collection]:
                    del self.db[collection][document_id]
                    self._save_collection(collection, self.db[collection])
                    return True
                return False
            logger.info(f"Deleted document from {collection} with ID {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    def query_documents(self, collection: str, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        try:
            results = []
            if self.store_type == DocumentStoreType.MONGODB:
                pass
            elif self.store_type == DocumentStoreType.FIRESTORE:
                pass
            elif self.store_type == DocumentStoreType.LOCAL_JSON:
                if collection not in self.db:
                    self.db[collection] = self._load_collection(collection)
                data = self.db[collection].values()
                for doc in data:
                    match = True
                    for k, v in query.items():
                        if k not in doc or doc[k] != v:
                            match = False
                            break
                    if match:
                        results.append(doc)
                    if len(results) >= limit:
                        break
            logger.info(f"Found {len(results)} documents in {collection}")
            return results
        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            return []
