<?php
/**
 * Knowledge Base Interface
 * 
 * Provides a web interface for accessing and managing the knowledge base.
 * This class handles rendering, templating, and user interactions.
 */
class KnowledgeBaseInterface {
    private $api;
    private $templateDir;
    private $config;
    
    /**
     * Constructor
     * 
     * @param KnowledgeBaseAPI $api API client instance
     * @param string $templateDir Directory containing templates
     * @param array $config Configuration options
     */
    public function __construct($api, $templateDir = 'templates', $config = []) {
        $this->api = $api;
        $this->templateDir = rtrim($templateDir, '/');
        $this->config = array_merge([
            'title' => 'Knowledge Base',
            'items_per_page' => 10,
            'cache_enabled' => true,
            'cache_duration' => 3600, // 1 hour
            'theme' => 'default'
        ], $config);
    }
    
    /**
     * Display the home page
     * 
     * @return string Rendered HTML
     */
    public function renderHome() {
        // Get featured categories and articles
        $categories = $this->api->getCategories();
        $featured = $this->api->search('', ['featured' => true, 'limit' => 5]);
        
        $data = [
            'title' => $this->config['title'],
            'categories' => $categories ?: [],
            'featured' => $featured ?: [],
            'theme' => $this->config['theme']
        ];
        
        return $this->render('home', $data);
    }
    
    /**
     * Display a search results page
     * 
     * @param string $query Search query
     * @param int $page Page number
     * @return string Rendered HTML
     */
    public function renderSearchResults($query, $page = 1) {
        $limit = $this->config['items_per_page'];
        $offset = ($page - 1) * $limit;
        
        $results = $this->api->search($query, [
            'limit' => $limit,
            'offset' => $offset
        ]);
        
        $totalResults = isset($results['total']) ? $results['total'] : 0;
        $totalPages = ceil($totalResults / $limit);
        
        $data = [
            'title' => "Search: {$query} - {$this->config['title']}",
            'query' => $query,
            'results' => isset($results['items']) ? $results['items'] : [],
            'total' => $totalResults,
            'page' => $page,
            'totalPages' => $totalPages,
            'theme' => $this->config['theme']
        ];
        
        return $this->render('search_results', $data);
    }
    
    /**
     * Display a category page
     * 
     * @param string $categoryId Category ID
     * @param int $page Page number
     * @return string Rendered HTML
     */
    public function renderCategory($categoryId, $page = 1) {
        $limit = $this->config['items_per_page'];
        $offset = ($page - 1) * $limit;
        
        // Get category details and articles
        $category = $this->api->getCategory($categoryId);
        $articles = $this->api->getCategoryArticles($categoryId, [
            'limit' => $limit,
            'offset' => $offset
        ]);
        
        $totalArticles = isset($articles['total']) ? $articles['total'] : 0;
        $totalPages = ceil($totalArticles / $limit);
        
        $data = [
            'title' => "{$category['title']} - {$this->config['title']}",
            'category' => $category ?: [],
            'articles' => isset($articles['items']) ? $articles['items'] : [],
            'total' => $totalArticles,
            'page' => $page,
            'totalPages' => $totalPages,
            'theme' => $this->config['theme']
        ];
        
        return $this->render('category', $data);
    }
    
    /**
     * Display an article page
     * 
     * @param string $articleId Article ID
     * @return string Rendered HTML
     */
    public function renderArticle($articleId) {
        // Get article and related content
        $article = $this->api->getArticle($articleId);
        $related = $this->api->getRelatedArticles($articleId);
        
        if (!$article) {
            return $this->renderError(404, 'Article not found');
        }
        
        $data = [
            'title' => "{$article['title']} - {$this->config['title']}",
            'article' => $article,
            'related' => $related ?: [],
            'theme' => $this->config['theme']
        ];
        
        return $this->render('article', $data);
    }
    
    /**
     * Display the article editor
     * 
     * @param string $articleId Article ID (null for new article)
     * @return string Rendered HTML
     */
    public function renderEditor($articleId = null) {
        $article = null;
        $categories = $this->api->getCategories();
        
        if ($articleId) {
            $article = $this->api->getArticle($articleId);
            if (!$article) {
                return $this->renderError(404, 'Article not found');
            }
        }
        
        $data = [
            'title' => $articleId ? "Edit Article - {$this->config['title']}" : "New Article - {$this->config['title']}",
            'article' => $article ?: [],
            'categories' => $categories ?: [],
            'theme' => $this->config['theme']
        ];
        
        return $this->render('editor', $data);
    }
    
