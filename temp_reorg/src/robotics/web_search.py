"""
Web search module with Tor integration for anonymous searching
This module provides web search capabilities with privacy protection
"""

import requests
import logging
import json
import os
from stem import Signal
from stem.control import Controller
import socks
import socket
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode, quote_plus
from typing import List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Tor configuration
TOR_ENABLED = os.environ.get('USE_TOR', 'false').lower() == 'true'
TOR_PASSWORD = os.environ.get('TOR_PASSWORD', '')  # For auth if needed
TOR_HOST = os.environ.get('TOR_HOST', '127.0.0.1')
TOR_SOCKS_PORT = int(os.environ.get('TOR_SOCKS_PORT', 9050))
TOR_CONTROL_PORT = int(os.environ.get('TOR_CONTROL_PORT', 9051))

# Search engines and API configuration
SEARCH_ENGINE = os.environ.get('SEARCH_ENGINE', 'duckduckgo')  # Options: 'duckduckgo', 'brave', etc.
SERP_API_KEY = os.environ.get('SERP_API_KEY', '')  # For SerpAPI if used

class TorSession:
    """Session class that routes requests through Tor for anonymity"""
    
    def __init__(self):
        self.session = requests.Session()
        if TOR_ENABLED:
            self._setup_tor_session()
            logger.info("Tor session initialized")
        else:
            logger.info("Standard session initialized (Tor disabled)")
    
    def _setup_tor_session(self):
        """Configure session to use Tor SOCKS proxy"""
        socks.set_default_proxy(socks.SOCKS5, TOR_HOST, TOR_SOCKS_PORT)
        socket.socket = socks.socksocket
        
        # Set session headers to avoid fingerprinting
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_new_tor_identity(self):
        """Request a new Tor circuit/identity"""
        if not TOR_ENABLED:
            logger.warning("Cannot get new Tor identity: Tor is disabled")
            return False
            
        try:
            with Controller.from_port(address=TOR_HOST, port=TOR_CONTROL_PORT) as controller:
                if TOR_PASSWORD:
                    controller.authenticate(password=TOR_PASSWORD)
                else:
                    controller.authenticate()
                    
                controller.signal(Signal.NEWNYM)
                logger.info("New Tor identity acquired")
                return True
        except Exception as e:
            logger.error(f"Failed to get new Tor identity: {e}")
            return False
    
    def get(self, url, **kwargs):
        """Perform a GET request through Tor if enabled"""
        try:
            return self.session.get(url, **kwargs)
        except Exception as e:
            logger.error(f"Request failed: {e}")
            # Try to get a new identity if using Tor
            if TOR_ENABLED:
                self.get_new_tor_identity()
            raise

