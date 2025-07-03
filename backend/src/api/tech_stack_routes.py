"""
Tech Stack API Routes for Knowledge Base Assistant
Stub endpoints for Node.js, Rails, Spring, and other backend integrations.
"""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/tech", tags=["tech_stack"])

# Node.js integration stub
@router.post("/nodejs/run")
def run_nodejs_script(script: str):
    """Run a Node.js script (stub)"""
    # In production, use subprocess or a Node.js microservice
    return {"status": "not_implemented", "detail": "Node.js integration not implemented yet."}

# Rails integration stub
@router.post("/rails/action")
def call_rails_action(controller: str, action: str, data: dict):
    """Call a Rails controller action (stub)"""
    return {"status": "not_implemented", "detail": "Rails integration not implemented yet."}

# Spring integration stub
@router.post("/spring/endpoint")
def call_spring_endpoint(path: str, data: dict):
    """Call a Spring endpoint (stub)"""
    return {"status": "not_implemented", "detail": "Spring integration not implemented yet."}

# General tech stack info
@router.get("/info")
def get_tech_stack_info():
    """Get information about supported tech stack"""
    return {
        "frontend": ["React", "jQuery", "HTML", "CSS", "JS", "Responsive Web"],
        "backend": ["FastAPI", "Django", "Rails", "Spring", "Node.js"],
        "databases": ["SQL", "NoSQL", "MySQL", "PostgreSQL", "MongoDB"]
    }
