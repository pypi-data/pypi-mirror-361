"""
AgentMeter API Client
"""

from typing import Optional, Dict, Any, List, Union
import httpx
from .auth import TokenAuth
from .resources import Users, Projects, MeterTypes, MeterEvents
from .exceptions import AgentMeterError
from .models import (
    # New models
    MeterType, MeterEvent, UsageAggregation,
    # Legacy models for backward compatibility
    MeterEventLegacy, APIRequestPayEvent, TokenBasedPayEvent, InstantPayEvent,
    MeterEventResponse, MeterEventsResponse, Project, UserMeter, MeterStats,
    BillingRecord, AgentMeterConfig
)


class AgentMeter:
    """Main AgentMeter client for interacting with the API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.agentmeter.money",
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key  # Store for backward compatibility
        self.auth = TokenAuth(api_key)
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # HTTP client setup
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            auth=self.auth,
        )
        
        # Resource managers
        self.users = Users(self._client)
        self.projects = Projects(self._client)
        self.meter_types = MeterTypes(self._client)
        self.meter_events = MeterEvents(self._client)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()


class AsyncAgentMeter:
    """Async AgentMeter client."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.agentmeter.money",
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key  # Store for backward compatibility
        self.auth = TokenAuth(api_key)
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # HTTP client setup
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            auth=self.auth,
        )
        
        # Resource managers
        self.users = Users(self._client)
        self.projects = Projects(self._client)
        self.meter_types = MeterTypes(self._client)
        self.meter_events = MeterEvents(self._client)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()