def search_web(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using the configured search engine, through Tor if enabled
    
    Args:
        query: Search query string
        num_results: Number of results to return
        
    Returns:
        List of search results with title, snippet, and URL
    """
    logger.info(f"Searching web for: {query}")
    
    if not query:
        logger.warning("Empty search query")
        return []
    
    # Create a session (Tor or regular)
    session = TorSession()
    
    # Select search method based on configuration
    if SEARCH_ENGINE == 'duckduckgo':
        return _search_duckduckgo(session, query, num_results)
    elif SEARCH_ENGINE == 'brave':
        return _search_brave(session, query, num_results)
    elif SEARCH_ENGINE == 'serpapi':
        return _search_serpapi(query, num_results)
    else:
        logger.error(f"Unknown search engine: {SEARCH_ENGINE}")
        return []

def _search_duckduckgo(session: TorSession, query: str, num_results: int) -> List[Dict[str, Any]]:
    """Search using DuckDuckGo"""
    try:
        # Construct DuckDuckGo search URL
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        
        response = session.get(search_url, timeout=10)
        if response.status_code != 200:
            logger.error(f"DuckDuckGo search failed with status code {response.status_code}")
            return []
            
        # Parse results
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Extract search results
        for result in soup.select('.result'):
            title_elem = result.select_one('.result__title')
            snippet_elem = result.select_one('.result__snippet')
            url_elem = result.select_one('.result__url')
            
            if title_elem and url_elem:
                title = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                url = url_elem.get_text(strip=True)
                
                results.append({
                    'title': title,
                    'snippet': snippet,
                    'url': url,
                    'source': 'duckduckgo'
                })
                
                if len(results) >= num_results:
                    break
                    
        return results
    except Exception as e:
        logger.error(f"Error in DuckDuckGo search: {e}")
        return []

def _search_brave(session: TorSession, query: str, num_results: int) -> List[Dict[str, Any]]:
    """Search using Brave Search"""
    try:
        # Construct Brave search URL
        search_url = f"https://search.brave.com/search?q={quote_plus(query)}"
        
        response = session.get(search_url, timeout=10)
        if response.status_code != 200:
            logger.error(f"Brave search failed with status code {response.status_code}")
            return []
            
        # Parse results
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Extract search results (adjust selectors based on Brave's HTML structure)
        for result in soup.select('.snippet'):
            title_elem = result.select_one('.snippet-title')
            description_elem = result.select_one('.snippet-description')
            url_elem = result.select_one('.snippet-url')
            
            if title_elem and url_elem:
                title = title_elem.get_text(strip=True)
                snippet = description_elem.get_text(strip=True) if description_elem else ""
                url = url_elem.get('href')
                
                results.append({
                    'title': title,
                    'snippet': snippet,
                    'url': url,
                    'source': 'brave'
                })
                
                if len(results) >= num_results:
                    break
                    
        return results
    except Exception as e:
        logger.error(f"Error in Brave search: {e}")
        return []

def _search_serpapi(query: str, num_results: int) -> List[Dict[str, Any]]:
    """Search using SerpAPI (requires API key)"""
    if not SERP_API_KEY:
        logger.error("SERP_API_KEY is required for SerpAPI searches")
        return []
        
    try:
        # Construct SerpAPI search URL
        params = {
            'q': query,
            'api_key': SERP_API_KEY,
            'num': num_results
        }
        search_url = f"https://serpapi.com/search?{urlencode(params)}"
        
        # Don't use Tor for API calls
        response = requests.get(search_url, timeout=10)
        if response.status_code != 200:
            logger.error(f"SerpAPI search failed with status code {response.status_code}")
            return []
            
        # Parse JSON response
        data = response.json()
        results = []
        
        if 'organic_results' in data:
            for result in data['organic_results'][:num_results]:
                results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'url': result.get('link', ''),
                    'source': 'serpapi'
                })
                
        return results
    except Exception as e:
        logger.error(f"Error in SerpAPI search: {e}")
        return []

def extract_web_content(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract content from a web page
    
    Args:
        url: The URL to extract content from
        
    Returns:
        Dictionary with title, text content, and metadata
    """
    logger.info(f"Extracting content from: {url}")
    
    session = TorSession()
    
    try:
        response = session.get(url, timeout=10)
        if response.status_code != 200:
            logger.error(f"Failed to fetch URL: {response.status_code}")
            return None
            
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get title and clean it up
        title = soup.title.string.strip() if soup.title else ""
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text and clean it up
        text = soup.get_text(separator=' ', strip=True)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Extract metadata
        meta_tags = soup.find_all('meta')
        metadata = {}
        
        for tag in meta_tags:
            if tag.get('name'):
                metadata[tag.get('name')] = tag.get('content', '')
            elif tag.get('property'):
                metadata[tag.get('property')] = tag.get('content', '')
        
        return {
            'title': title,
            'text': text,
            'url': url,
            'metadata': metadata
        }
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {e}")
        return None

# API endpoint for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    query = "privacy technologies"
    print(f"Searching for: {query}")
    
    results = search_web(query, 3)
    print(json.dumps(results, indent=2))
    
    if results:
        print("\nExtracting content from first result:")
        content = extract_web_content(results[0]['url'])
        if content:
            print(f"Title: {content['title']}")
            print(f"Text snippet: {content['text'][:200]}...")
