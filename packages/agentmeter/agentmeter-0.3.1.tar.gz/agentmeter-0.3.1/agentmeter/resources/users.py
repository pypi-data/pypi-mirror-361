"""
Users resource manager
"""

from typing import Optional
import httpx
from ..models import UserMeter
from ..exceptions import AgentMeterError
from ..utils.retry import with_retry


class Users:
    """Users resource manager."""
    
    def __init__(self, client: httpx.Client):
        self._client = client
    
    @with_retry()
    def get_meter(self, user_id: str, project_id: str) -> UserMeter:
        """Get user meter for a project."""
        response = self._client.get(
            f"/api/v1/users/{user_id}/meter",
            params={"project_id": project_id}
        )
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return UserMeter(**response.json())
    
    @with_retry()
    def set_meter(
        self,
        user_id: str,
        project_id: str,
        threshold_amount: float
    ) -> UserMeter:
        """Set user meter threshold."""
        data = {
            "project_id": project_id,
            "threshold_amount": threshold_amount
        }
        
        response = self._client.put(f"/api/v1/users/{user_id}/meter", json=data)
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return UserMeter(**response.json())
    
    @with_retry()
    def increment_meter(
        self,
        user_id: str,
        project_id: str,
        amount: float
    ) -> UserMeter:
        """Increment user meter usage."""
        data = {
            "project_id": project_id,
            "amount": amount
        }
        
        response = self._client.post(f"/api/v1/users/{user_id}/meter/increment", json=data)
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return UserMeter(**response.json())
    
    @with_retry()
    def reset_meter(self, user_id: str, project_id: str) -> UserMeter:
        """Reset user meter usage."""
        data = {"project_id": project_id}
        
        response = self._client.post(f"/api/v1/users/{user_id}/meter/reset", json=data)
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return UserMeter(**response.json()) 