"""
Rate limiting middleware for OmniSearch AI.
Prevents server overload by limiting concurrent uploads and processing.
"""

import time
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RateLimiter:
    """Rate limiter implementation with sliding window and token bucket algorithms."""
    
    def __init__(self):
        # Sliding window rate limiting (requests per time window)
        self.windows = defaultdict(lambda: deque())
        
        # Token bucket for burst control
        self.buckets = defaultdict(lambda: {'tokens': 10, 'last_refill': time.time()})
        
        # Active uploads tracking
        self.active_uploads = defaultdict(int)
        self.active_processing = defaultdict(int)
        
        # Global counters
        self.global_active_uploads = 0
        self.global_active_processing = 0
        
        # Configuration
        self.config = {
            # Per-user limits
            'requests_per_minute': 30,      # Max requests per minute per user
            'requests_per_hour': 200,       # Max requests per hour per user
            'uploads_per_minute': 5,        # Max uploads per minute per user
            'uploads_per_hour': 20,         # Max uploads per hour per user
            'concurrent_uploads_per_user': 3,  # Max concurrent uploads per user
            
            # Global limits
            'max_global_uploads': 10,       # Max concurrent uploads server-wide
            'max_global_processing': 5,     # Max concurrent processing jobs
            
            # Token bucket settings
            'bucket_size': 10,              # Token bucket size
            'refill_rate': 1,               # Tokens per second
            
            # File size limits
            'max_file_size_mb': 10,         # Max file size in MB
        }
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (user ID or IP address)."""
        # Try to get user ID from JWT token or session
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Fallback to IP address
        client_ip = request.client.host
        return f"ip:{client_ip}"
    
    def _clean_old_entries(self, window: deque, max_age: int):
        """Remove entries older than max_age seconds."""
        cutoff_time = time.time() - max_age
        while window and window[0] < cutoff_time:
            window.popleft()
    
    def check_rate_limit(
        self, 
        client_id: str, 
        endpoint_type: str = "general"
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if request is within rate limits.
        
        Args:
            client_id: Client identifier
            endpoint_type: Type of endpoint ('general', 'upload', 'processing')
        
        Returns:
            Tuple of (allowed, error_message, retry_after_seconds)
        """
        current_time = time.time()
        
        # Get appropriate limits based on endpoint type
        if endpoint_type == 'upload':
            minute_limit = self.config['uploads_per_minute']
            hour_limit = self.config['uploads_per_hour']
        else:
            minute_limit = self.config['requests_per_minute']
            hour_limit = self.config['requests_per_hour']
        
        # Check sliding window limits
        minute_window_key = f"{client_id}:minute"
        hour_window_key = f"{client_id}:hour"
        
        # Clean old entries
        self._clean_old_entries(self.windows[minute_window_key], 60)
        self._clean_old_entries(self.windows[hour_window_key], 3600)
        
        # Check minute limit
        if len(self.windows[minute_window_key]) >= minute_limit:
            return False, f"Rate limit exceeded: {minute_limit} requests per minute", 60
        
        # Check hour limit
        if len(self.windows[hour_window_key]) >= hour_limit:
            return False, f"Rate limit exceeded: {hour_limit} requests per hour", 3600
        
        # Check token bucket for burst control
        bucket = self.buckets[client_id]
        time_passed = current_time - bucket['last_refill']
        
        # Refill tokens
        bucket['tokens'] = min(
            self.config['bucket_size'],
            bucket['tokens'] + time_passed * self.config['refill_rate']
        )
        bucket['last_refill'] = current_time
        
        # Check if tokens available
        if bucket['tokens'] < 1:
            return False, "Rate limit exceeded: too many requests in short time", 10
        
        # Consume token
        bucket['tokens'] -= 1
        
        # Add to windows
        self.windows[minute_window_key].append(current_time)
        self.windows[hour_window_key].append(current_time)
        
        return True, None, None
    
    def check_concurrent_limits(
        self, 
        client_id: str, 
        operation_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check concurrent operation limits.
        
        Args:
            client_id: Client identifier
            operation_type: 'upload' or 'processing'
        
        Returns:
            Tuple of (allowed, error_message)
        """
        if operation_type == 'upload':
            # Check per-user concurrent uploads
            if self.active_uploads[client_id] >= self.config['concurrent_uploads_per_user']:
                return False, f"Too many concurrent uploads (max: {self.config['concurrent_uploads_per_user']})"
            
            # Check global concurrent uploads
            if self.global_active_uploads >= self.config['max_global_uploads']:
                return False, f"Server busy: too many concurrent uploads (max: {self.config['max_global_uploads']})"
        
        elif operation_type == 'processing':
            # Check global concurrent processing
            if self.global_active_processing >= self.config['max_global_processing']:
                return False, f"Server busy: too many files being processed (max: {self.config['max_global_processing']})"
        
        return True, None
    
    def start_operation(self, client_id: str, operation_type: str):
        """Mark start of an operation."""
        if operation_type == 'upload':
            self.active_uploads[client_id] += 1
            self.global_active_uploads += 1
        elif operation_type == 'processing':
            self.active_processing[client_id] += 1
            self.global_active_processing += 1
    
    def end_operation(self, client_id: str, operation_type: str):
        """Mark end of an operation."""
        if operation_type == 'upload':
            self.active_uploads[client_id] = max(0, self.active_uploads[client_id] - 1)
            self.global_active_uploads = max(0, self.global_active_uploads - 1)
        elif operation_type == 'processing':
            self.active_processing[client_id] = max(0, self.active_processing[client_id] - 1)
            self.global_active_processing = max(0, self.global_active_processing - 1)
    
    def get_status(self) -> Dict:
        """Get current rate limiter status."""
        return {
            'global_stats': {
                'active_uploads': self.global_active_uploads,
                'active_processing': self.global_active_processing,
                'max_uploads': self.config['max_global_uploads'],
                'max_processing': self.config['max_global_processing']
            },
            'config': self.config,
            'active_clients': len(self.active_uploads) + len(self.active_processing)
        }

# Global rate limiter instance
rate_limiter = RateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        
        # Skip rate limiting for health checks and docs
        if request.url.path in ['/health', '/docs', '/redoc', '/openapi.json']:
            return await call_next(request)
        
        client_id = rate_limiter._get_client_id(request)
        
        # Determine endpoint type
        endpoint_type = "general"
        if "/upload" in request.url.path:
            endpoint_type = "upload"
        elif "/processing" in request.url.path:
            endpoint_type = "processing"
        
        # Check rate limits
        allowed, error_msg, retry_after = rate_limiter.check_rate_limit(
            client_id, 
            endpoint_type
        )
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": error_msg,
                    "retry_after": retry_after,
                    "timestamp": datetime.now().isoformat()
                },
                headers={"Retry-After": str(retry_after)} if retry_after else {}
            )
        
        # Check concurrent limits for uploads
        if endpoint_type == "upload" and request.method == "POST":
            concurrent_allowed, concurrent_error = rate_limiter.check_concurrent_limits(
                client_id, 
                "upload"
            )
            
            if not concurrent_allowed:
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": "Service unavailable",
                        "message": concurrent_error,
                        "retry_after": 30,
                        "timestamp": datetime.now().isoformat()
                    },
                    headers={"Retry-After": "30"}
                )
            
            # Mark upload operation start
            rate_limiter.start_operation(client_id, "upload")
            
            try:
                response = await call_next(request)
                return response
            finally:
                # Always mark operation end
                rate_limiter.end_operation(client_id, "upload")
        
        else:
            # For non-upload endpoints, just proceed
            return await call_next(request)

class FileSizeValidator:
    """Validator for file size limits."""
    
    @staticmethod
    def validate_file_size(content_length: Optional[int]) -> Tuple[bool, Optional[str]]:
        """
        Validate file size.
        
        Args:
            content_length: Content length from request headers
        
        Returns:
            Tuple of (valid, error_message)
        """
        max_size_bytes = rate_limiter.config['max_file_size_mb'] * 1024 * 1024
        
        if content_length is None:
            return False, "Content-Length header is required"
        
        if content_length > max_size_bytes:
            return False, f"File too large. Maximum size: {rate_limiter.config['max_file_size_mb']}MB"
        
        if content_length <= 0:
            return False, "Invalid file size"
        
        return True, None

# Dependency for file size validation
async def validate_file_size_dependency(request: Request):
    """FastAPI dependency for file size validation."""
    content_length = request.headers.get('content-length')
    
    if content_length:
        try:
            content_length = int(content_length)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid Content-Length header"
            )
        
        valid, error_msg = FileSizeValidator.validate_file_size(content_length)
        
        if not valid:
            raise HTTPException(status_code=413, detail=error_msg)
    
    return True
