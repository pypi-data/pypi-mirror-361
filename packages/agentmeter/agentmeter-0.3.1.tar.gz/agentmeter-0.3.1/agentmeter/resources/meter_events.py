"""
Meter events resource manager
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import httpx
from ..models import MeterEvent, MeterEventCreate, UsageAggregation
from ..exceptions import AgentMeterError
from ..utils.retry import with_retry


class MeterEvents:
    """Meter events resource manager."""
    
    def __init__(self, client: httpx.Client):
        self._client = client
    
    @with_retry()
    def record(
        self,
        meter_type_id: UUID,
        subject_id: str,
        quantity: float,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MeterEvent:
        """Record a meter event."""
        event_data = MeterEventCreate(
            meter_type_id=meter_type_id,
            subject_id=subject_id,
            quantity=quantity,
            timestamp=timestamp,
            event_metadata=metadata or {}
        )
        
        response = self._client.post(
            "/api/v1/meter-events/",
            json=event_data.model_dump(exclude_none=True)
        )
        
        if response.status_code != 201:
            raise AgentMeterError.from_response(response)
        
        return MeterEvent(**response.json())
    
    @with_retry()
    def list(
        self,
        meter_type_id: Optional[UUID] = None,
        subject_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[MeterEvent]:
        """List meter events with filtering."""
        params = {"limit": limit}
        if meter_type_id:
            params["meter_type_id"] = str(meter_type_id)
        if subject_id:
            params["subject_id"] = subject_id
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        
        response = self._client.get("/api/v1/meter-events/", params=params)
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return [MeterEvent(**event) for event in response.json()]
    
    @with_retry()
    def get_aggregations(
        self,
        meter_type_id: Optional[UUID] = None,
        subject_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> UsageAggregation:
        """Get usage aggregations."""
        params = {}
        if meter_type_id:
            params["meter_type_id"] = str(meter_type_id)
        if subject_id:
            params["subject_id"] = subject_id
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        
        response = self._client.get("/api/v1/meter-events/aggregates", params=params)
        
        if response.status_code != 200:
            raise AgentMeterError.from_response(response)
        
        return UsageAggregation(**response.json()) 