# PHP Web Interface

This documentation covers the PHP components for integrating with the Knowledge Base system, including API clients, web interfaces, and implementation guides.

## Overview

The PHP Web Interface module provides libraries and components for building web applications that interact with the Knowledge Base. It includes an API client, user interface components, and integration examples.

### Key Features

- Knowledge Base API client for PHP applications
- Web interface components for displaying and managing knowledge content
- Authentication and authorization integration
- Caching and performance optimization
- Templating and theming support
- Search integration
- Multi-language support

## Components

### KnowledgeBaseAPI

The `KnowledgeBaseAPI` class is a PHP client for accessing the Knowledge Base API. It provides methods for searching, retrieving, and managing knowledge content.

```php
// Initialize the API client
$api = new KnowledgeBaseAPI('https://api.knowledge-base.example', 'YOUR_API_KEY');

// Search the knowledge base
$results = $api->search('robotics navigation');

// Get a specific article
$article = $api->getArticle('article-123');
```

### KnowledgeBaseInterface

The `KnowledgeBaseInterface` class provides a web interface for displaying and interacting with knowledge content. It includes templates for common views such as search results, article display, and category browsing.

```php
// Initialize the interface
$interface = new KnowledgeBaseInterface($api, 'templates', [
    'title' => 'Company Knowledge Base',
    'theme' => 'corporate'
]);

// Display the home page
echo $interface->renderHome();

// Display search results
echo $interface->renderSearchResults('robotics', 1);
```

## Installation

### Requirements

- PHP 7.4 or higher
- cURL extension
- JSON extension
- Optionally: Memcached or Redis for caching

### Via Composer

```bash
composer require knowledge-base/php-client
```

### Manual Installation

1. Download the latest release from the repository
2. Include the files in your PHP project
3. Use autoloading or require the necessary files

```php
require_once 'path/to/KnowledgeBaseAPI.php';
require_once 'path/to/KnowledgeBaseInterface.php';
```

## Configuration

### API Client Configuration

```php
$api = new KnowledgeBaseAPI(
    'https://api.knowledge-base.example',  // API URL
    'YOUR_API_KEY',                        // API key
);

// Set request timeout (seconds)
$api->setTimeout(30);
```

### Interface Configuration

```php
$interface = new KnowledgeBaseInterface(
    $api,                 // API client instance
    'templates',          // Template directory
    [
        'title' => 'Knowledge Base',
        'items_per_page' => 10,
        'cache_enabled' => true,
        'cache_duration' => 3600, // 1 hour
        'theme' => 'default'
    ]
);
```

## Usage Examples

### Basic Search Interface

```php
<?php
require_once 'vendor/autoload.php';

// Initialize the API and interface
$api = new KnowledgeBaseAPI('https://api.knowledge-base.example', 'YOUR_API_KEY');
$interface = new KnowledgeBaseInterface($api);

// Get search query from request
$query = isset($_GET['q']) ? $_GET['q'] : '';
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;

// Display search form and results
if (!empty($query)) {
    echo $interface->renderSearchResults($query, $page);
} else {
    echo $interface->renderHome();
}
?>
```

### Article Display

```php
<?php
require_once 'vendor/autoload.php';

// Initialize the API and interface
$api = new KnowledgeBaseAPI('https://api.knowledge-base.example', 'YOUR_API_KEY');
$interface = new KnowledgeBaseInterface($api);

// Get article ID from request
$articleId = isset($_GET['id']) ? $_GET['id'] : null;

if ($articleId) {
    echo $interface->renderArticle($articleId);
} else {
    echo $interface->renderError(400, 'Article ID is required');
}
?>
```

### Article Editor

```php
<?php
require_once 'vendor/autoload.php';

// Initialize the API and interface
$api = new KnowledgeBaseAPI('https://api.knowledge-base.example', 'YOUR_API_KEY');
$interface = new KnowledgeBaseInterface($api);

// Get article ID from request
$articleId = isset($_GET['id']) ? $_GET['id'] : null;

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $result = $interface->processArticleForm($_POST);
    
    if ($result['success']) {
        header('Location: article.php?id=' . $result['article_id']);
        exit;
    } else {
        $error = $result['message'];
    }
}

// Display editor form
echo $interface->renderEditor($articleId);
?>
```

## Customization

### Custom Templates

The interface uses PHP templates for rendering. You can create custom templates by copying the default templates and modifying them according to your needs.

```php
// Use custom templates
$interface = new KnowledgeBaseInterface(
    $api,
    'path/to/custom/templates',
    ['theme' => 'custom']
);
```

### Custom Styling

Add custom CSS to style the knowledge base interface:

```html
<link rel="stylesheet" href="path/to/custom/style.css">
```

### Template Structure

A basic template structure includes:

- `home.php` - Home page template
- `search_results.php` - Search results template
- `article.php` - Article display template
- `category.php` - Category browse template
- `editor.php` - Article editor template
- `error.php` - Error page template

## Advanced Features

### Caching

The interface supports caching to improve performance:

