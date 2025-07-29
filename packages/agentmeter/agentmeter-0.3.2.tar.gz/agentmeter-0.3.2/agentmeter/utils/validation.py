"""
Input validation utilities for AgentMeter SDK
"""

import uuid
from typing import Any


def validate_uuid(value: Any) -> bool:
    """Validate if a value is a valid UUID."""
    if isinstance(value, uuid.UUID):
        return True
    
    if isinstance(value, str):
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False
    
    return False


def validate_positive_number(value: Any) -> bool:
    """Validate if a value is a positive number."""
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def validate_non_empty_string(value: Any) -> bool:
    """Validate if a value is a non-empty string."""
    return isinstance(value, str) and len(value.strip()) > 0 