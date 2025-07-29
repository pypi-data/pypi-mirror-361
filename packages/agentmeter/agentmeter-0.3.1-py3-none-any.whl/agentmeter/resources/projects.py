"""
Projects resource manager
"""

from typing import List, Optional
import httpx
from ..models import Project
from ..exceptions import AgentMeterError
from ..utils.retry import with_retry


class Projects:
    """Projects resource manager."""
    
    def __init__(self, client: httpx.Client):
        self._client = client
    
    @with_retry()
    def create(self, name: str, description: Optional[str] = None) -> Project:
        """Create a new project."""
        data = {
            "name": name,
            "description": description
        }
        
        response = self._client.post("/api/v1/projects/", json=data)
        
        if response.status_code != 201:
            raise AgentMeterError.from_response(response)
        
        return Project(**response.json())
    
    @with_retry()
    def get(self, project_id: str) -> Project:
        """Get a project by ID."""
        response = self._client.get(f"/api/v1/projects/{project_id}")
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return Project(**response.json())
    
    @with_retry()
    def list(self) -> List[Project]:
        """List all projects."""
        response = self._client.get("/api/v1/projects/")
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return [Project(**project) for project in response.json()]
    
    @with_retry()
    def update(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Project:
        """Update a project."""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        
        response = self._client.patch(f"/api/v1/projects/{project_id}", json=data)
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return Project(**response.json())
    
    @with_retry()
    def delete(self, project_id: str) -> bool:
        """Delete a project."""
        response = self._client.delete(f"/api/v1/projects/{project_id}")
        
        if response.status_code not in [200, 204]:
            raise AgentMeterError.from_response(response)
        
        return True 