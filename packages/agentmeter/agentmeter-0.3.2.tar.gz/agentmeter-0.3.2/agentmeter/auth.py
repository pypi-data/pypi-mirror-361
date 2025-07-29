"""
Authentication handling for AgentMeter SDK
"""

import httpx
from typing import Optional


class TokenAuth(httpx.Auth):
    """Project access token authentication."""
    
    def __init__(self, token: str):
        self.token = token
    
    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class APIKeyAuth(httpx.Auth):
    """Alternative API key authentication (if implemented)."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def auth_flow(self, request):
        request.headers["X-API-Key"] = self.api_key
        yield request 