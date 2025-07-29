"""
AgentMeter Python SDK - Usage tracking and billing for agent applications

Version 0.3.1 introduces a new resource-based architecture while maintaining
backward compatibility with existing code.
"""

from .client import AgentMeter, AsyncAgentMeter, AgentMeterClient
from .tracker import (
    AgentMeterTracker, track_usage, track_api_request_pay, 
    track_token_based_pay, track_instant_pay
)
from .decorators import (
    meter_function, meter_agent, meter_api_request_pay, 
    meter_token_based_pay, meter_instant_pay
)
from .langchain_integration import LangChainAgentMeterCallback
from .models import (
    # New v0.3.1 models
    MeterType, MeterEvent, MeterEventCreate, UsageAggregation,
    # Legacy models for backward compatibility
    EventType, PaymentType, MeterEventLegacy, APIRequestPayEvent, 
    TokenBasedPayEvent, InstantPayEvent, MeterEventResponse, MeterEventsResponse,
    AgentMeterConfig, Project, UserMeter, MeterStats, BillingRecord
)
from .exceptions import (
    AgentMeterError, AuthenticationError, AuthorizationError, NotFoundError,
    ValidationError, ServerError,
    # Legacy aliases
    RateLimitError, AgentMeterAPIError, AgentMeterValidationError
)

__version__ = "0.3.1"
__author__ = "AgentMeter Team"

# Convenience functions for easy integration
def create_client(
    api_key: str,
    project_id: str = None,
    agent_id: str = None,
    user_id: str = "anonymous",
    base_url: str = "https://api.agentmeter.money"
) -> AgentMeterClient:
    """
    Create a pre-configured AgentMeter client
    
    Args:
        api_key: Your project's secret key
        project_id: Project identifier
        agent_id: Agent identifier
        user_id: User identifier (default: "anonymous")
        base_url: API base URL (default: staging)
    
    Returns:
        Configured AgentMeterClient instance
    """
    return AgentMeterClient(
        api_key=api_key,
        project_id=project_id,
        agent_id=agent_id,
        user_id=user_id,
        base_url=base_url
    )

# Quick start functions for different payment types
def quick_api_request_pay(
    client: AgentMeterClient,
    project_id: str,
    agent_id: str,
    user_id: str = None,
    api_calls: int = 1,
    unit_price: float = 0.001
):
    """Quick API request payment recording"""
    return client.record_api_request_pay(
        api_calls=api_calls, 
        unit_price=unit_price,
        project_id=project_id,
        agent_id=agent_id,
        user_id=user_id
    )

def quick_token_based_pay(
    client: AgentMeterClient,
    project_id: str,
    agent_id: str,
    user_id: str = None,
    tokens_in: int = 0,
    tokens_out: int = 0,
    input_token_price: float = 0.000004,
    output_token_price: float = 0.000001
):
    """Quick token-based payment recording"""
    return client.record_token_based_pay(
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        input_token_price=input_token_price,
        output_token_price=output_token_price,
        project_id=project_id,
        agent_id=agent_id,
        user_id=user_id
    )

def quick_instant_pay(
    client: AgentMeterClient,
    project_id: str,
    agent_id: str,
    user_id: str = None,
    amount: float = 0.0,
    description: str = "Instant payment"
):
    """Quick instant payment recording"""
    return client.record_instant_pay(
        amount=amount, 
        description=description,
        project_id=project_id,
        agent_id=agent_id,
        user_id=user_id
    )

# Export main classes and functions for easy access
__all__ = [
    # Main clients (v0.3.1)
    'AgentMeter',
    'AsyncAgentMeter',
    
    # Legacy client (backward compatibility)
    'AgentMeterClient',
    'create_client',
    
    # Tracking (legacy)
    'AgentMeterTracker',
    'track_usage',
    'track_api_request_pay',
    'track_token_based_pay', 
    'track_instant_pay',
    
    # Decorators (legacy)
    'meter_function',
    'meter_agent',
    'meter_api_request_pay',
    'meter_token_based_pay',
    'meter_instant_pay',
    
    # New v0.3.1 models
    'MeterType',
    'MeterEvent',
    'MeterEventCreate',
    'UsageAggregation',
    
    # Legacy models
    'EventType',
    'PaymentType',
    'MeterEventLegacy',
    'APIRequestPayEvent',
    'TokenBasedPayEvent',
    'InstantPayEvent',
    'MeterEventResponse',
    'MeterEventsResponse',
    'AgentMeterConfig',
    'Project',
    'UserMeter',
    'MeterStats',
    'BillingRecord',
    
    # Integrations
    'LangChainAgentMeterCallback',
    
    # Exceptions
    'AgentMeterError',
    'AuthenticationError',
    'AuthorizationError',
    'NotFoundError',
    'ValidationError',
    'ServerError',
    'RateLimitError',
    'AgentMeterAPIError',
    'AgentMeterValidationError',
    
    # Quick functions (legacy)
    'quick_api_request_pay',
    'quick_token_based_pay',
    'quick_instant_pay'
]
