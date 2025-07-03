"""
Django Integration Service for Knowledge Base Assistant
Provides a bridge between the FastAPI backend and Django framework
Enables Django models, views, and admin functionality
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union
import importlib
import inspect
import sys
from pathlib import Path
from datetime import datetime

# FastAPI imports
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class DjangoViewRequest(BaseModel):
    """Request data for a Django view call"""
    view_name: str
    method: str = "GET"
    params: Dict[str, Any] = Field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    
class DjangoModelRequest(BaseModel):
    """Request data for Django model operations"""
    model_name: str
    operation: str  # get, create, update, delete
    filters: Dict[str, Any] = Field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    order_by: Optional[List[str]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

class DjangoAdminRequest(BaseModel):
    """Request data for Django admin operations"""
    model_name: str
    action_name: str
    object_ids: List[str] = Field(default_factory=list)
    
class DjangoResponse(BaseModel):
    """Standard response format for Django integration"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

# Django integration service
class DjangoService:
    """
    Service for integrating with Django applications
    Provides access to Django models, views, and admin functionality
    """
    
    def __init__(self, django_settings_module: str = None, django_path: str = None):
        """
        Initialize Django integration
        
        Args:
            django_settings_module: Python path to Django settings module
            django_path: Path to Django project root
        """
        self.django_initialized = False
        self.settings_module = django_settings_module or os.environ.get('DJANGO_SETTINGS_MODULE')
        self.django_path = django_path or os.environ.get('DJANGO_PATH', './django_app')
        
        # Try to initialize Django if settings are provided
        if self.settings_module:
            self._initialize_django()
    
    def _initialize_django(self):
        """Initialize Django environment"""
        try:
            # Add Django project to Python path if not already there
            django_path = Path(self.django_path).resolve()
            if str(django_path) not in sys.path:
                sys.path.insert(0, str(django_path))
            
            # Set Django settings
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', self.settings_module)
            
            # Configure Django
            import django
            django.setup()
            
            self.django_initialized = True
            logger.info(f"Django initialized with settings {self.settings_module}")
            
            # Import common Django modules after setup
            self.models = importlib.import_module('django.db.models')
            self.auth = importlib.import_module('django.contrib.auth')
            self.admin = importlib.import_module('django.contrib.admin')
            
        except ImportError as e:
            logger.error(f"Failed to import Django: {e}")
            raise Exception(f"Django is not installed or properly configured: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize Django: {e}")
            raise Exception(f"Django initialization failed: {e}")
    
    def _ensure_django_initialized(self):
        """Ensure Django is initialized before operations"""
        if not self.django_initialized:
            raise Exception("Django is not initialized. Provide settings module in constructor or environment variable.")
    
    def get_model(self, model_name: str):
        """
        Get Django model by name
        
        Args:
            model_name: Fully qualified model name (e.g., 'app.ModelName')
            
        Returns:
            Django model class
        """
        self._ensure_django_initialized()
        
        try:
            # Parse app and model name
            parts = model_name.split('.')
            if len(parts) != 2:
                raise ValueError(f"Invalid model name format: {model_name}. Use 'app.ModelName' format.")
                
            app_name, model_class_name = parts
            
            # Import app models
            module = importlib.import_module(f"{app_name}.models")
            
            # Get model class
            model_class = getattr(module, model_class_name)
            
            return model_class
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to get model {model_name}: {e}")
            raise Exception(f"Django model {model_name} not found: {e}")
    
    def get_view(self, view_name: str):
        """
        Get Django view function by name
        
        Args:
            view_name: Fully qualified view name (e.g., 'app.views.view_name')
            
        Returns:
            Django view function
        """
        self._ensure_django_initialized()
        
        try:
            # Parse module and view name
            parts = view_name.split('.')
            if len(parts) < 2:
                raise ValueError(f"Invalid view name format: {view_name}. Use 'app.views.view_name' format.")
                
            module_path = '.'.join(parts[:-1])
            view_func_name = parts[-1]
            
            # Import module
            module = importlib.import_module(module_path)
            
            # Get view function
            view_func = getattr(module, view_func_name)
            
            return view_func
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to get view {view_name}: {e}")
            raise Exception(f"Django view {view_name} not found: {e}")
    
    def call_view(self, request_data: DjangoViewRequest) -> DjangoResponse:
        """
        Call a Django view
        
        Args:
            request_data: View request data
            
        Returns:
            View response
        """
        self._ensure_django_initialized()
        
        try:
            view_func = self.get_view(request_data.view_name)
            
            # Import Django request/response modules
            from django.http import HttpRequest
            from django.http.response import HttpResponse
            from django.test.client import RequestFactory
            
            # Create Django request
            factory = RequestFactory()
            method = request_data.method.lower()
            
            if method == 'get':
                django_request = factory.get('/', request_data.params)
            elif method == 'post':
                django_request = factory.post('/', data=request_data.body, content_type='application/json')
            elif method == 'put':
                django_request = factory.put('/', data=request_data.body, content_type='application/json')
            elif method == 'delete':
                django_request = factory.delete('/', data=request_data.body, content_type='application/json')
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Call view function
            response = view_func(django_request)
            
            # Process response
            if isinstance(response, HttpResponse):
                try:
                    content = json.loads(response.content)
                except json.JSONDecodeError:
                    content = response.content.decode('utf-8')
                
                return DjangoResponse(
                    success=response.status_code < 400,
                    data=content,
                    meta={
                        'status_code': response.status_code,
                        'content_type': response.get('Content-Type', 'text/html')
                    }
                )
            else:
                # Non-HttpResponse result (e.g., direct dict return)
                return DjangoResponse(
                    success=True,
                    data=response
                )
                
        except Exception as e:
            logger.error(f"Failed to call Django view {request_data.view_name}: {e}")
            return DjangoResponse(success=False, error=str(e))
    
    def query_model(self, request_data: DjangoModelRequest) -> DjangoResponse:
        """
        Perform operations on a Django model
        
        Args:
            request_data: Model request data
            
        Returns:
            Model operation response
        """
        self._ensure_django_initialized()
        
        try:
            model_class = self.get_model(request_data.model_name)
            operation = request_data.operation.lower()
            
            # Handle different operations
            if operation == 'get':
                # Query model
                queryset = model_class.objects.filter(**request_data.filters)
                
                # Apply ordering
                if request_data.order_by:
                    queryset = queryset.order_by(*request_data.order_by)
                
                # Apply pagination
                if request_data.offset is not None:
                    queryset = queryset[request_data.offset:]
                
                if request_data.limit is not None:
                    queryset = queryset[:request_data.limit]
                
                # Convert to list of dicts
                result = list(queryset.values())
                
                return DjangoResponse(
                    success=True,
                    data=result,
                    meta={
                        'count': len(result),
                        'model': request_data.model_name
                    }
                )
                
            elif operation == 'create':
                # Create model instance
                if not request_data.data:
                    raise ValueError("Data is required for create operation")
                
                instance = model_class.objects.create(**request_data.data)
                
                return DjangoResponse(
                    success=True,
                    data={
                        'id': instance.pk,
                        **{f.name: getattr(instance, f.name) for f in instance._meta.fields}
                    },
                    meta={
                        'model': request_data.model_name,
                        'operation': 'create'
                    }
                )
                
            elif operation == 'update':
                # Update model instance(s)
                if not request_data.filters:
                    raise ValueError("Filters are required for update operation")
                
                if not request_data.data:
                    raise ValueError("Data is required for update operation")
                
                count = model_class.objects.filter(**request_data.filters).update(**request_data.data)
                
                return DjangoResponse(
                    success=True,
                    data={'updated_count': count},
                    meta={
                        'model': request_data.model_name,
                        'operation': 'update'
                    }
                )
                
            elif operation == 'delete':
                # Delete model instance(s)
                if not request_data.filters:
                    raise ValueError("Filters are required for delete operation")
                
                count, _ = model_class.objects.filter(**request_data.filters).delete()
                
                return DjangoResponse(
                    success=True,
                    data={'deleted_count': count},
                    meta={
                        'model': request_data.model_name,
                        'operation': 'delete'
                    }
                )
                
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            logger.error(f"Failed to perform {request_data.operation} on model {request_data.model_name}: {e}")
            return DjangoResponse(success=False, error=str(e))
    
    def perform_admin_action(self, request_data: DjangoAdminRequest) -> DjangoResponse:
        """
        Perform an admin action on model instances
        
        Args:
            request_data: Admin action request data
            
        Returns:
            Action response
        """
        self._ensure_django_initialized()
        
        try:
            model_class = self.get_model(request_data.model_name)
            
            # Find admin site and model admin
            from django.contrib.admin.sites import site
            
            # Get model admin
            model_admin = site._registry.get(model_class)
            if not model_admin:
                raise ValueError(f"No admin registered for model {request_data.model_name}")
            
            # Find action
            action = getattr(model_admin, request_data.action_name, None)
            if not action or not callable(action):
                # Check for general admin actions
                action = getattr(model_admin.admin_site, request_data.action_name, None)
            
            if not action or not callable(action):
                raise ValueError(f"Admin action {request_data.action_name} not found")
            
            # Get queryset of objects
            queryset = model_class.objects.filter(pk__in=request_data.object_ids)
            
            # Execute action
            from django.http import HttpRequest
            request = HttpRequest()
            result = action(model_admin, request, queryset)
            
            return DjangoResponse(
                success=True,
                data=result,
                meta={
                    'model': request_data.model_name,
                    'action': request_data.action_name,
                    'affected': queryset.count()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to perform admin action {request_data.action_name} on {request_data.model_name}: {e}")
            return DjangoResponse(success=False, error=str(e))

# Create FastAPI router for Django integration
def create_django_router(django_service: DjangoService = None) -> APIRouter:
    """
    Create FastAPI router for Django integration
    
    Args:
        django_service: Django service instance (optional)
        
    Returns:
        FastAPI router
    """
    router = APIRouter(
        prefix="/django",
        tags=["django"],
        responses={404: {"description": "Not found"}}
    )
    
    # Create service if not provided
    if django_service is None:
        django_service = DjangoService()
    
    @router.post("/view/{view_path:path}", response_model=DjangoResponse)
    async def call_django_view(
        view_path: str,
        request: Request
    ):
        """Call a Django view by path"""
        try:
            # Get request body
            body = await request.json() if request.headers.get('content-type') == 'application/json' else {}
            
            # Create request data
            request_data = DjangoViewRequest(
                view_name=view_path,
                method=request.method,
                params=dict(request.query_params),
                body=body
            )
            
            # Call view
            return django_service.call_view(request_data)
        except Exception as e:
            logger.error(f"Django view call error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/model/{model_path:path}", response_model=DjangoResponse)
    async def query_django_model(
        model_path: str,
        request_data: DjangoModelRequest
    ):
        """Query a Django model"""
        try:
            # Override model name from path
            request_data.model_name = model_path
            
            # Query model
            return django_service.query_model(request_data)
        except Exception as e:
            logger.error(f"Django model query error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/admin/{model_path:path}/{action}", response_model=DjangoResponse)
    async def admin_action(
        model_path: str,
        action: str,
        request_data: DjangoAdminRequest
    ):
        """Perform a Django admin action"""
        try:
            # Override model name and action from path
            request_data.model_name = model_path
            request_data.action_name = action
            
            # Perform action
            return django_service.perform_admin_action(request_data)
        except Exception as e:
            logger.error(f"Django admin action error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router


# Example usage when run as script
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example: Initialize Django service
    try:
        # Set environment variables
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_django_app.settings')
        os.environ.setdefault('DJANGO_PATH', './your_django_app')
        
        # Create service
        service = DjangoService()
        
        # Example: Get model
        print("Getting User model...")
        User = service.get_model('auth.User')
        print(f"User model fields: {[f.name for f in User._meta.fields]}")
        
        # Example: Query model
        print("Querying users...")
        request = DjangoModelRequest(
            model_name='auth.User',
            operation='get',
            filters={'is_staff': True},
            limit=5
        )
        result = service.query_model(request)
        print(f"Found {len(result.data)} staff users")
        
    except Exception as e:
        print(f"Example failed: {e}")
