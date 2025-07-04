"""
Advanced Web Scraping Module for the Knowledge Base Assistant
Features:
- Configurable scraping with multiple strategies
- Data extraction and structured parsing
- Dynamic content handling
- Rate limiting and politeness controls
- Error recovery and retry mechanisms
"""

import logging
import time
import random
import json
import re
from typing import Dict, List, Any, Optional, Union, Callable
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd
import concurrent.futures
from datetime import datetime

# Optional imports for advanced functionality
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Constants and configuration
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# Rate limiting settings (to be polite to servers)
MIN_REQUEST_INTERVAL = 2.0  # seconds between requests
JITTER = 1.0  # random jitter added to request interval
MAX_RETRIES = 3  # maximum number of retries for failed requests
RETRY_DELAY = 5  # seconds to wait between retries

class RateLimiter:
    """Simple rate limiter to ensure polite scraping"""
    
    def __init__(self, min_interval: float = MIN_REQUEST_INTERVAL, jitter: float = JITTER):
        self.min_interval = min_interval
        self.jitter = jitter
        self.last_request_time = 0
        
    def wait(self):
        """Wait until it's appropriate to make the next request"""
        now = time.time()
        elapsed = now - self.last_request_time
        
        if elapsed < self.min_interval:
            # Add random jitter to avoid detection patterns
            delay = self.min_interval - elapsed + random.uniform(0, self.jitter)
            time.sleep(delay)
            
        self.last_request_time = time.time()

