"""
Enhanced API response models and utilities for consistent response formatting.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List, Union
from datetime import datetime
from enum import Enum

class ResponseStatus(str, Enum):
    """Standard response status values."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"

class ResponseCode(str, Enum):
    """Standard response codes."""
    OK = "OK"
    CREATED = "CREATED"
    ACCEPTED = "ACCEPTED"
    NO_CONTENT = "NO_CONTENT"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

class ResponseMetadata(BaseModel):
    """Metadata included in API responses."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    version: str = "2.0.0"
    processing_time_ms: Optional[float] = None
    
class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""
    page: int = Field(ge=1, description="Current page number")
    limit: int = Field(ge=1, le=100, description="Items per page")
    total_items: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_prev: bool = Field(description="Whether there are previous pages")

class StandardResponse(BaseModel):
    """Standard API response format."""
    status: ResponseStatus
    code: ResponseCode
    message: str
    data: Optional[Any] = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)

class ListResponse(BaseModel):
    """Response format for list endpoints."""
    status: ResponseStatus
    code: ResponseCode
    message: str
    data: List[Any]
    pagination: Optional[PaginationMeta] = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)

class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = None
    code: str
    message: str
    value: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Standard error response format."""
    status: ResponseStatus = ResponseStatus.ERROR
    code: ResponseCode
    message: str
    errors: Optional[List[ErrorDetail]] = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)

# File operation responses
class FileUploadResponse(BaseModel):
    """Response for file upload operations."""
    file_id: str
    filename: str
    size_bytes: int
    size_mb: float
    workspace_id: str
    status: str
    storage_path: Optional[str] = None
    processing_status: Optional[str] = None

class FileListResponse(BaseModel):
    """Response for file listing operations."""
    files: List[Dict[str, Any]]
    total_files: int
    workspace_id: str
    
class FileInfoResponse(BaseModel):
    """Response for file information."""
    file_info: Dict[str, Any]
    metadata: Dict[str, Any]
    content_preview: Optional[str] = None

# Search operation responses
class SearchResultItem(BaseModel):
    """Individual search result item."""
    id: str
    title: str
    content: str
    score: float
    source: str
    file_id: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    """Response for search operations."""
    query: str
    answer: str
    confidence: float
    results: List[SearchResultItem]
    total_results: int
    processing_time_seconds: float
    search_metadata: Dict[str, Any]

# AI operation responses
class AIOperationResponse(BaseModel):
    """Response for AI operations."""
    operation: str
    model_used: str
    result: Any
    confidence: Optional[float] = None
    processing_time_seconds: float
    token_count: Optional[int] = None
    metadata: Dict[str, Any]

# Health check response
class HealthCheckResponse(BaseModel):
    """Response for health check."""
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: Optional[float] = None
    services: Dict[str, Dict[str, Any]]
    system_info: Dict[str, Any]
