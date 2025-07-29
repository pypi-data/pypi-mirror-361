"""
Data models for AgentMeter SDK
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List, Literal, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID, uuid4
import httpx  # For backward compatibility with tests


# New models for v0.3.1
class MeterType(BaseModel):
    """Meter type model."""
    id: Optional[Union[UUID, str]] = None
    project_id: Optional[Union[UUID, str]] = None  # Optional for backward compatibility
    name: str
    unit: Optional[str] = None  # Optional for backward compatibility
    description: Optional[str] = None
    aggregation_method: str = "sum"
    is_active: bool = True
    created_at: Optional[str] = None  # Keep as string for backward compatibility
    updated_at: Optional[str] = None  # Keep as string for backward compatibility
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Meter type name cannot be empty")
        return v
    
    # Pydantic v1 backward compatibility methods
    def dict(self, **kwargs) -> Dict[str, Any]:
        """Backward compatibility for Pydantic v1 dict() method"""
        return self.model_dump(**kwargs)
    
    def json(self, **kwargs) -> str:
        """Backward compatibility for Pydantic v1 json() method"""
        return self.model_dump_json(**kwargs)
    
    @classmethod
    def parse_raw(cls, data: Union[str, bytes], **kwargs):
        """Backward compatibility for Pydantic v1 parse_raw() method"""
        if isinstance(data, bytes):
            data = data.decode()
        return cls.model_validate_json(data, **kwargs)


class MeterEvent(BaseModel):
    """Meter event model."""
    id: Optional[Union[UUID, str]] = None
    meter_type_id: Union[UUID, str]
    subject_id: str
    quantity: float
    timestamp: Optional[str] = None  # Keep as string for backward compatibility
    received_at: Optional[str] = None  # Keep as string for backward compatibility
    event_metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        # Handle backward compatibility field mappings
        if 'metadata' in data and 'event_metadata' not in data:
            data['event_metadata'] = data.pop('metadata')
        if 'created_at' in data and 'timestamp' not in data:
            data['timestamp'] = data.pop('created_at')
        super().__init__(**data)
    
    # Backward compatibility properties
    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """Backward compatibility alias for event_metadata"""
        return self.event_metadata
    
    @metadata.setter 
    def metadata(self, value: Optional[Dict[str, Any]]):
        """Backward compatibility setter for event_metadata"""
        self.event_metadata = value
    
    # Support for created_at in tests
    @property
    def created_at(self) -> Optional[str]:
        """Backward compatibility alias for timestamp"""
        return self.timestamp
    
    @created_at.setter
    def created_at(self, value: Optional[str]):
        """Backward compatibility setter for timestamp"""
        self.timestamp = value
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v
    
    # Pydantic v1 backward compatibility methods
    def dict(self, **kwargs) -> Dict[str, Any]:
        """Backward compatibility for Pydantic v1 dict() method"""
        data = self.model_dump(**kwargs)
        # Map internal field names to backward-compatible names
        if 'event_metadata' in data:
            data['metadata'] = data.pop('event_metadata')
        if 'timestamp' in data:
            data['created_at'] = data['timestamp']  # Keep both for compatibility
        return data
    
    def json(self, **kwargs) -> str:
        """Backward compatibility for Pydantic v1 json() method"""
        return self.model_dump_json(**kwargs)
    
    @classmethod
    def parse_raw(cls, data: Union[str, bytes], **kwargs):
        """Backward compatibility for Pydantic v1 parse_raw() method"""
        if isinstance(data, bytes):
            data = data.decode()
        return cls.model_validate_json(data, **kwargs)


class MeterEventCreate(BaseModel):
    """Model for creating meter events."""
    meter_type_id: Union[UUID, str]
    subject_id: str
    quantity: float
    timestamp: Optional[str] = None  # Keep as string for backward compatibility
    event_metadata: Optional[Dict[str, Any]] = None  # Default to None for backward compatibility
    
    def __init__(self, **data):
        # Handle backward compatibility field mappings
        if 'metadata' in data and 'event_metadata' not in data:
            data['event_metadata'] = data.pop('metadata')
        super().__init__(**data)
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v
    
    @field_validator('meter_type_id')
    @classmethod
    def validate_meter_type_id(cls, v):
        if isinstance(v, str) and len(v.strip()) == 0:
            raise ValueError("Meter type ID cannot be empty")
        return v
    
    @field_validator('subject_id')
    @classmethod
    def validate_subject_id(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Subject ID cannot be empty")
        return v
    
    # Backward compatibility properties
    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """Backward compatibility alias for event_metadata"""
        return self.event_metadata
    
    @metadata.setter 
    def metadata(self, value: Optional[Dict[str, Any]]):
        """Backward compatibility setter for event_metadata"""
        self.event_metadata = value


class UsageAggregation(BaseModel):
    """Usage aggregation result."""
    meter_type_id: Optional[Union[UUID, str]] = None  # For compatibility with tests
    subject_id: Optional[str] = None  # For backward compatibility
    total_quantity: float
    total_events: int
    unique_subjects: Optional[int] = None  # Optional for backward compatibility
    first_event: Optional[str] = None  # Keep as string for backward compatibility
    last_event: Optional[str] = None  # Keep as string for backward compatibility
    period_start: Optional[str] = None  # For backward compatibility
    period_end: Optional[str] = None  # For backward compatibility
    
    def __init__(self, **data):
        # Handle backward compatibility field mappings
        if 'event_count' in data and 'total_events' not in data:
            data['total_events'] = data.pop('event_count')
        super().__init__(**data)
    
    @field_validator('total_quantity')
    @classmethod
    def validate_total_quantity(cls, v):
        if v < 0:
            raise ValueError("Total quantity cannot be negative")
        return v
    
    @field_validator('total_events')
    @classmethod
    def validate_total_events(cls, v):
        if v < 0:
            raise ValueError("Event count cannot be negative")
        return v
    
    # Backward compatibility properties
    @property
    def event_count(self) -> int:
        """Backward compatibility alias for total_events"""
        return self.total_events
    
    @event_count.setter
    def event_count(self, value: int):
        """Backward compatibility setter for total_events"""
        self.total_events = value
    
    # Pydantic v1 backward compatibility methods
    def dict(self, **kwargs) -> Dict[str, Any]:
        """Backward compatibility for Pydantic v1 dict() method"""
        return self.model_dump(**kwargs)
    
    def json(self, **kwargs) -> str:
        """Backward compatibility for Pydantic v1 json() method"""
        return self.model_dump_json(**kwargs)
    
    @classmethod
    def parse_raw(cls, data: Union[str, bytes], **kwargs):
        """Backward compatibility for Pydantic v1 parse_raw() method"""
        if isinstance(data, bytes):
            data = data.decode()
        return cls.model_validate_json(data, **kwargs)


# Backwards compatibility models
class PaymentType(str, Enum):
    """Payment types supported by AgentMeter"""
    API_REQUEST_PAY = "api_request_pay"
    TOKEN_BASED_PAY = "token_based_pay"
    INSTANT_PAY = "instant_pay"


class EventType(str, Enum):
    """Event types for backwards compatibility"""
    API_CALL = "api_call"
    TOKEN_USAGE = "token_usage"
    INSTANT_PAYMENT = "instant_payment"


class MeterEventLegacy(BaseModel):
    """Legacy base model for all metering events"""
    model_config = ConfigDict(extra='allow')  # Allow extra fields for backward compatibility
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    agent_id: str
    user_id: str
    total_cost: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    payment_type: Optional[str] = None  # Added for backward compatibility
    
    @field_validator('total_cost')
    @classmethod
    def validate_cost(cls, v):
        if v < 0:
            raise ValueError("Cost cannot be negative")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = self.model_dump()
        result['timestamp'] = self.timestamp.isoformat()
        
        # Convert enum values to strings
        for key, value in result.items():
            if hasattr(value, 'value'):  # Check if it's an enum
                result[key] = value.value
                
        return result


class APIRequestPayEvent(MeterEventLegacy):
    """Event for API request-based payments"""
    event_type: Literal[EventType.API_CALL] = EventType.API_CALL
    payment_type: Literal[PaymentType.API_REQUEST_PAY] = PaymentType.API_REQUEST_PAY
    api_calls: int = 1
    unit_price: float
    
    def __init__(self, **data):
        super().__init__(**data)
        self.payment_type = PaymentType.API_REQUEST_PAY
    
    @field_validator('api_calls')
    @classmethod
    def validate_api_calls(cls, v):
        if v < 0:
            raise ValueError("API calls cannot be negative")
        return v
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIRequestPayEvent':
        """Create instance from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        return cls(**data)


