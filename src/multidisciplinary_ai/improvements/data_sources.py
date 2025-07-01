"""
Data Source Enhancements
=======================

Enhanced data source integration with support for multiple data sources,
caching, rate limiting, and advanced features.
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """Types of data sources supported by the system."""
    API = "api"
    DATABASE = "database"
    FILE = "file"
    WEB = "web"
    STREAM = "stream"

@dataclass
class DataSourceConfig:
    """Configuration for a data source."""
    name: str
    source_type: DataSourceType
    endpoint: str
    auth_required: bool = False
    auth_params: Dict[str, str] = field(default_factory=dict)
    rate_limit: float = 1.0  # requests per second
    cache_ttl: int = 3600  # cache time-to-live in seconds
    timeout: int = 30  # request timeout in seconds
    retries: int = 3  # number of retry attempts
    retry_delay: float = 1.0  # delay between retries in seconds
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 1
    last_updated: datetime = field(default_factory=datetime.utcnow)

class DataSourceEnhancer:
    """
    Enhances data source integration with advanced features:
    - Rate limiting
    - Request caching
    - Retry logic
    - Authentication
    - Request batching
    - Error handling
    """
    
    def __init__(self, cache_dir: str = ".cache/data_sources"):
        """Initialize the data source enhancer."""
        self.sources: Dict[str, DataSourceConfig] = {}
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.request_timestamps: Dict[str, List[float]] = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'KnowledgeSystem/1.0',
            'Accept': 'application/json'
        })
    
    def add_source(self, name: str, config: DataSourceConfig) -> None:
        """
        Add a new data source configuration.
        
        Args:
            name: Unique identifier for the data source
            config: DataSourceConfig object with configuration
        """
        self.sources[name] = config
        self.request_timestamps[name] = []
        logger.info(f"Added data source: {name} ({config.source_type.value})")
    
    def get_source(self, name: str) -> Optional[DataSourceConfig]:
        """
        Get a data source configuration by name.
        
        Args:
            name: Name of the data source
            
        Returns:
            DataSourceConfig if found, None otherwise
        """
        return self.sources.get(name)
    
    def _get_cache_path(self, source_name: str, query_hash: str) -> Path:
        """
        Generate a cache file path for a query.
        
        Args:
            source_name: Name of the data source
            query_hash: MD5 hash of the query parameters
            
        Returns:
            Path object for the cache file
        """
        return self.cache_dir / f"{source_name}_{query_hash}.json"
    
    def _load_from_cache(self, cache_path: Path, ttl: int) -> Optional[Any]:
        """
        Load data from cache if it exists and is not expired.
        
        Args:
            cache_path: Path to the cache file
            ttl: Time-to-live in seconds
            
        Returns:
            Cached data if valid, None otherwise
        """
        try:
            if not cache_path.exists():
                return None
                
            file_age = time.time() - cache_path.stat().st_mtime
            if ttl > 0 and file_age > ttl:
                return None
                
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Error loading from cache {cache_path}: {e}")
            return None
    
    def _save_to_cache(self, cache_path: Path, data: Any) -> None:
        """
        Save data to cache.
        
        Args:
            cache_path: Path to the cache file
            data: Data to cache (must be JSON-serializable)
        """
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (TypeError, OSError) as e:
            logger.warning(f"Error saving to cache {cache_path}: {e}")
    
    def _respect_rate_limit(self, source_name: str) -> None:
        """
        Ensure we respect the rate limit for a data source.
        
        Args:
            source_name: Name of the data source
        """
        if source_name not in self.request_timestamps:
            return
            
        timestamps = self.request_timestamps[source_name]
        now = time.time()
        
        # Remove timestamps older than 1 second
        timestamps = [t for t in timestamps if now - t < 1.0]
        
        config = self.sources.get(source_name)
        if not config:
            return
            
        # Calculate time to wait if we've exceeded the rate limit
        if len(timestamps) >= config.rate_limit:
            time_to_wait = 1.0 - (now - timestamps[0])
            if time_to_wait > 0:
                logger.debug(f"Rate limit reached for {source_name}, waiting {time_to_wait:.2f}s")
                time.sleep(time_to_wait)
        
        # Update timestamps
        self.request_timestamps[source_name] = timestamps
        self.request_timestamps[source_name].append(time.time())
    
    def _make_request(
        self,
        method: str,
        url: str,
        source_config: DataSourceConfig,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            source_config: Data source configuration
            **kwargs: Additional request parameters
            
        Returns:
            requests.Response object
            
        Raises:
            requests.exceptions.RequestException: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(source_config.retries + 1):
            try:
                # Respect rate limiting
                self._respect_rate_limit(source_config.name)
                
                # Make the request
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=source_config.headers,
                    params=kwargs.get('params'),
                    json=kwargs.get('json'),
                    data=kwargs.get('data'),
                    timeout=source_config.timeout,
                    **{k: v for k, v in kwargs.items() 
                       if k not in ['params', 'json', 'data']}
                )
                
                # Check for HTTP errors
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < source_config.retries:
                    wait_time = source_config.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{source_config.retries}): {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    time.sleep(wait_time)
        
        # If we get here, all retries failed
        raise last_exception or Exception("Unknown error in _make_request")
    
    def fetch_data(
        self,
        source_name: str,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch data from a configured data source.
        
        Args:
            source_name: Name of the configured data source
            endpoint: API endpoint (appended to base URL)
            params: Query parameters
            use_cache: Whether to use cached data if available
            **kwargs: Additional request parameters
            
        Returns:
            Dictionary containing the response data and metadata
            
        Raises:
            ValueError: If the data source is not found or disabled
            requests.exceptions.RequestException: If the request fails after all retries
        """
        config = self.get_source(source_name)
        if not config or not config.enabled:
            raise ValueError(f"Data source not found or disabled: {source_name}")
        
        # Prepare request
        url = urljoin(config.endpoint.rstrip('/') + '/', endpoint.lstrip('/'))
        params = {**config.params, **(params or {})}
        
        # Generate cache key
        import hashlib
        cache_key = hashlib.md5(
            f"{url}?{json.dumps(params, sort_keys=True)}".encode('utf-8')
        ).hexdigest()
        cache_path = self._get_cache_path(source_name, cache_key)
        
        # Try to load from cache
        if use_cache and config.cache_ttl > 0:
            cached_data = self._load_from_cache(cache_path, config.cache_ttl)
            if cached_data is not None:
                logger.info(f"Using cached data for {source_name}:{endpoint}")
                return {
                    'data': cached_data,
                    'cached': True,
                    'source': source_name,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        try:
            # Make the request
            response = self._make_request(
                method='GET',
                url=url,
                source_config=config,
                params=params,
                **kwargs
            )
            
            # Parse response
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                data = response.json()
            else:
                data = response.text
            
            # Save to cache
            if use_cache and config.cache_ttl > 0:
                self._save_to_cache(cache_path, data)
            
            return {
                'data': data,
                'cached': False,
                'source': source_name,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching from {source_name}: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Initialize the data source enhancer
    enhancer = DataSourceEnhancer()
    
    # Add a sample API data source
    wikipedia_config = DataSourceConfig(
        name="wikipedia",
        source_type=DataSourceType.API,
        endpoint="https://en.wikipedia.org/api/rest_v1",
        rate_limit=2.0,  # 2 requests per second
        cache_ttl=86400,  # 1 day cache
        headers={
            'Accept': 'application/json',
            'User-Agent': 'KnowledgeSystem/1.0 (your-email@example.com)'
        }
    )
    enhancer.add_source("wikipedia", wikipedia_config)
    
    # Fetch data from Wikipedia
    try:
        result = enhancer.fetch_data(
            source_name="wikipedia",
            endpoint="page/summary/Artificial_intelligence",
            use_cache=True
        )
        print(f"Title: {result['data'].get('title')}")
        print(f"Extract: {result['data'].get('extract')[:200]}...")
        print(f"Cached: {result.get('cached', False)}")
        
    except Exception as e:
        print(f"Error: {e}")
