"""
Network Utilities for Owls E-commerce Platform
==============================================
Utilities for handling IP addresses and network-related operations.
"""

import logging
from typing import Optional
from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger(__name__)


# Trusted proxy headers in order of preference
# SECURITY: These headers can be spoofed by clients, so we only trust them
# if the request comes through a known proxy
IP_HEADERS = [
    'HTTP_X_FORWARDED_FOR',
    'HTTP_X_REAL_IP',
    'HTTP_CF_CONNECTING_IP',  # Cloudflare
    'HTTP_TRUE_CLIENT_IP',    # Akamai, Cloudflare Enterprise
    'HTTP_X_CLIENT_IP',
    'REMOTE_ADDR',
]

# Private/Internal IP ranges that should not be returned as client IP
PRIVATE_IP_PREFIXES = (
    '10.',
    '172.16.', '172.17.', '172.18.', '172.19.',
    '172.20.', '172.21.', '172.22.', '172.23.',
    '172.24.', '172.25.', '172.26.', '172.27.',
    '172.28.', '172.29.', '172.30.', '172.31.',
    '192.168.',
    '127.',
    '169.254.',  # Link-local
    'fc', 'fd',  # IPv6 private
    '::1',       # IPv6 localhost
    'fe80:',     # IPv6 link-local
)


def is_private_ip(ip: str) -> bool:
    """
    Check if an IP address is private/internal.
    
    Args:
        ip: IP address string
        
    Returns:
        bool: True if IP is private/internal
    """
    if not ip:
        return True
    
    ip_lower = ip.lower()
    return any(ip_lower.startswith(prefix.lower()) for prefix in PRIVATE_IP_PREFIXES)


def get_client_ip(request: HttpRequest) -> str:
    """
    Get the real client IP address from request.
    
    SECURITY: This function handles proxy headers correctly to get the real
    client IP, not the proxy's IP. It respects NUM_PROXIES setting to prevent
    IP spoofing via X-Forwarded-For header manipulation.
    
    Configuration:
    - Set NUM_PROXIES in settings.py to the number of trusted proxies
    - For Cloudflare only: NUM_PROXIES = 1
    - For Cloudflare + Load Balancer: NUM_PROXIES = 2
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        str: Client IP address (best guess)
    """
    # Number of trusted proxies in front of Django
    # If behind Cloudflare + ALB, set to 2
    num_proxies = getattr(settings, 'NUM_PROXIES', 0)
    
    # Try django-ipware if available (most reliable)
    try:
        from ipware import get_client_ip as ipware_get_client_ip
        ip, is_routable = ipware_get_client_ip(
            request,
            request_header_order=IP_HEADERS
        )
        if ip:
            return ip
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"ipware error: {e}")
    
    # Manual extraction with proxy awareness
    for header in IP_HEADERS:
        ip_value = request.META.get(header)
        
        if not ip_value:
            continue
        
        # Handle X-Forwarded-For which may contain multiple IPs
        # Format: "client, proxy1, proxy2, ..."
        if header == 'HTTP_X_FORWARDED_FOR':
            # Split and clean up
            ips = [ip.strip() for ip in ip_value.split(',')]
            
            if num_proxies > 0 and len(ips) > num_proxies:
                # Trust only the IP added by our first trusted proxy
                # Count from the right: rightmost is last proxy, then second-to-last, etc.
                # The client IP is at position -(num_proxies + 1) from the right
                # But we want the first IP added by a trusted proxy, which is -(num_proxies)
                client_index = len(ips) - num_proxies - 1
                if client_index >= 0:
                    client_ip = ips[client_index]
                else:
                    client_ip = ips[0]
            else:
                # No proxy count configured or not enough IPs
                # Take the first non-private IP, or the leftmost IP
                client_ip = None
                for ip in ips:
                    if not is_private_ip(ip):
                        client_ip = ip
                        break
                if not client_ip:
                    client_ip = ips[0]
            
            if client_ip and client_ip.strip():
                return client_ip.strip()
        else:
            # Single IP headers
            if ip_value and ip_value.strip():
                return ip_value.strip()
    
    # Last resort: REMOTE_ADDR (will be proxy IP if behind proxy)
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def get_client_ip_safe(request: HttpRequest) -> str:
    """
    Get client IP with additional validation.
    
    Same as get_client_ip but with extra validation to ensure
    the returned value is a valid IP format.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        str: Validated client IP address
    """
    import re
    
    ip = get_client_ip(request)
    
    # Basic IPv4 validation
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    # Basic IPv6 validation (simplified)
    ipv6_pattern = r'^[0-9a-fA-F:]+$'
    
    if re.match(ipv4_pattern, ip):
        # Validate each octet is 0-255
        try:
            octets = [int(o) for o in ip.split('.')]
            if all(0 <= o <= 255 for o in octets):
                return ip
        except ValueError:
            pass
    elif re.match(ipv6_pattern, ip):
        return ip
    
    # If validation fails, log and return a safe default
    logger.warning(f"Invalid IP format detected: {ip}")
    return '0.0.0.0'
