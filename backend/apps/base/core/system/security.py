"""
Security Utilities for Owls E-commerce Platform
================================================
Common security functions for input sanitization, validation, etc.
"""

import re
import html
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def sanitize_html(text: str, allow_basic_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    SECURITY: This function removes or escapes potentially dangerous HTML
    that could be used for cross-site scripting attacks.
    
    Args:
        text: Input text that may contain HTML
        allow_basic_tags: If True, allows basic formatting tags (b, i, u, br)
        
    Returns:
        str: Sanitized text safe for HTML rendering
    """
    if not text:
        return text
    
    try:
        import bleach
        
        if allow_basic_tags:
            # Allow only safe formatting tags
            allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'br', 'p']
            allowed_attrs = {}
        else:
            # Strip all HTML tags
            allowed_tags = []
            allowed_attrs = {}
        
        return bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
        
    except ImportError:
        # Fallback: escape all HTML if bleach not available
        logger.warning("bleach library not installed, using basic HTML escape")
        return html.escape(text)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks.
    
    SECURITY: This function removes potentially dangerous characters
    that could be used for directory traversal or log injection.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Safe filename
    """
    if not filename:
        return 'unnamed'
    
    # Remove path separators and null bytes
    filename = filename.replace('/', '_').replace('\\', '_').replace('\x00', '')
    
    # Remove control characters that could mess up logs
    filename = ''.join(char for char in filename if ord(char) >= 32 or char in '\t')
    
    # Remove or replace dangerous patterns
    dangerous_patterns = [
        (r'\.\.', '_'),           # Parent directory traversal
        (r'^\.', '_'),            # Hidden files (Unix)
        (r'[\x00-\x1f]', ''),     # Control characters
        (r'[<>:"|?*]', '_'),      # Windows invalid chars
        (r'\s+', ' '),            # Multiple spaces to single
    ]
    
    for pattern, replacement in dangerous_patterns:
        filename = re.sub(pattern, replacement, filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        if ext:
            filename = name[:255 - len(ext) - 1] + '.' + ext
        else:
            filename = filename[:255]
    
    return filename.strip() or 'unnamed'


def sanitize_text_field(text: str, max_length: int = None) -> str:
    """
    Sanitize user-provided text field for safe storage and display.
    
    SECURITY: Use this for free-text fields like customer_note, address, etc.
    
    Args:
        text: User input text
        max_length: Optional maximum length
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ''
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters except newlines and tabs
    text = ''.join(
        char for char in text 
        if ord(char) >= 32 or char in '\n\r\t'
    )
    
    # Escape HTML entities to prevent XSS
    text = html.escape(text)
    
    # Normalize whitespace
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
    
    # Trim
    text = text.strip()
    
    # Limit length
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def sanitize_for_logging(text: str, max_length: int = 200) -> str:
    """
    Sanitize text for safe logging.
    
    SECURITY: Prevents log injection attacks where attacker could
    manipulate log files by including newlines or control characters.
    
    Args:
        text: Text to sanitize for logging
        max_length: Maximum length to log
        
    Returns:
        str: Log-safe text
    """
    if not text:
        return ''
    
    # Remove newlines to prevent log injection
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32)
    
    # Truncate
    if len(text) > max_length:
        text = text[:max_length] + '...'
    
    return text


def validate_email_format(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid format
    """
    if not email:
        return False
    
    # Basic email regex (not exhaustive but catches most issues)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging or display.
    
    Args:
        data: Sensitive data to mask (e.g., credit card, phone)
        visible_chars: Number of trailing characters to show
        
    Returns:
        str: Masked data (e.g., "****1234")
    """
    if not data:
        return ''
    
    if len(data) <= visible_chars:
        return '*' * len(data)
    
    return '*' * (len(data) - visible_chars) + data[-visible_chars:]