class TokenBasedPayEvent(MeterEventLegacy):
    """Event for token-based payments"""
    event_type: Literal[EventType.TOKEN_USAGE] = EventType.TOKEN_USAGE
    payment_type: Literal[PaymentType.TOKEN_BASED_PAY] = PaymentType.TOKEN_BASED_PAY
    tokens_in: int = 0
    tokens_out: int = 0
    input_token_price: float
    output_token_price: float
    
    def __init__(self, **data):
        super().__init__(**data)
        self.payment_type = PaymentType.TOKEN_BASED_PAY
    
    @field_validator('tokens_in', 'tokens_out')
    @classmethod
    def validate_tokens(cls, v):
        if v < 0:
            raise ValueError("Token count cannot be negative")
        return v
    
    @property
    def total_tokens(self) -> int:
        """Total tokens used"""
        return self.tokens_in + self.tokens_out
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenBasedPayEvent':
        """Create instance from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        return cls(**data)


class InstantPayEvent(MeterEventLegacy):
    """Event for instant payments"""
    event_type: Literal[EventType.INSTANT_PAYMENT] = EventType.INSTANT_PAYMENT
    payment_type: Literal[PaymentType.INSTANT_PAY] = PaymentType.INSTANT_PAY
    amount: float
    description: str
    
    def __init__(self, **data):
        super().__init__(**data)
        self.payment_type = PaymentType.INSTANT_PAY
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InstantPayEvent':
        """Create instance from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        return cls(**data)


