"""Authentication and authorization."""
import os
import secrets
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import hashlib
import hmac

security = HTTPBearer()

# Admin API key from environment
ADMIN_API_KEY = os.getenv('SINGL_ADMIN_API_KEY', None)

# If no API key is set, generate one on startup
if not ADMIN_API_KEY:
    ADMIN_API_KEY = secrets.token_urlsafe(32)
    print(f"\n{'='*80}")
    print(f"⚠️  NO ADMIN API KEY SET! Generated temporary key:")
    print(f"   {ADMIN_API_KEY}")
    print(f"   Set SINGL_ADMIN_API_KEY environment variable for persistence.")
    print(f"{'='*80}\n")


def verify_api_key(api_key: str) -> bool:
    """
    Verify API key using constant-time comparison.

    Args:
        api_key: API key to verify

    Returns:
        True if valid, False otherwise
    """
    if not ADMIN_API_KEY:
        return False

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(api_key, ADMIN_API_KEY)


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    Dependency that requires valid authentication.

    Args:
        credentials: Bearer token from request header

    Returns:
        API key if valid

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = credentials.credentials

    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return api_key


async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[str]:
    """
    Dependency for optional authentication.

    Args:
        credentials: Bearer token from request header (optional)

    Returns:
        API key if provided and valid, None otherwise
    """
    if not credentials:
        return None

    api_key = credentials.credentials

    if verify_api_key(api_key):
        return api_key

    return None


def get_admin_api_key() -> str:
    """Get the current admin API key."""
    return ADMIN_API_KEY
