from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import json
from typing import List, Optional, Dict, Any

# Import web search module
from web_search import search_web, extract_web_content
from web_automation import WebAutomation
from networking import connect_vpn, set_dns, start_voip_client, get_network_status
import logging

app = FastAPI(title="Knowledge Base Assistant API")

# Allow CORS for local development and cross-platform clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example: List top-level categories (directories) in the knowledge base
@app.get("/categories")
def get_categories():
    base_path = Path(__file__).parent.parent.parent / "src"
    categories = []
    for item in base_path.iterdir():
        if item.is_dir():
            categories.append({"id": item.name, "name": item.name.replace('_', ' ').title()})
    return {"categories": categories}

# Example: List files in a category
def list_files_in_dir(directory: Path) -> List[dict]:
    files = []
    for item in directory.iterdir():
        if item.is_file() and not item.name.startswith("."):
            files.append({"name": item.name, "path": str(item)})
        elif item.is_dir():
            files.append({"name": item.name, "path": str(item), "is_dir": True})
    return files

@app.get("/category/{category_id}/files")
def get_category_files(category_id: str):
    base_path = Path(__file__).parent.parent.parent / "src" / category_id
    if not base_path.exists():
        return {"error": "Category not found"}
    return {"files": list_files_in_dir(base_path)}

# Example: Get file content (for docs, code, etc.)
@app.get("/file")
def get_file_content(path: str = Query(..., description="Absolute or relative file path")):
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return {"error": "File not found"}
    # Limit file size for safety
    if file_path.stat().st_size > 100_000:
        return {"error": "File too large to display"}
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    return {"content": content}

# Enhanced search for the knowledge base with improved error handling and logging
import logging
import traceback
from backend.src.monitoring.prometheus_metrics import setup_metrics
from backend.src.monitoring.sentry_integration import init_sentry
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from backend.src.agents.codegen_agent import CodeGenAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Monitoring and Analytics Integration ---
# Initialize Prometheus metrics and Sentry error tracking at app startup
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    init_sentry(SENTRY_DSN)
    app.add_middleware(SentryAsgiMiddleware)
setup_metrics(app)

# --- End Monitoring Setup ---

# --- Agent Registration ---
codegen_agent = CodeGenAgent()
# --- End Agent Registration ---

@app.get("/search")
def search_knowledge_base(q: str):
    """Search the knowledge base for the given query with enhanced error handling.
    
    This function will try multiple search paths if the primary one fails.
    It also implements improved error reporting and returns diagnostic info.
    """
    if not q or len(q.strip()) == 0:
        return {"results": [], "message": "Empty query"}
    
    try:
        # Try multiple possible knowledge base paths
        paths_to_try = [
            Path(__file__).parent.parent.parent / "src",           # Standard path
            Path(__file__).parent.parent.parent,                  # Root path
            Path(__file__).parent.parent.parent / "knowledge_base", # Alt. structure
            Path.cwd() / "knowledge_base",                        # Current working dir
        ]
        
        results = []
        searched_paths = []
        files_checked = 0
        
        # Log the search attempt
        logger.info(f"Searching for: '{q}' in knowledge base")
        
        # Try each path until we find something
        for base_path in paths_to_try:
            if not base_path.exists() or not base_path.is_dir():
                logger.info(f"Path does not exist or is not a directory: {base_path}")
                continue
                
            searched_paths.append(str(base_path))
            logger.info(f"Searching in path: {base_path}")
            
            # Look for both exact and partial matches
            for dirpath, _, filenames in os.walk(base_path):
                for fname in filenames:
                    # Skip hidden files, binaries, etc.
                    if (fname.startswith(".") or fname.endswith((".pyc", ".jpg", ".png", ".gif")))\
                       or "__pycache__" in dirpath:
                        continue
                    
                    fpath = Path(dirpath) / fname
                    files_checked += 1
                    
                    # Skip large files
                    try:
                        if fpath.stat().st_size > 500_000:  # 500KB max
                            continue
                    except Exception:
                        continue
                        
                    # Read and search content
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            text = f.read()
                            # Look for case-insensitive matches
                            if q.lower() in text.lower():
                                # Find the context where the match occurs
                                pos = text.lower().find(q.lower())
                                start = max(0, pos - 50)
                                end = min(len(text), pos + len(q) + 50)
                                snippet = f"...{text[start:end]}..."
                                
                                results.append({
                                    "file": str(fpath),
                                    "snippet": snippet,
                                    "title": fname
                                })
                                
                                # For debugging - log matches
                                logger.info(f"Match found in: {fpath}")
                    except Exception as e:
                        logger.debug(f"Error reading {fpath}: {e}")
                        continue
            
            # If we found results in this path, stop searching other paths
            if results:
                break
                
        # Return results with diagnostic info
        return {
            "results": results[:30],  # increased limit to 30 results
            "query": q,
            "diagnostic": {
                "paths_searched": searched_paths,
                "files_checked": files_checked,
                "total_results": len(results)
            }
        }
    except Exception as e:
        # Log the full error with traceback
        error_details = traceback.format_exc()
        logger.error(f"Search error: {e}\n{error_details}")
        
        # Return a detailed error for debugging
        return {
            "error": "Failed to search knowledge base",
            "details": str(e),
            "query": q
        }

