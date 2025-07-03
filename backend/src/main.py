from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import json
from typing import List, Optional

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

# Example: Search for a keyword in the knowledge base (simple version)
@app.get("/search")
def search_knowledge_base(q: str):
    base_path = Path(__file__).parent.parent.parent / "src"
    results = []
    for dirpath, _, filenames in os.walk(base_path):
        for fname in filenames:
            if fname.startswith(".") or fname.endswith(".pyc"):
                continue
            fpath = Path(dirpath) / fname
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    if q.lower() in text.lower():
                        results.append({"file": str(fpath), "snippet": text[:200]})
            except Exception:
                continue
    return {"results": results[:20]}  # limit to 20 results for demo

# Code generation endpoint
from pydantic import BaseModel
class CodeGenRequest(BaseModel):
    prompt: str
    language: str = "python"
    max_tokens: int = 256

@app.post("/generate_code")
def generate_code(req: CodeGenRequest):
    # TODO: Replace with real LLM integration (OpenAI, local, etc.)
    # For now, return a dummy code snippet
    if not os.environ.get("OPENAI_API_KEY"):
        return {"code": f"# Example {req.language} code for: {req.prompt}\ndef example():\n    pass\n"}
    # If OpenAI key is set, call OpenAI API (pseudo-code)
    # ...
    return {"code": f"# [LLM] {req.language} code for: {req.prompt}\ndef example():\n    pass\n"}

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

@app.get("/")
def root():
    return {"status": "Knowledge Base Assistant API is running"}
