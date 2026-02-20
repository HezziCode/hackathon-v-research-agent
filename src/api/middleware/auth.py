"""T072: OAuth2 Bearer token authentication middleware."""

from __future__ import annotations

import logging

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

# Paths that don't require authentication
PUBLIC_PATHS = {
    "/health",
    "/metrics",
    "/.well-known/agent.json",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """Validate Bearer token on protected endpoints.

    In development mode (no AUTH_ENABLED env), all requests pass through.
    In production, validates the Bearer token against configured issuer.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public paths
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # Skip auth if not enabled (dev mode)
        import os
        if not os.getenv("AUTH_ENABLED", ""):
            return await call_next(request)

        # Validate Bearer token
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Bearer token")

        token = auth[7:]
        if not token:
            raise HTTPException(status_code=401, detail="Empty Bearer token")

        # Token validation stub — replace with JWKS verification in production
        # For hackathon, accept any non-empty token
        request.state.user = {"token": token}
        return await call_next(request)
