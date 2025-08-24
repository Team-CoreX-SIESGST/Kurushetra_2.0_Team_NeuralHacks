"""
Centralized exception handling for OmniSearch AI.
Provides consistent error responses and proper logging.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Dict, Any, Optional
import traceback
from datetime import datetime
from app.utils.logging_config import get_logger, log_exception

logger = get_logger("exception_handler")

class OmniSearchException(Exception):
    """Base exception for OmniSearch AI application."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "OMNISEARCH_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

class ValidationException(OmniSearchException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )

class AuthenticationException(OmniSearchException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401
        )

class AuthorizationException(OmniSearchException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403
        )

class ResourceNotFoundException(OmniSearchException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )

class RateLimitException(OmniSearchException):
    """Exception for rate limit exceeded."""
    
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after}
        )

class FileProcessingException(OmniSearchException):
    """Exception for file processing errors."""
    
    def __init__(self, message: str, filename: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="FILE_PROCESSING_ERROR",
            status_code=422,
            details={"filename": filename, **(details or {})}
        )

class AIServiceException(OmniSearchException):
    """Exception for AI service errors."""
    
    def __init__(self, service_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{service_name} error: {message}",
            error_code="AI_SERVICE_ERROR",
            status_code=503,
            details={"service": service_name, **(details or {})}
        )

class StorageException(OmniSearchException):
    """Exception for storage service errors."""
    
    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Storage {operation} failed: {message}",
            error_code="STORAGE_ERROR",
            status_code=503,
            details={"operation": operation, **(details or {})}
        )

def create_error_response(
    request: Request,
    error_code: str,
    message: str,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized error response."""
    
    error_response = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
            "method": request.method,
        }
    }
    
    if details:
        error_response["error"]["details"] = details
    
    # Add request ID if available
    if hasattr(request.state, 'request_id'):
        error_response["error"]["request_id"] = request.state.request_id
    
    # Add trace ID for debugging in development
    if hasattr(request.state, 'trace_id'):
        error_response["error"]["trace_id"] = request.state.trace_id
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )

async def omnisearch_exception_handler(request: Request, exc: OmniSearchException) -> JSONResponse:
    """Handle custom OmniSearch exceptions."""
    
    log_exception(
        logger,
        exc,
        extra_data={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "request_path": str(request.url.path),
            "request_method": request.method,
            "details": exc.details
        }
    )
    
    return create_error_response(
        request=request,
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details if exc.details else None
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED", 
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE"
    }
    
    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
    
    # Log the exception
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            'extra_data': {
                'status_code': exc.status_code,
                'detail': exc.detail,
                'request_path': str(request.url.path),
                'request_method': request.method,
                'type': 'http_exception'
            }
        }
    )
    
    return create_error_response(
        request=request,
        error_code=error_code,
        message=str(exc.detail),
        status_code=exc.status_code
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    
    # Log the full exception with stack trace
    log_exception(
        logger,
        exc,
        extra_data={
            "request_path": str(request.url.path),
            "request_method": request.method,
            "exception_type": type(exc).__name__
        }
    )
    
    # Don't expose internal error details in production
    message = "An internal server error occurred"
    details = None
    
    # In development, provide more details
    import os
    if os.getenv("DEBUG", "false").lower() == "true":
        message = f"Internal error: {str(exc)}"
        details = {
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc().split('\n')
        }
    
    return create_error_response(
        request=request,
        error_code="INTERNAL_SERVER_ERROR",
        message=message,
        status_code=500,
        details=details
    )

def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    
    # Custom exception handlers
    app.add_exception_handler(OmniSearchException, omnisearch_exception_handler)
    app.add_exception_handler(ValidationException, omnisearch_exception_handler)
    app.add_exception_handler(AuthenticationException, omnisearch_exception_handler)
    app.add_exception_handler(AuthorizationException, omnisearch_exception_handler)
    app.add_exception_handler(ResourceNotFoundException, omnisearch_exception_handler)
    app.add_exception_handler(RateLimitException, omnisearch_exception_handler)
    app.add_exception_handler(FileProcessingException, omnisearch_exception_handler)
    app.add_exception_handler(AIServiceException, omnisearch_exception_handler)
    app.add_exception_handler(StorageException, omnisearch_exception_handler)
    
    # HTTP exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # General exception handler (catch-all)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered successfully")
