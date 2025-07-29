"""
Meter types resource manager
"""

from typing import List, Optional
from uuid import UUID
import httpx
from ..models import MeterType
from ..exceptions import AgentMeterError
from ..utils.retry import with_retry


class MeterTypes:
    """Meter types resource manager."""
    
    def __init__(self, client: httpx.Client):
        self._client = client
    
    @with_retry()
    def create(
        self,
        name: str,
        project_id: Optional[UUID] = None,
        unit: Optional[str] = None,
        description: Optional[str] = None,
        aggregation_method: str = "sum"
    ) -> MeterType:
        """Create a new meter type."""
        data = {
            "name": name,
            "aggregation_method": aggregation_method
        }
        
        if project_id:
            data["project_id"] = str(project_id)
        if unit:
            data["unit"] = unit
        if description:
            data["description"] = description
        
        response = self._client.post("/api/v1/meter-types/", json=data)
        
        if response.status_code != 201:
            raise AgentMeterError.from_response(response)
        
        return MeterType(**response.json())
    
    @with_retry()
    def get(self, meter_type_id: UUID) -> MeterType:
        """Get a meter type by ID."""
        response = self._client.get(f"/api/v1/meter-types/{meter_type_id}")
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return MeterType(**response.json())
    
    @with_retry()
    def list(self, project_id: Optional[UUID] = None) -> List[MeterType]:
        """List meter types."""
        params = {}
        if project_id:
            params["project_id"] = str(project_id)
        
        response = self._client.get("/api/v1/meter-types/", params=params)
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return [MeterType(**meter_type) for meter_type in response.json()]
    
    @with_retry()
    def update(
        self,
        meter_type_id: UUID,
        name: Optional[str] = None,
        unit: Optional[str] = None,
        description: Optional[str] = None,
        aggregation_method: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> MeterType:
        """Update a meter type."""
        data = {}
        if name is not None:
            data["name"] = name
        if unit is not None:
            data["unit"] = unit
        if description is not None:
            data["description"] = description
        if aggregation_method is not None:
            data["aggregation_method"] = aggregation_method
        if is_active is not None:
            data["is_active"] = is_active
        
        response = self._client.patch(f"/api/v1/meter-types/{meter_type_id}", json=data)
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return MeterType(**response.json())
    
    @with_retry()
    def delete(self, meter_type_id: UUID) -> bool:
        """Delete a meter type."""
        response = self._client.delete(f"/api/v1/meter-types/{meter_type_id}")
        
        if response.status_code not in [200, 204]:
            raise AgentMeterError.from_response(response)
        
        return True 