    /**
     * Process article form submission
     * 
     * @param array $formData Form data
     * @return array Response status and message
     */
    public function processArticleForm($formData) {
        $required = ['title', 'content', 'category_id'];
        foreach ($required as $field) {
            if (!isset($formData[$field]) || trim($formData[$field]) === '') {
                return [
                    'success' => false,
                    'message' => "Field '{$field}' is required."
                ];
            }
        }
        
        $articleData = [
            'title' => $formData['title'],
            'content' => $formData['content'],
            'category_id' => $formData['category_id'],
            'tags' => isset($formData['tags']) ? explode(',', $formData['tags']) : [],
            'featured' => isset($formData['featured']) ? (bool)$formData['featured'] : false
        ];
        
        if (isset($formData['article_id']) && !empty($formData['article_id'])) {
            // Update existing article
            $result = $this->api->updateArticle($formData['article_id'], $articleData);
            $message = 'Article updated successfully';
        } else {
            // Create new article
            $result = $this->api->createArticle($articleData);
            $message = 'Article created successfully';
        }
        
        if (!$result) {
            return [
                'success' => false,
                'message' => $this->api->getLastError() ?: 'Unknown error'
            ];
        }
        
        return [
            'success' => true,
            'message' => $message,
            'article_id' => isset($result['id']) ? $result['id'] : null
        ];
    }
    
    /**
     * Display error page
     * 
     * @param int $code HTTP error code
     * @param string $message Error message
     * @return string Rendered HTML
     */
    public function renderError($code, $message = '') {
        $errorMessages = [
            400 => 'Bad Request',
            401 => 'Unauthorized',
            403 => 'Forbidden',
            404 => 'Not Found',
            500 => 'Internal Server Error'
        ];
        
        if (!$message && isset($errorMessages[$code])) {
            $message = $errorMessages[$code];
        }
        
        $data = [
            'title' => "Error {$code} - {$this->config['title']}",
            'code' => $code,
            'message' => $message,
            'theme' => $this->config['theme']
        ];
        
        return $this->render('error', $data);
    }
    
    /**
     * Render a template with data
     * 
     * @param string $template Template name
     * @param array $data Template variables
     * @return string Rendered HTML
     */
    private function render($template, $data = []) {
        $templateFile = "{$this->templateDir}/{$template}.php";
        
        if (!file_exists($templateFile)) {
            return "Template not found: {$template}";
        }
        
        // Extract variables for use in template
        extract($data);
        
        // Capture output
        ob_start();
        include $templateFile;
        $output = ob_get_clean();
        
        return $output;
    }
    
    /**
     * Get cache key for a request
     * 
     * @param string $template Template name
     * @param array $params Request parameters
     * @return string Cache key
     */
    private function getCacheKey($template, $params = []) {
        return md5($template . json_encode($params));
    }
    
    /**
     * Save data to cache
     * 
     * @param string $key Cache key
     * @param mixed $data Data to cache
     * @param int $duration Cache duration in seconds
     * @return bool Success status
     */
    private function saveCache($key, $data, $duration = null) {
        if (!$this->config['cache_enabled']) {
            return false;
        }
        
        if ($duration === null) {
            $duration = $this->config['cache_duration'];
        }
        
        $cacheDir = $this->config['cache_dir'] ?? sys_get_temp_dir() . '/kb_cache';
        
        if (!is_dir($cacheDir) && !mkdir($cacheDir, 0755, true)) {
            return false;
        }
        
        $file = "{$cacheDir}/{$key}.cache";
        $cacheData = [
            'expires' => time() + $duration,
            'data' => $data
        ];
        
        return file_put_contents($file, serialize($cacheData)) !== false;
    }
    
    /**
     * Get data from cache
     * 
     * @param string $key Cache key
     * @return mixed Cached data or false if not found/expired
     */
    private function getCache($key) {
        if (!$this->config['cache_enabled']) {
            return false;
        }
        
        $cacheDir = $this->config['cache_dir'] ?? sys_get_temp_dir() . '/kb_cache';
        $file = "{$cacheDir}/{$key}.cache";
        
        if (!file_exists($file)) {
            return false;
        }
        
        $cacheData = unserialize(file_get_contents($file));
        
        if (!$cacheData || !isset($cacheData['expires']) || !isset($cacheData['data'])) {
            return false;
        }
        
        if (time() > $cacheData['expires']) {
            // Cache expired, remove file
            @unlink($file);
            return false;
        }
        
        return $cacheData['data'];
    }
}
