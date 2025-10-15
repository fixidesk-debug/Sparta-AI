"""
Custom middleware for the application
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import time
import logging
import uuid

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses"""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(duration * 1000, 2))
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.exception(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                }
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers"""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: dict = {}
        self.window_start_times: dict = {}
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limiting for health check
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_id = request.client.host if request.client else "unknown"
        
        # Get current time
        current_time = time.time()
        
        # Initialize tracking for new clients
        if client_id not in self.request_counts:
            self.request_counts[client_id] = 0
            self.window_start_times[client_id] = current_time
        
        # Check if we're in a new time window (1 minute)
        if current_time - self.window_start_times[client_id] >= 60:
            self.request_counts[client_id] = 0
            self.window_start_times[client_id] = current_time
        
        # Increment request count
        self.request_counts[client_id] += 1
        
        # Check rate limit
        if self.request_counts[client_id] > self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for client: {client_id}",
                extra={
                    "client_id": client_id,
                    "request_count": self.request_counts[client_id],
                    "limit": self.requests_per_minute,
                }
            )
            return Response(
                content='{"error": "Rate limit exceeded. Please try again later."}',
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": "60"
                }
            )
        
        return await call_next(request)
