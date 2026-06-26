import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentiment_platform.api")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that intercept incoming HTTP requests, tracks response status codes,
    and logs overall execution durations.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate execution duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log analytics details
        logger.info(
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Latency: {duration_ms:.2f}ms"
        )
        
        # Add execution time to headers
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        
        return response
