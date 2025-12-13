"""
URL Utility Functions for Owls E-commerce Platform
==================================================
Centralized URL building utilities for email links and other purposes.
"""

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from urllib.parse import urlencode


def build_password_reset_url(user) -> str:
    """
    Build password reset URL for a user.
    
    Args:
        user: User instance
        
    Returns:
        str: Full password reset URL
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    base_url = f"{settings.FRONTEND_URL}/reset-password"
    params = urlencode({'uid': uid, 'token': token})
    
    return f"{base_url}?{params}"


def build_email_verification_url(user, token: str) -> str:
    """
    Build email verification URL for a user.
    
    Args:
        user: User instance
        token: Verification token
        
    Returns:
        str: Full email verification URL
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    base_url = f"{settings.FRONTEND_URL}/verify-email"
    params = urlencode({'uid': uid, 'token': token})
    
    return f"{base_url}?{params}"


def build_order_tracking_url(order_number: str) -> str:
    """
    Build order tracking URL.
    
    Args:
        order_number: Order number
        
    Returns:
        str: Full order tracking URL
    """
    return f"{settings.FRONTEND_URL}/orders/{order_number}/tracking"


def build_product_url(product_slug: str) -> str:
    """
    Build product detail URL.
    
    Args:
        product_slug: Product slug
        
    Returns:
        str: Full product URL
    """
    return f"{settings.FRONTEND_URL}/products/{product_slug}"


def build_vendor_portal_url(path: str = '') -> str:
    """
    Build vendor portal URL.
    
    Args:
        path: Optional path within vendor portal
        
    Returns:
        str: Full vendor portal URL
    """
    base_url = settings.ADMIN_URL.rstrip('/')
    if path:
        return f"{base_url}/{path.lstrip('/')}"
    return base_url


def build_admin_url(path: str = '') -> str:
    """
    Build admin panel URL.
    
    Args:
        path: Optional path within admin panel
        
    Returns:
        str: Full admin URL
    """
    base_url = f"{settings.FRONTEND_URL}/admin"
    if path:
        return f"{base_url}/{path.lstrip('/')}"
    return base_url


def build_unsubscribe_url(user, token: str) -> str:
    """
    Build email unsubscribe URL.
    
    Args:
        user: User instance
        token: Unsubscribe token
        
    Returns:
        str: Full unsubscribe URL
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    base_url = f"{settings.FRONTEND_URL}/unsubscribe"
    params = urlencode({'uid': uid, 'token': token})
    
    return f"{base_url}?{params}"
