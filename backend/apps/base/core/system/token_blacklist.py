"""
Access Token Blacklist for Owls E-commerce Platform
====================================================
Redis-based deny list for immediate access token invalidation.

SECURITY: Standard JWT logout only blacklists refresh tokens. This module
provides an additional layer to immediately invalidate access tokens on logout,
password change, or security events.
"""

import logging
from typing import Optional
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Cache key prefix for blacklisted access tokens
ACCESS_TOKEN_BLACKLIST_PREFIX = 'jwt_access_blacklist:'


def blacklist_access_token(jti: str, ttl_seconds: Optional[int] = None) -> bool:
    """
    Add an access token to the deny list.
    
    SECURITY: This invalidates the access token immediately, preventing
    any further use even if the token is not yet expired.
    
    Args:
        jti: The JWT ID (jti claim) of the access token
        ttl_seconds: Time to keep in blacklist (defaults to ACCESS_TOKEN_LIFETIME)
        
    Returns:
        bool: True if successfully blacklisted
    """
    if not jti:
        return False
    
    if ttl_seconds is None:
        # Default to access token lifetime from settings
        simple_jwt = getattr(settings, 'SIMPLE_JWT', {})
        access_lifetime = simple_jwt.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=30))
        ttl_seconds = int(access_lifetime.total_seconds())
    
    cache_key = f"{ACCESS_TOKEN_BLACKLIST_PREFIX}{jti}"
    
    try:
        cache.set(cache_key, True, timeout=ttl_seconds)
        logger.info(f"Access token blacklisted: {jti[:8]}...")
        return True
    except Exception as e:
        logger.error(f"Failed to blacklist access token: {e}")
        return False


def is_access_token_blacklisted(jti: str) -> bool:
    """
    Check if an access token is in the deny list.
    
    Args:
        jti: The JWT ID (jti claim) of the access token
        
    Returns:
        bool: True if token is blacklisted
    """
    if not jti:
        return False
    
    cache_key = f"{ACCESS_TOKEN_BLACKLIST_PREFIX}{jti}"
    
    try:
        return cache.get(cache_key) is True
    except Exception as e:
        logger.error(f"Failed to check access token blacklist: {e}")
        # Fail-safe: if we can't check, assume not blacklisted
        # to avoid blocking legitimate requests
        return False


def blacklist_all_user_tokens(user_id: int) -> bool:
    """
    Blacklist all access tokens for a user by storing user's invalidation timestamp.
    
    SECURITY: Used when user changes password, logs out of all devices,
    or when a security incident is detected.
    
    Args:
        user_id: The user's ID
        
    Returns:
        bool: True if successfully set
    """
    from django.utils import timezone
    
    cache_key = f"user_tokens_invalid_after:{user_id}"
    
    try:
        # Store the timestamp after which all tokens should be invalid
        cache.set(cache_key, timezone.now().isoformat(), timeout=86400 * 7)  # 7 days
        logger.info(f"All tokens invalidated for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate user tokens: {e}")
        return False


def is_token_issued_before_invalidation(user_id: int, issued_at) -> bool:
    """
    Check if a token was issued before the user's token invalidation timestamp.
    
    Args:
        user_id: The user's ID
        issued_at: The token's iat claim (issued at timestamp)
        
    Returns:
        bool: True if token is invalid (issued before invalidation)
    """
    from django.utils import timezone
    from datetime import datetime
    
    cache_key = f"user_tokens_invalid_after:{user_id}"
    
    try:
        invalidation_time = cache.get(cache_key)
        if not invalidation_time:
            return False  # No invalidation set
        
        # Parse the invalidation timestamp
        if isinstance(invalidation_time, str):
            invalidation_dt = datetime.fromisoformat(invalidation_time)
        else:
            invalidation_dt = invalidation_time
        
        # Convert issued_at to datetime if it's a timestamp
        if isinstance(issued_at, (int, float)):
            issued_dt = datetime.fromtimestamp(issued_at, tz=timezone.utc)
        else:
            issued_dt = issued_at
        
        # Make timezone aware if needed
        if issued_dt.tzinfo is None:
            issued_dt = timezone.make_aware(issued_dt)
        if invalidation_dt.tzinfo is None:
            invalidation_dt = timezone.make_aware(invalidation_dt)
        
        return issued_dt < invalidation_dt
        
    except Exception as e:
        logger.error(f"Failed to check token invalidation: {e}")
        return False


class AccessTokenBlacklistAuthentication:
    """
    Mixin for JWT authentication that checks access token blacklist.
    
    SECURITY: Add this check to your authentication flow to enable
    immediate access token invalidation on logout.
    
    Usage in views.py:
        from apps.base.core.system.token_blacklist import is_access_token_blacklisted
        
        # In your authentication or middleware
        if is_access_token_blacklisted(token_jti):
            raise AuthenticationFailed('Token has been revoked')
    """
    pass
