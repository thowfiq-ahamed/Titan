"""
TITAN Platform API - Authentication & Security
Provides API key and Token validation dependencies.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from .config import settings

api_key_header = APIKeyHeader(name="X-Titan-API-Key", auto_error=False)


def require_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verifies that the provided API key matches the configured platform key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required 'X-Titan-API-Key' header."
        )
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid platform API key."
        )
    return api_key