class MeterEventResponse(BaseModel):
    """Response model for meter event operations"""
    success: bool = True
    event_id: str
    cost: float = 0.0
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeterEventResponse':
        """Create instance from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        return cls(**data)


class MeterEventsResponse(BaseModel):
    """Response model for multiple meter events"""
    events: List[Dict[str, Any]] = Field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 50
    has_more: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeterEventsResponse':
        """Create instance from dictionary"""
        return cls(**data)


class UserMeter(BaseModel):
    """User subscription meter for tracking usage limits"""
    project_id: str
    user_id: str
    threshold_amount: float
    current_usage: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    last_reset_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def remaining_budget(self) -> float:
        """Remaining budget amount"""
        return max(0, self.threshold_amount - self.current_usage)
    
    @property
    def usage_percentage(self) -> float:
        """Usage as percentage of threshold"""
        if self.threshold_amount <= 0:
            return 0.0
        return min(100.0, (self.current_usage / self.threshold_amount) * 100)
    
    @property
    def is_over_limit(self) -> bool:
        """Check if usage exceeds threshold"""
        return self.current_usage >= self.threshold_amount
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserMeter':
        """Create instance from dictionary"""
        for field in ['created_at', 'last_reset_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        return cls(**data)


class MeterStats(BaseModel):
    """Usage statistics for a project/agent/user"""
    total_api_calls: int = 0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_cost: float = 0.0
    timeframe: str = "30 days"
    
    @property
    def total_tokens(self) -> int:
        """Total tokens (input + output)"""
        return self.total_tokens_in + self.total_tokens_out
    
    @property
    def average_cost_per_call(self) -> float:
        """Average cost per API call"""
        if self.total_api_calls == 0:
            return 0.0
        return self.total_cost / self.total_api_calls


class Project(BaseModel):
    """Project information"""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create instance from dictionary"""
        for field in ['created_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        return cls(**data)


class BillingRecord(BaseModel):
    """Billing record for a project"""
    id: str
    project_id: str
    period_start: datetime
    period_end: datetime
    amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BillingRecord':
        """Create instance from dictionary"""
        for field in ['period_start', 'period_end', 'created_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        return cls(**data)


class AgentMeterConfig(BaseModel):
    """Configuration for AgentMeter client"""
    api_key: str
    project_id: Optional[str] = None  # Optional for backward compatibility
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    base_url: str = "https://api.agentmeter.money"
    timeout: float = 30.0  # Changed to float for compatibility with tests
    max_retries: int = 3  # Changed from retry_attempts for test compatibility
    batch_size: int = 50
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("API key cannot be empty")
        return v
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v < 0:
            raise ValueError("Timeout cannot be negative")
        return v
    
    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v):
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        return v


# Request models
class ProjectCreateRequest(BaseModel):
    """Request model for creating a project"""
    name: str
    description: Optional[str] = None


class UserMeterSetRequest(BaseModel):
    """Request model for setting user meter threshold"""
    threshold_amount: float
    
    @field_validator('threshold_amount')
    @classmethod
    def validate_threshold(cls, v):
        if v < 0:
            raise ValueError("Threshold amount cannot be negative")
        return v


class UserMeterIncrementRequest(BaseModel):
    """Request model for incrementing user meter usage"""
    amount: float
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class UserMeterResetRequest(BaseModel):
    """Request model for resetting user meter"""
    pass


class BillingRecordCreateRequest(BaseModel):
    """Request model for creating a billing record"""
    project_id: str
    period_start: str  # ISO format date string
    period_end: str    # ISO format date string
    amount: float
    status: str = "pending"
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class BillingRecordUpdateRequest(BaseModel):
    """Request model for updating a billing record"""
    status: Optional[str] = None
    amount: Optional[float] = None
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError("Amount cannot be negative")
        return v