```php
$interface = new KnowledgeBaseInterface(
    $api,
    'templates',
    [
        'cache_enabled' => true,
        'cache_duration' => 1800,  // 30 minutes
        'cache_dir' => '/path/to/cache'
    ]
);
```

### Authentication Integration

Integrate with authentication systems:

```php
// Check if user is authenticated
if (isUserAuthenticated()) {
    // Get user information
    $user = getCurrentUser();
    
    // Set API key for the user
    $api->setApiKey($user['api_key']);
    
    // Display editor for authenticated users
    if ($user['can_edit']) {
        echo $interface->renderEditor($articleId);
    } else {
        echo $interface->renderArticle($articleId);
    }
} else {
    // Redirect to login
    header('Location: login.php');
    exit;
}
```

### Webhooks

Set up webhooks to receive notifications when knowledge content is updated:

```php
// Webhook endpoint
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $_SERVER['REQUEST_URI'] === '/webhook') {
    $payload = json_decode(file_get_contents('php://input'), true);
    
    if ($payload && isset($payload['event'])) {
        switch ($payload['event']) {
            case 'article.created':
            case 'article.updated':
                // Clear cache for the affected article
                clearCache('article_' . $payload['article_id']);
                break;
            case 'category.updated':
                // Clear category cache
                clearCache('category_' . $payload['category_id']);
                break;
        }
    }
    
    http_response_code(200);
    echo json_encode(['status' => 'success']);
    exit;
}
```

## Performance Optimization

### Request Optimization

```php
// Reduce API calls by combining requests
$categories = $api->getCategories();
$featured = $api->search('', ['featured' => true, 'limit' => 5]);

// Use these results in multiple sections of your page
```

### Caching Strategies

- **Page caching**: Cache entire rendered pages
- **Fragment caching**: Cache specific parts of pages
- **API response caching**: Cache API responses
- **Query parameter normalization**: Normalize search queries to improve cache hits

## Troubleshooting

### Common Issues

- **API Connection Errors**: Check API URL, network connectivity, and firewall settings
- **Authentication Failures**: Verify API key and permissions
- **Performance Issues**: Enable caching and optimize API requests
- **Rendering Problems**: Check template files and PHP version compatibility

### Debugging

Enable debugging mode to get detailed error information:

```php
// Enable debugging
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Get last API error
if (!$results) {
    echo "API Error: " . $api->getLastError();
}
```

## Integration Examples

### Integration with Laravel

```php
// ServiceProvider
namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use KnowledgeBaseAPI;

class KnowledgeBaseServiceProvider extends ServiceProvider
{
    public function register()
    {
        $this->app->singleton(KnowledgeBaseAPI::class, function ($app) {
            return new KnowledgeBaseAPI(
                config('services.knowledge_base.url'),
                config('services.knowledge_base.key')
            );
        });
    }
}

// Controller
namespace App\Http\Controllers;

use KnowledgeBaseAPI;

class KnowledgeBaseController extends Controller
{
    protected $api;
    
    public function __construct(KnowledgeBaseAPI $api)
    {
        $this->api = $api;
    }
    
    public function search(Request $request)
    {
        $query = $request->input('q');
        $results = $this->api->search($query);
        
        return view('knowledge.search', [
            'query' => $query,
            'results' => $results
        ]);
    }
}
```

### Integration with WordPress

```php
// functions.php
function register_knowledge_base_api() {
    require_once plugin_dir_path(__FILE__) . 'vendor/autoload.php';
    
    global $kb_api;
    $kb_api = new KnowledgeBaseAPI(
        get_option('kb_api_url'),
        get_option('kb_api_key')
    );
}
add_action('init', 'register_knowledge_base_api');

// Shortcode for displaying search results
function kb_search_shortcode($atts) {
    global $kb_api;
    
    $query = isset($_GET['kb_q']) ? $_GET['kb_q'] : '';
    $page = isset($_GET['kb_page']) ? (int)$_GET['kb_page'] : 1;
    
    $interface = new KnowledgeBaseInterface($kb_api);
    
    ob_start();
    echo '<div class="kb-search-form">';
    echo '<form method="get">';
    echo '<input type="text" name="kb_q" value="' . esc_attr($query) . '" placeholder="Search knowledge base...">';
    echo '<button type="submit">Search</button>';
    echo '</form>';
    echo '</div>';
    
    if (!empty($query)) {
        echo $interface->renderSearchResults($query, $page);
    }
    
    return ob_get_clean();
}
add_shortcode('kb_search', 'kb_search_shortcode');
```

## References

- [PHP Documentation Standards](references/php_standards.md)
- [Knowledge Base API Reference](references/api_reference.md)
- [Template Development Guide](references/template_guide.md)
- [Performance Optimization Guide](references/performance_guide.md)
- [Security Best Practices](references/security_guide.md)

## Contributing

Guidelines for contributing to the PHP module:

- [Development Setup](contributing/setup.md)
- [Coding Standards](contributing/standards.md)
- [Testing Guidelines](contributing/testing.md)
- [Documentation Guidelines](contributing/documentation.md)
- [Pull Request Process](contributing/pull_requests.md)
