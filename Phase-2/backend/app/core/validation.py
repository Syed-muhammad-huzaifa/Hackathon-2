"""
Input validation and sanitization utilities.

Provides functions to sanitize and validate user input.
"""
import re
from typing import Optional


def sanitize_string(value: Optional[str], max_length: Optional[int] = None) -> Optional[str]:
    """
    Sanitize string input by trimming whitespace and enforcing length limits.

    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string or None if input is None/empty
    """
    if value is None:
        return None

    # Trim whitespace
    sanitized = value.strip()

    # Return None for empty strings
    if not sanitized:
        return None

    # Enforce max length
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def validate_user_id(user_id: str) -> bool:
    """
    Validate user ID format.

    Args:
        user_id: User identifier to validate

    Returns:
        True if valid, False otherwise
    """
    if not user_id or not isinstance(user_id, str):
        return False

    # User ID should be alphanumeric with hyphens/underscores
    # Length between 1 and 255 characters
    if len(user_id) < 1 or len(user_id) > 255:
        return False

    # Allow alphanumeric, hyphens, underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, user_id))


def sanitize_task_title(title: str) -> str:
    """
    Sanitize task title.

    Args:
        title: Task title to sanitize

    Returns:
        Sanitized title

    Raises:
        ValueError: If title is invalid
    """
    sanitized = sanitize_string(title, max_length=500)

    if not sanitized:
        raise ValueError("Task title cannot be empty")

    return sanitized


def sanitize_task_description(description: Optional[str]) -> Optional[str]:
    """
    Sanitize task description.

    Args:
        description: Task description to sanitize

    Returns:
        Sanitized description or None
    """
    return sanitize_string(description, max_length=10000)
