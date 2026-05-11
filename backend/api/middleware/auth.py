"""Authentication middleware."""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Simple API key authentication."""

    EXEMPT_PATHS = {"/docs", "/openapi.json", "/health", "/api/embed"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXEMPT_PATHS or request.url.path.startswith("/api/embed"):
            return await call_next(request)

        # In production: validate JWT or API key
        # For now, pass through
        response = await call_next(request)
        return response
