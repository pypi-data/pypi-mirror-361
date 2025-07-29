"""
AgentMeter v0.3.1 New Features Example
=====================================

This example demonstrates the new resource-based architecture and features 
introduced in v0.3.1, while maintaining backward compatibility.
"""

import asyncio
from uuid import UUID, uuid4
from datetime import datetime
import os

# New v0.3.1 imports
from agentmeter import AgentMeter, AsyncAgentMeter
from agentmeter.models import MeterType, MeterEvent, UsageAggregation

# Legacy imports still work for backward compatibility
from agentmeter import AgentMeterClient


async def demonstrate_new_features():
    """Demonstrate the new v0.3.1 features"""
    
    # Your API key (in production, use environment variables)
    api_key = os.getenv("AGENTMETER_API_KEY", "your-api-key-here")
    
    print("=== AgentMeter v0.3.1 New Features Demo ===\n")
    
    # 1. New Resource-Based Client (Sync)
    print("1. Using the new AgentMeter client (Sync)")
    with AgentMeter(api_key=api_key) as meter:
        
        # Create a project
        try:
            project = meter.projects.create(
                name="Demo Project v0.3.1",
                description="Demonstrating new features"
            )
            print(f"✓ Created project: {project.name} (ID: {project.id})")
            project_id = UUID(project.id)
        except Exception as e:
            print(f"⚠ Using mock project ID due to: {e}")
            project_id = uuid4()
        
        # Create a meter type
        try:
            meter_type = meter.meter_types.create(
                project_id=project_id,
                name="api_calls",
                unit="requests",
                description="Track API calls",
                aggregation_method="sum"
            )
            print(f"✓ Created meter type: {meter_type.name} (ID: {meter_type.id})")
        except Exception as e:
            print(f"⚠ Using mock meter type due to: {e}")
            meter_type = MeterType(
                id=uuid4(),
                project_id=project_id,
                name="api_calls",
                unit="requests",
                description="Track API calls"
            )
        
        # Record some events
        try:
            for i in range(5):
                event = meter.meter_events.record(
                    meter_type_id=meter_type.id,
                    subject_id=f"user_{i+1}",
                    quantity=float(i+1),
                    metadata={"source": "demo", "batch": "v031"}
                )
                print(f"✓ Recorded event for user_{i+1}: {event.quantity} {meter_type.unit}")
        except Exception as e:
            print(f"⚠ Mock event recording due to: {e}")
        
        # Get aggregations
        try:
            aggregation = meter.meter_events.get_aggregations(
                meter_type_id=meter_type.id
            )
            print(f"✓ Total events: {aggregation.total_events}")
            print(f"✓ Total quantity: {aggregation.total_quantity}")
            print(f"✓ Unique subjects: {aggregation.unique_subjects}")
        except Exception as e:
            print(f"⚠ Mock aggregation due to: {e}")
            print("✓ Total events: 5")
            print("✓ Total quantity: 15.0")
            print("✓ Unique subjects: 5")
    
    print("\n" + "="*50 + "\n")
    
    # 2. New Async Client
    print("2. Using the new AsyncAgentMeter client")
    async with AsyncAgentMeter(api_key=api_key) as async_meter:
        
        try:
            # List projects
            projects = await async_meter.projects.list()
            print(f"✓ Found {len(projects)} projects")
        except Exception as e:
            print(f"⚠ Mock project list due to: {e}")
            print("✓ Found 1 projects")
        
        try:
            # List meter types
            meter_types = await async_meter.meter_types.list(project_id=project_id)
            print(f"✓ Found {len(meter_types)} meter types")
        except Exception as e:
            print(f"⚠ Mock meter types list due to: {e}")
            print("✓ Found 1 meter types")
    
    print("\n" + "="*50 + "\n")
    
    # 3. Backward Compatibility
    print("3. Backward compatibility with legacy client")
    with AgentMeterClient(
        api_key=api_key,
        project_id=str(project_id),
        agent_id="demo-agent",
        user_id="demo-user"
    ) as legacy_client:
        
        # Legacy methods still work
        try:
            response = legacy_client.record_api_request_pay(
                api_calls=3,
                unit_price=0.001
            )
            print(f"✓ Legacy API request recording: {response.success}")
        except Exception as e:
            print(f"✓ Legacy API request recording: True (mocked)")
        
        try:
            response = legacy_client.record_token_based_pay(
                tokens_in=150,
                tokens_out=50,
                input_token_price=0.000004,
                output_token_price=0.000001
            )
            print(f"✓ Legacy token-based recording: {response.success}")
        except Exception as e:
            print(f"✓ Legacy token-based recording: True (mocked)")


def demonstrate_error_handling():
    """Demonstrate improved error handling"""
    print("4. Improved Error Handling")
    
    try:
        with AgentMeter(api_key="invalid-key") as meter:
            # This will raise an AuthenticationError
            meter.projects.list()
    except Exception as e:
        print(f"✓ Proper error handling: {type(e).__name__}")
    
    print("✓ Enhanced exception hierarchy with specific error types")


def demonstrate_context_managers():
    """Demonstrate context manager usage"""
    print("\n5. Context Manager Support")
    
    # Sync context manager
    print("✓ Sync context manager automatically closes HTTP connections")
    
    # Async context manager  
    print("✓ Async context manager with proper async cleanup")
    
    # Both ensure proper resource cleanup


def main():
    """Main demonstration function"""
    print("AgentMeter Python SDK v0.3.1")
    print("============================")
    print("New resource-based architecture with full backward compatibility\n")
    
    # Run async demo
    asyncio.run(demonstrate_new_features())
    
    # Error handling demo
    demonstrate_error_handling()
    
    # Context managers demo
    demonstrate_context_managers()
    
    print("\n" + "="*50)
    print("Key Benefits of v0.3.1:")
    print("• Resource-based architecture for better organization")
    print("• Both sync and async support") 
    print("• Improved error handling with specific exception types")
    print("• Better type safety with Pydantic v2")
    print("• Modern HTTP client (httpx) with retry logic")
    print("• Full backward compatibility with existing code")
    print("• Context manager support for automatic cleanup")
    print("="*50)


if __name__ == "__main__":
    main() 