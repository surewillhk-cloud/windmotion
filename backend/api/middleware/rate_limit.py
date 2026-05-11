"""Rate limiting middleware."""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.requests: dict = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean old entries
        self.requests = {k: v for k, v in self.requests.items() if now - v[-1] < 60}

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Check rate limit
        recent = [t for t in self.requests[client_ip] if now - t < 60]
        if len(recent) >= self.rpm:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        self.requests[client_ip].append(now)
        response = await call_next(request)
        return response
