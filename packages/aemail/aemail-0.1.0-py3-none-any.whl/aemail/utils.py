"""
Utility functions for the email server.
"""

import re
from typing import List, Optional


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def extract_domain(email: str) -> Optional[str]:
    """
    Extract domain from email address.
    
    Args:
        email: Email address
        
    Returns:
        Domain part of email or None if invalid
    """
    if not validate_email(email):
        return None
    
    return email.split('@')[1].lower()


def normalize_email(email: str) -> str:
    """
    Normalize email address (lowercase, strip whitespace).
    
    Args:
        email: Email address to normalize
        
    Returns:
        Normalized email address
    """
    if not email:
        return ""
    
    return email.strip().lower()


def filter_valid_emails(emails: List[str]) -> List[str]:
    """
    Filter list to only include valid email addresses.
    
    Args:
        emails: List of email addresses
        
    Returns:
        List of valid email addresses
    """
    return [email for email in emails if validate_email(email)]


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        return "unnamed"
    
    return sanitized