# Code generation endpoint
from pydantic import BaseModel
class CodeGenRequest(BaseModel):
    prompt: str
    language: str = "python"
    max_tokens: int = 256

@app.post("/generate_code")
def generate_code(req: CodeGenRequest):
    # Use the registered CodeGenAgent for code generation
    try:
        result = codegen_agent.generate_code(req.prompt, req.language)
        return result
    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")


from fastapi import File, UploadFile
@app.post("/analyze_multimodal")
def analyze_multimodal(file: UploadFile = File(...), type: str = "image"):
    # TODO: Integrate with real multimodal recognition API
    # For now, return dummy response
    if type == "image":
        return {"result": "Detected objects: cat, laptop"}
    elif type == "audio":
        return {"result": "Recognized speech: 'Hello world'"}
    else:
        return {"result": "Unsupported type"}

# Web search endpoints
@app.get("/web-search")
def web_search_endpoint(query: str, num_results: int = 5):
    """
    Search the web using Tor for privacy (if enabled)
    
    Args:
        query: Search query
        num_results: Number of results to return (default: 5)
        
    Returns:
        List of search results
    """
    if not query or len(query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query parameter is required")
        
    try:
        results = search_web(query, num_results)
        return {"results": results, "query": query}
    except Exception as e:
        logging.error(f"Web search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/extract-content")
def extract_content_endpoint(url: str):
    """
    Extract and parse content from a web page
    
    Args:
        url: URL to extract content from
        
    Returns:
        Parsed content including title, text, and metadata
    """
    if not url or len(url.strip()) == 0:
        raise HTTPException(status_code=400, detail="URL parameter is required")
        
    try:
        content = extract_web_content(url)
        if not content:
            raise HTTPException(status_code=404, detail="Failed to extract content from URL")
        return content
    except Exception as e:
        logging.error(f"Content extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@app.post("/automate")
def automate_endpoint(payload: dict):
    """
    Run web automation tasks (agent-driven). Accepts JSON with:
    - url: Target URL
    - actions: List of actions (goto, fill_form, click, screenshot, run_script)
    - selectors: Dict of selectors/values for form filling/clicking
    - script: Optional JS to run
    - headless: Whether to run headless (default True)
    - use_playwright: Whether to prefer Playwright (default True)
    Returns: automation results (success, screenshot path, HTML, errors)
    """
    import tempfile
    import base64
    try:
        url = payload.get('url')
        actions = payload.get('actions', [])
        selectors = payload.get('selectors', {})
        script = payload.get('script')
        headless = payload.get('headless', True)
        use_playwright = payload.get('use_playwright', True)
        screenshot_b64 = None
        html = None
        logs = []
        errors = []
        with WebAutomation(headless=headless, use_playwright=use_playwright) as bot:
            for action in actions:
                if action == 'goto':
                    bot.goto(url)
                    logs.append(f"Navigated to {url}")
                elif action == 'fill_form':
                    bot.fill_form(selectors)
                    logs.append(f"Filled form fields {selectors}")
                elif action == 'click':
                    for sel in selectors:
                        bot.click(sel)
                        logs.append(f"Clicked {sel}")
                elif action == 'screenshot':
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpf:
                        bot.screenshot(tmpf.name)
                        tmpf.seek(0)
                        screenshot_b64 = base64.b64encode(tmpf.read()).decode()
                        logs.append(f"Screenshot captured")
                elif action == 'run_script' and script:
                    result = bot.run_script(script)
                    logs.append(f"Script run, result: {result}")
                elif action == 'get_content':
                    html = bot.get_content()
                    logs.append("HTML content captured")
                else:
                    logs.append(f"Unknown action: {action}")
        return {
            "success": True,
            "logs": logs,
            "screenshot_b64": screenshot_b64,
            "html": html,
            "errors": errors
        }
    except Exception as e:
        logging.error(f"Automation error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/vpn/connect")
def vpn_connect(payload: dict):
    """Connect to a VPN using OpenVPN or WireGuard. Payload: {config_path, vpn_type}"""
    try:
        config_path = payload.get('config_path')
        vpn_type = payload.get('vpn_type', 'openvpn')
        result = connect_vpn(config_path, vpn_type)
        return {"success": result}
    except Exception as e:
        logging.error(f"VPN connect error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/dns/set")
def dns_set(payload: dict):
    """Set DNS servers. Payload: {nameservers: list, method: system|doh|dot}"""
    try:
        nameservers = payload.get('nameservers', [])
        method = payload.get('method', 'system')
        result = set_dns(nameservers, method)
        return {"success": result}
    except Exception as e:
        logging.error(f"DNS set error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/voip/start")
def voip_start(payload: dict):
    """Start a VOIP client. Payload: {sip_account: dict}"""
    try:
        sip_account = payload.get('sip_account', {})
        result = start_voip_client(sip_account)
        return {"success": result}
    except Exception as e:
        logging.error(f"VOIP start error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/network/status")
def network_status():
    """Get basic network status and diagnostics."""
    try:
        status = get_network_status()
        return status
    except Exception as e:
        logging.error(f"Network status error: {e}")
        return {"error": str(e)}

@app.get("/")
def root():
    return {"status": "Knowledge Base Assistant API is running", "features": ["knowledge base", "search", "code generation", "multimodal", "web search", "web automation", "vpn", "dns", "voip"]}