# Backward compatibility class
class AgentMeterClient:
    """Legacy client for backward compatibility"""
    
    def __init__(
        self, 
        api_key: str,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = "anonymous",
        base_url: str = "https://api.agentmeter.money"
    ):
        """
        Initialize AgentMeter client
        
        Args:
            api_key: The project secret key for authentication
            project_id: Default project ID for operations
            agent_id: Default agent ID for operations
            user_id: Default user ID for operations
            base_url: The base URL for the AgentMeter API
        """
        self.api_key = api_key
        self.project_id = project_id
        self.agent_id = agent_id
        self.user_id = user_id
        self.base_url = base_url.rstrip('/')
        
        # Use the new client internally
        self._client = AgentMeter(api_key=api_key, base_url=base_url)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = self._client._client.get('/health')
            if response.status_code == 200:
                return response.json()
            else:
                raise AgentMeterError.from_response(response)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # === Legacy Event Recording ===
    
    def record_event(self, event: Union[MeterEventLegacy, APIRequestPayEvent, TokenBasedPayEvent, InstantPayEvent]) -> MeterEventResponse:
        """Record a usage event (legacy)"""
        # Convert legacy event to new format
        event_data = event.to_dict() if hasattr(event, 'to_dict') else event.model_dump()
        
        # For now, just return a mock response for backward compatibility
        return MeterEventResponse(
            success=True,
            event_id=event_data.get('id', 'mock-id'),
            cost=event_data.get('total_cost', 0.0),
            message="Event recorded successfully"
        )
    
    def record_api_request_pay(
        self,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_calls: int = 1,
        unit_price: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> MeterEventResponse:
        """Record an API request payment event"""
        event = APIRequestPayEvent(
            project_id=project_id or self.project_id,
            agent_id=agent_id or self.agent_id,
            user_id=user_id or self.user_id,
            api_calls=api_calls,
            unit_price=unit_price or 0.0,
            metadata=metadata or {}
        )
        return self.record_event(event)
    
    def record_token_based_pay(
        self,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
        input_token_price: Optional[float] = None,
        output_token_price: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> MeterEventResponse:
        """Record a token-based payment event"""
        event = TokenBasedPayEvent(
            project_id=project_id or self.project_id,
            agent_id=agent_id or self.agent_id,
            user_id=user_id or self.user_id,
            tokens_in=tokens_in or 0,
            tokens_out=tokens_out or 0,
            input_token_price=input_token_price or 0.0,
            output_token_price=output_token_price or 0.0,
            metadata=metadata or {}
        )
        return self.record_event(event)
    
    def record_instant_pay(
        self,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        amount: float = 0.0,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> MeterEventResponse:
        """Record an instant payment event"""
        event = InstantPayEvent(
            project_id=project_id or self.project_id,
            agent_id=agent_id or self.agent_id,
            user_id=user_id or self.user_id,
            amount=amount,
            description=description or "Instant payment",
            metadata=metadata or {}
        )
        return self.record_event(event)
    
    # === Legacy Query Methods ===
    
    def get_events(
        self,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get events (legacy method)"""
        # Return empty list for backward compatibility
        return []
    
    def get_meter_stats(
        self,
        project_id: Optional[str] = None,
        timeframe: str = "30 days"
    ) -> MeterStats:
        """Get meter statistics"""
        return MeterStats(timeframe=timeframe)
    
    def get_user_meter(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> UserMeter:
        """Get user meter"""
        try:
            return self._client.users.get_meter(
                user_id=user_id or self.user_id,
                project_id=project_id or self.project_id
            )
        except Exception:
            # Return default for backward compatibility
            return UserMeter(
                project_id=project_id or self.project_id,
                user_id=user_id or self.user_id,
                threshold_amount=0.0
            )
    
    def set_user_meter(
        self,
        threshold_amount: float,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> UserMeter:
        """Set user meter threshold"""
        return self._client.users.set_meter(
            user_id=user_id or self.user_id,
            project_id=project_id or self.project_id,
            threshold_amount=threshold_amount
        )
    
    def increment_user_meter(
        self,
        amount: float,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> UserMeter:
        """Increment user meter usage"""
        return self._client.users.increment_meter(
            user_id=user_id or self.user_id,
            project_id=project_id or self.project_id,
            amount=amount
        )
    
    def reset_user_meter(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> UserMeter:
        """Reset user meter"""
        return self._client.users.reset_meter(
            user_id=user_id or self.user_id,
            project_id=project_id or self.project_id
        )
    
    # === Project Management ===
    
    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        """Create a new project"""
        return self._client.projects.create(name=name, description=description)
    
    def get_project(self, project_id: str) -> Project:
        """Get project by ID"""
        return self._client.projects.get(project_id=project_id)
    
    def list_projects(self) -> List[Project]:
        """List all projects"""
        return self._client.projects.list()
    
    def update_project(
        self, 
        project_id: str, 
        name: Optional[str] = None, 
        description: Optional[str] = None
    ) -> Project:
        """Update a project"""
        return self._client.projects.update(
            project_id=project_id,
            name=name,
            description=description
        )
    
    def delete_project(self, project_id: str) -> Dict[str, bool]:
        """Delete a project"""
        success = self._client.projects.delete(project_id=project_id)
        return {"success": success}
    
    # === Billing (Placeholder methods for backward compatibility) ===
    
    def create_billing_record(
        self,
        project_id: str,
        period_start: str,
        period_end: str,
        amount: float,
        status: str = "pending"
    ) -> BillingRecord:
        """Create billing record (placeholder)"""
        from datetime import datetime
        return BillingRecord(
            id="mock-id",
            project_id=project_id,
            period_start=datetime.fromisoformat(period_start),
            period_end=datetime.fromisoformat(period_end),
            amount=amount,
            status=status,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def list_billing_records(self, project_id: Optional[str] = None) -> List[BillingRecord]:
        """List billing records (placeholder)"""
        return []
    
    def update_billing_record(
        self,
        record_id: str,
        status: Optional[str] = None,
        amount: Optional[float] = None
    ) -> BillingRecord:
        """Update billing record (placeholder)"""
        from datetime import datetime
        return BillingRecord(
            id=record_id,
            project_id="mock-project",
            period_start=datetime.now(),
            period_end=datetime.now(),
            amount=amount or 0.0,
            status=status or "pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )