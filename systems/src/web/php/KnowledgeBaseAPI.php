<?php
/**
 * Knowledge Base API Client
 * 
 * This class provides access to the knowledge base API from PHP applications.
 * It handles authentication, request formatting, and response parsing.
 */
class KnowledgeBaseAPI {
    private $apiUrl;
    private $apiKey;
    private $lastError;
    private $timeout = 30;
    
    /**
     * Constructor
     * 
     * @param string $apiUrl The base URL for the knowledge base API
     * @param string $apiKey API key for authentication
     */
    public function __construct($apiUrl, $apiKey = null) {
        $this->apiUrl = rtrim($apiUrl, '/');
        $this->apiKey = $apiKey;
    }
    
    /**
     * Set API key for authentication
     * 
     * @param string $apiKey The API key
     * @return void
     */
    public function setApiKey($apiKey) {
        $this->apiKey = $apiKey;
    }
    
    /**
     * Set request timeout
     * 
     * @param int $seconds Timeout in seconds
     * @return void
     */
    public function setTimeout($seconds) {
        $this->timeout = max(1, intval($seconds));
    }
    
    /**
     * Get the last error message
     * 
     * @return string|null Last error message or null if no error
     */
    public function getLastError() {
        return $this->lastError;
    }
    
    /**
     * Search the knowledge base
     * 
     * @param string $query Search query
     * @param array $options Optional search parameters
     * @return array|false Search results or false on error
     */
    public function search($query, $options = []) {
        $params = array_merge([
            'q' => $query,
            'limit' => 10,
            'offset' => 0
        ], $options);
        
        return $this->request('GET', '/search', $params);
    }
    
    /**
     * Get article by ID
     * 
     * @param string $articleId Article ID
     * @return array|false Article data or false on error
     */
    public function getArticle($articleId) {
        return $this->request('GET', "/articles/{$articleId}");
    }
    
    /**
     * Get all categories
     * 
     * @return array|false List of categories or false on error
     */
    public function getCategories() {
        return $this->request('GET', '/categories');
    }
    
    /**
     * Get articles in a category
     * 
     * @param string $categoryId Category ID
     * @param array $options Optional parameters
     * @return array|false List of articles or false on error
     */
    public function getCategoryArticles($categoryId, $options = []) {
        $params = array_merge([
            'limit' => 20,
            'offset' => 0
        ], $options);
        
        return $this->request('GET', "/categories/{$categoryId}/articles", $params);
    }
    
    /**
     * Create new article
     * 
     * @param array $articleData Article data
     * @return array|false Created article or false on error
     */
    public function createArticle($articleData) {
        return $this->request('POST', '/articles', [], $articleData);
    }
    
    /**
     * Update an article
     * 
     * @param string $articleId Article ID
     * @param array $articleData Article data
     * @return array|false Updated article or false on error
     */
    public function updateArticle($articleId, $articleData) {
        return $this->request('PUT', "/articles/{$articleId}", [], $articleData);
    }
    
    /**
     * Delete an article
     * 
     * @param string $articleId Article ID
     * @return bool True on success, false on error
     */
    public function deleteArticle($articleId) {
        $result = $this->request('DELETE', "/articles/{$articleId}");
        return $result !== false;
    }
    
    /**
     * Get related articles
     * 
     * @param string $articleId Article ID
     * @param int $limit Maximum number of related articles to return
     * @return array|false Related articles or false on error
     */
    public function getRelatedArticles($articleId, $limit = 5) {
        return $this->request('GET', "/articles/{$articleId}/related", ['limit' => $limit]);
    }
    
    /**
     * Submit feedback for an article
     * 
     * @param string $articleId Article ID
     * @param array $feedback Feedback data
     * @return bool True on success, false on error
     */
    public function submitFeedback($articleId, $feedback) {
        $result = $this->request('POST', "/articles/{$articleId}/feedback", [], $feedback);
        return $result !== false;
    }
    
    /**
     * Export data from the knowledge base
     * 
     * @param string $format Export format (json, csv, xml)
     * @param array $options Export options
     * @return string|false Exported data or false on error
     */
    public function exportData($format = 'json', $options = []) {
        $params = array_merge([
            'format' => $format
        ], $options);
        
        $result = $this->request('GET', '/export', $params);
        return $result;
    }
    
    /**
     * Send a request to the API
     * 
     * @param string $method HTTP method
     * @param string $endpoint API endpoint
     * @param array $params Query parameters
     * @param array $data Request body data
     * @return array|false Response data or false on error
     */
    private function request($method, $endpoint, $params = [], $data = null) {
        $url = $this->apiUrl . $endpoint;
        
        // Add query parameters
        if (!empty($params)) {
            $url .= '?' . http_build_query($params);
        }
        
        // Initialize cURL
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);
        
        // Set request method
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
        
        // Set headers
        $headers = ['Accept: application/json'];
        
        // Add API key if available
        if ($this->apiKey) {
            $headers[] = "Authorization: Bearer {$this->apiKey}";
        }
        
        // Add request data if provided
        if ($data !== null) {
            $jsonData = json_encode($data);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
            $headers[] = 'Content-Type: application/json';
            $headers[] = 'Content-Length: ' . strlen($jsonData);
        }
        
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        
        // Execute request
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        
        // Check for errors
        if (curl_errno($ch)) {
            $this->lastError = curl_error($ch);
            curl_close($ch);
            return false;
        }
        
        curl_close($ch);
        
        // Parse response
        $responseData = json_decode($response, true);
        
        // Handle error responses
        if ($httpCode >= 400) {
            $this->lastError = isset($responseData['error']) ? 
                $responseData['error'] : "HTTP Error {$httpCode}";
            return false;
        }
        
        return $responseData;
    }
}