class WebScraper:
    """Main web scraping class with support for different strategies"""
    
    def __init__(self, 
                 use_playwright: bool = False, 
                 headers: Dict[str, str] = None,
                 proxy: str = None,
                 rate_limit_interval: float = MIN_REQUEST_INTERVAL):
        """
        Initialize the scraper
        
        Args:
            use_playwright: Whether to use Playwright for JS rendering
            headers: Custom headers to use for requests
            proxy: Optional proxy URL
            rate_limit_interval: Minimum seconds between requests
        """
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.headers = headers or DEFAULT_HEADERS
        self.proxy = proxy
        self.rate_limiter = RateLimiter(rate_limit_interval)
        self.playwright = None
        self.browser = None
        
        if self.use_playwright and not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright requested but not installed. Falling back to requests.")
            self.use_playwright = False
            
        logger.info(f"Initialized scraper with {'Playwright' if self.use_playwright else 'Requests'}")
        
    def __enter__(self):
        """Context manager entry"""
        if self.use_playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,
                proxy={"server": self.proxy} if self.proxy else None
            )
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            
    def fetch_page(self, url: str, wait_for_selector: str = None, retries: int = MAX_RETRIES) -> Optional[str]:
        """
        Fetch a page using the configured strategy
        
        Args:
            url: URL to fetch
            wait_for_selector: CSS selector to wait for when using Playwright
            retries: Number of retry attempts for failed requests
            
        Returns:
            HTML content or None if failed
        """
        logger.info(f"Fetching URL: {url}")
        
        # Respect rate limiting
        self.rate_limiter.wait()
        
        # Try to fetch with retries
        for attempt in range(retries + 1):
            try:
                if self.use_playwright:
                    return self._fetch_with_playwright(url, wait_for_selector)
                else:
                    return self._fetch_with_requests(url)
            except Exception as e:
                if attempt < retries:
                    delay = RETRY_DELAY * (attempt + 1)
                    logger.warning(f"Fetch failed (attempt {attempt+1}/{retries+1}): {e}. Retrying in {delay}s")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to fetch {url} after {retries+1} attempts: {e}")
                    return None
                
    def _fetch_with_requests(self, url: str) -> str:
        """Fetch page using requests"""
        response = requests.get(
            url,
            headers=self.headers,
            proxies={"http": self.proxy, "https": self.proxy} if self.proxy else None,
            timeout=30
        )
        response.raise_for_status()
        return response.text
    
    def _fetch_with_playwright(self, url: str, wait_for_selector: str = None) -> str:
        """Fetch page using Playwright (with JS rendering)"""
        if not self.browser:
            raise RuntimeError("Playwright browser not initialized. Use context manager.")
            
        page = self.browser.new_page(user_agent=self.headers.get('User-Agent'))
        
        try:
            # Set headers
            page.set_extra_http_headers({k: v for k, v in self.headers.items() if k != 'User-Agent'})
            
            # Navigate to URL
            page.goto(url, wait_until='networkidle')
            
            # Wait for specific content if requested
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector)
                
            # Get the rendered HTML
            content = page.content()
            return content
        finally:
            page.close()

    def extract_data(self, html: str, extraction_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from HTML using the provided extraction configuration
        
        Args:
            html: HTML content
            extraction_config: Configuration for data extraction
            
        Returns:
            Dictionary of extracted data
        """
        if not html:
            return {}
            
        soup = BeautifulSoup(html, 'html.parser')
        result = {}
        
        # Extract data based on the configuration
        for field_name, config in extraction_config.items():
            try:
                selector = config.get('selector')
                attribute = config.get('attribute')
                is_list = config.get('is_list', False)
                post_process = config.get('post_process')
                
                if is_list:
                    elements = soup.select(selector)
                    if attribute == '_text':
                        values = [el.get_text(strip=True) for el in elements]
                    else:
                        values = [el.get(attribute) for el in elements]
                        
                    # Filter out None values
                    values = [v for v in values if v]
                    
                    # Apply post-processing if specified
                    if post_process and callable(post_process):
                        values = [post_process(v) for v in values]
                        
                    result[field_name] = values
                else:
                    element = soup.select_one(selector)
                    if element:
                        if attribute == '_text':
                            value = element.get_text(strip=True)
                        else:
                            value = element.get(attribute)
                            
                        # Apply post-processing if specified
                        if value and post_process and callable(post_process):
                            value = post_process(value)
                            
                        result[field_name] = value
                    else:
                        result[field_name] = None
            except Exception as e:
                logger.error(f"Error extracting field '{field_name}': {e}")
                result[field_name] = None
                
        return result
    
    def scrape_multiple(self, urls: List[str], extraction_config: Dict[str, Any], 
                        max_workers: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs in parallel
        
        Args:
            urls: List of URLs to scrape
            extraction_config: Configuration for data extraction
            max_workers: Maximum number of concurrent workers
            
        Returns:
            List of extracted data dictionaries
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.scrape_single, url, extraction_config): url
                for url in urls
            }
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    if data:
                        data['_url'] = url  # Add source URL
                        data['_timestamp'] = datetime.now().isoformat()
                        results.append(data)
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    
        return results
    
    def scrape_single(self, url: str, extraction_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Scrape a single URL
        
        Args:
            url: URL to scrape
            extraction_config: Configuration for data extraction
            
        Returns:
            Dictionary of extracted data or None if failed
        """
        html = self.fetch_page(url)
        if html:
            return self.extract_data(html, extraction_config)
        return None
    
    def scrape_pagination(self, base_url: str, extraction_config: Dict[str, Any],
                         page_param: str = 'page', start_page: int = 1,
                         max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape paginated results
        
        Args:
            base_url: Base URL for pagination
            extraction_config: Configuration for data extraction
            page_param: URL parameter for pagination
            start_page: Starting page number
            max_pages: Maximum pages to scrape
            
        Returns:
            List of extracted data dictionaries
        """
        all_results = []
        
        for page in range(start_page, start_page + max_pages):
            if '?' in base_url:
                url = f"{base_url}&{page_param}={page}"
            else:
                url = f"{base_url}?{page_param}={page}"
                
            logger.info(f"Scraping page {page}/{start_page + max_pages - 1}: {url}")
            
            # Scrape the page
            html = self.fetch_page(url)
            if not html:
                logger.warning(f"Failed to fetch page {page}, stopping pagination")
                break
                
            # Extract data from this page
            data = self.extract_data(html, extraction_config)
            
            # If we have an items key in the extraction config, use that
            items = data.get('items', [])
            if items:
                all_results.extend(items)
            else:
                # Otherwise treat the entire result as a single item
                data['_url'] = url
                data['_page'] = page
                data['_timestamp'] = datetime.now().isoformat()
                all_results.append(data)
                
            # Simple heuristic: if we got fewer results than expected, assume we've reached the end
            if len(items) == 0:
                logger.info(f"No items found on page {page}, stopping pagination")
                break
                
        return all_results

class DataAnalyzer:
    """Class for analyzing scraped data"""
    
    @staticmethod
    def to_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert scraped data to pandas DataFrame"""
        return pd.DataFrame(data)
    
    @staticmethod
    def basic_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic statistics on numerical columns"""
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        stats = {
            'count': df.shape[0],
            'columns': list(df.columns),
            'numeric_columns': list(numeric_cols),
            'missing_values': df.isna().sum().to_dict(),
            'numeric_stats': df[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else {}
        }
        
        return stats
    
    @staticmethod
    def text_analysis(df: pd.DataFrame, text_column: str) -> Dict[str, Any]:
        """Analyze text data in the specified column"""
        if text_column not in df.columns:
            return {'error': f'Column {text_column} not found'}
            
        # Filter out missing values
        text_data = df[text_column].dropna()
        
        result = {
            'count': len(text_data),
            'avg_length': sum(len(str(t)) for t in text_data) / max(len(text_data), 1),
            'min_length': min((len(str(t)) for t in text_data), default=0),
            'max_length': max((len(str(t)) for t in text_data), default=0)
        }
        
        # Add word frequency if we have data
        if len(text_data) > 0:
            all_text = ' '.join(str(t).lower() for t in text_data)
            words = re.findall(r'\b\w+\b', all_text)
            word_freq = {}
            
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
                    
            # Get top words
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            result['top_words'] = dict(top_words)
            
        return result
    
    @staticmethod
    def save_to_json(data: List[Dict[str, Any]], filepath: str) -> bool:
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving data to {filepath}: {e}")
            return False
            
    @staticmethod
    def save_to_csv(df: pd.DataFrame, filepath: str) -> bool:
        """Save DataFrame to CSV file"""
        try:
            df.to_csv(filepath, index=False, encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Error saving data to {filepath}: {e}")
            return False

# Example usage
def example_scrape():
    """Example of how to use the scraper"""
    # Define extraction config for a simple product page
    product_config = {
        'title': {'selector': 'h1.product-title', 'attribute': '_text'},
        'price': {'selector': 'span.price', 'attribute': '_text'},
        'description': {'selector': 'div.description', 'attribute': '_text'},
        'images': {'selector': 'div.product-gallery img', 'attribute': 'src', 'is_list': True}
    }
    
    # Example pagination config for a blog
    blog_config = {
        'posts': {
            'selector': 'article.blog-post',
            'is_list': True,
            'items': {
                'title': {'selector': 'h2', 'attribute': '_text'},
                'date': {'selector': 'time', 'attribute': '_text'},
                'excerpt': {'selector': '.excerpt', 'attribute': '_text'},
                'link': {'selector': 'a.read-more', 'attribute': 'href'}
            }
        }
    }
    
    # Use the scraper
    with WebScraper(use_playwright=True) as scraper:
        # Scrape a single product
        product_data = scraper.scrape_single('https://example.com/product/1', product_config)
        
        # Scrape multiple products
        products = scraper.scrape_multiple([
            'https://example.com/product/1',
            'https://example.com/product/2',
            'https://example.com/product/3'
        ], product_config)
        
        # Scrape paginated blog
        blog_posts = scraper.scrape_pagination('https://example.com/blog', blog_config, max_pages=3)
        
        # Analyze the data
        analyzer = DataAnalyzer()
        df = analyzer.to_dataframe(products)
        stats = analyzer.basic_stats(df)
        
        # Save results
        analyzer.save_to_json(products, 'products.json')
        analyzer.save_to_csv(df, 'products.csv')
        
        return {
            'product': product_data,
            'products_count': len(products),
            'blog_posts_count': len(blog_posts),
            'stats': stats
        }

if __name__ == "__main__":
    # Configure logging for direct execution
    logging.basicConfig(level=logging.INFO)
    
    # Run example
    print("Starting example scrape...")
    results = example_scrape()
    print(f"Results: {json.dumps(results, indent=2)}")
