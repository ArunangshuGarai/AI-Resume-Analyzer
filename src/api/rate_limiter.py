"""
Rate limiting middleware for API
Add this to src/api/rate_limiter.py
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import time
from collections import defaultdict, deque
from typing import Dict, Deque

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
    
    def is_allowed(self, client_ip: str) -> tuple[bool, int]:
        """Check if request is allowed, return (allowed, time_until_reset)"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        client_requests = self.requests[client_ip]
        while client_requests and client_requests[0] < minute_ago:
            client_requests.popleft()
        
        # Check if limit exceeded
        if len(client_requests) >= self.requests_per_minute:
            oldest_request = client_requests[0]
            time_until_reset = int(60 - (now - oldest_request))
            return False, time_until_reset
        
        # Add current request
        client_requests.append(now)
        return True, 0

# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=5)  # Conservative limit

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    
    # Skip rate limiting for health check and docs
    if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    client_ip = request.client.host
    allowed, time_until_reset = rate_limiter.is_allowed(client_ip)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Try again in {time_until_reset} seconds.",
                "retry_after": time_until_reset
            },
            headers={"Retry-After": str(time_until_reset)}
        )
    
    response = await call_next(request)
    return response