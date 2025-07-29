"""
Exception handling for AgentMeter SDK
"""

import httpx
from typing import Optional, Dict, Any


class AgentMeterError(Exception):
    """Base exception for AgentMeter SDK."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
    
    @classmethod
    def from_response(cls, response: httpx.Response) -> "AgentMeterError":
        """Create exception from HTTP response."""
        try:
            data = response.json()
            message = data.get("detail", f"HTTP {response.status_code}")
        except:
            message = f"HTTP {response.status_code}: {response.text}"
        
        if response.status_code == 401:
            return AuthenticationError(message, response.status_code, data)
        elif response.status_code == 403:
            return AuthorizationError(message, response.status_code, data)
        elif response.status_code == 404:
            return NotFoundError(message, response.status_code, data)
        elif response.status_code == 422:
            return ValidationError(message, response.status_code, data)
        elif response.status_code >= 500:
            return ServerError(message, response.status_code, data)
        else:
            return cls(message, response.status_code, data)


class AuthenticationError(AgentMeterError):
    """Authentication failed."""
    pass


class AuthorizationError(AgentMeterError):
    """Not authorized for this operation."""
    pass


class NotFoundError(AgentMeterError):
    """Resource not found."""
    pass


class ValidationError(AgentMeterError):
    """Request validation failed."""
    pass


class ServerError(AgentMeterError):
    """Server error."""
    pass


# Backwards compatibility aliases
AgentMeterAPIError = AgentMeterError
RateLimitError = AuthorizationError
AgentMeterValidationError = ValidationError
AgentMeterConfigurationError = AgentMeterError
AgentMeterConnectionError = AgentMeterError