/**
 * Database Service for Knowledge Base Assistant
 * Provides frontend access to database services (document store, vector DB, relational DB)
 * Handles API calls, caching, and error handling
 */

import axios from 'axios';
import { getBaseUrl } from '../utils/config';

// Base URL for API calls
const baseUrl = getBaseUrl();

// Create axios instance with common configuration
const api = axios.create({
  baseURL: `${baseUrl}/api`,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Error handler for API calls
 * @param {Error} error - Axios error object
 * @returns {Object} - Standardized error object
 */
const handleError = (error) => {
  console.error('Database service error:', error);
  
  // Extract message from different error types
  const message = error.response?.data?.detail || 
                 error.response?.data?.message ||
                 error.message ||
                 'Unknown database error';
                 
  return { 
    error: true, 
    message,
    status: error.response?.status || 500
  };
};

/**
 * Document Store Service
 * Handles unstructured data (conversations, multimodal assets, etc.)
 */
const documentStore = {
  /**
   * Create a document in the document store
   * @param {string} collection - Collection name
   * @param {Object} document - Document to create
   * @returns {Promise<Object>} - Created document info
   */
  async createDocument(collection, document) {
    try {
      const response = await api.post(`/db/documents/${collection}`, document);
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  },
  
  /**
   * Get a document from the document store
   * @param {string} collection - Collection name
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} - Document data
   */
  async getDocument(collection, documentId) {
    try {
      const response = await api.get(`/db/documents/${collection}/${documentId}`);
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  },
  
  /**
   * Update a document in the document store
   * @param {string} collection - Collection name
   * @param {string} documentId - Document ID
   * @param {Object} document - Updated document data
   * @returns {Promise<Object>} - Update result
   */
  async updateDocument(collection, documentId, document) {
    try {
      const response = await api.put(`/db/documents/${collection}/${documentId}`, document);
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  },
  
  /**
   * Delete a document from the document store
   * @param {string} collection - Collection name
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} - Deletion result
   */
  async deleteDocument(collection, documentId) {
    try {
      const response = await api.delete(`/db/documents/${collection}/${documentId}`);
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  },
  
  /**
   * Query documents in the document store
   * @param {string} collection - Collection name
   * @param {Object} query - Query parameters
   * @param {number} limit - Maximum number of results
   * @returns {Promise<Array>} - Matching documents
   */
  async queryDocuments(collection, query, limit = 100) {
    try {
      const response = await api.post(`/db/documents/${collection}/query`, query, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  }
};

/**
 * Vector Database Service
 * Handles semantic search and vector embeddings
 */
const vectorDb = {
  /**
   * Add documents with embeddings to the vector database
   * @param {Array<Object>} documents - Documents to add
   * @param {string} collection - Collection name
   * @returns {Promise<Object>} - Result with count of added documents
   */
  async addDocuments(documents, collection = 'knowledge_base') {
    try {
      const response = await api.post('/db/vectors/add', documents, {
        params: { collection }
      });
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  },
  
  /**
   * Search for similar documents in the vector database
   * @param {string} query - Search query text
   * @param {string} collection - Collection name
   * @param {number} limit - Maximum number of results
   * @param {Object} filter - Optional filter criteria
   * @returns {Promise<Array>} - Search results
   */
  async search(query, collection = 'default', limit = 5, filter = null) {
    try {
      const response = await api.post('/db/vectors/search', {
        query,
        collection,
        limit,
        filter
      });
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  },
  
  /**
   * Delete a document from the vector database
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} - Deletion result
   */
  async deleteDocument(documentId) {
    try {
      const response = await api.delete(`/db/vectors/${documentId}`);
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  }
};

/**
 * Relational Database Service
 * Handles structured data (users, settings, etc.)
 */
const relationalDb = {
  /**
   * Create a new user
   * @param {Object} user - User data
   * @returns {Promise<Object>} - Created user info
   */
  async createUser(user) {
    try {
      const response = await api.post('/db/users', user);
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  },
  
  /**
   * Get user details
   * @param {string} userId - User ID
   * @returns {Promise<Object>} - User data
   */
  async getUser(userId) {
    try {
      const response = await api.get(`/db/users/${userId}`);
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  },
  
  /**
   * Update user details
   * @param {string} userId - User ID
   * @param {Object} userData - Updated user data
   * @returns {Promise<Object>} - Update result
   */
  async updateUser(userId, userData) {
    try {
      const response = await api.put(`/db/users/${userId}`, userData);
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  },
  
  /**
   * Save a user setting
   * @param {string} userId - User ID
   * @param {string} key - Setting key
   * @param {string} value - Setting value
   * @returns {Promise<Object>} - Result
   */
  async saveSetting(userId, key, value) {
    try {
      const response = await api.post(`/db/users/${userId}/settings`, {
        key,
        value
      });
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  },
  
  /**
   * Get all user settings
   * @param {string} userId - User ID
   * @returns {Promise<Object>} - Settings key-value pairs
   */
  async getSettings(userId) {
    try {
      const response = await api.get(`/db/users/${userId}/settings`);
      return response.data;
    } catch (error) {
      return handleError(error);
    }
  }
};

/**
 * Combined database service
 */
const databaseService = {
  documents: documentStore,
  vectors: vectorDb,
  users: relationalDb
};

export default databaseService;
