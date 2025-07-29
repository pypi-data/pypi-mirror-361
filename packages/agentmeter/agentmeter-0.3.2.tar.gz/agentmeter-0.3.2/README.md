![AgentMeter SDK Banner](cover.png)

# AgentMeter Python SDK v0.3.1

**Modern Python SDK for usage tracking and billing in AI applications.**

[![PyPI version](https://badge.fury.io/py/agentmeter.svg)](https://pypi.org/project/agentmeter/)
[![Python Support](https://img.shields.io/pypi/pyversions/agentmeter.svg)](https://pypi.org/project/agentmeter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎯 **Resource-Based Architecture** - Clean, organized API with dedicated resource managers
- ⚡ **Async/Await Support** - Full async support for modern Python applications
- 🔌 **Rich Integrations** - First-class support for LangChain, Coinbase AgentKit, and more
- 🛡️ **Type Safety** - Built with Pydantic v2 for robust data validation and type hints
- 🌐 **Production Ready** - Enterprise-grade reliability with retry logic and error handling
- 📊 **Flexible Billing** - Support for usage-based, token-based, and instant billing models
- 🔄 **100% Backward Compatible** - All v0.2.0 code continues to work unchanged

## 🚀 Quick Start

### Installation

```bash
pip install agentmeter
```

### Basic Usage

```python
from agentmeter import AgentMeter

# Initialize client
with AgentMeter(api_key="your_api_key") as meter:
    # Create a meter type
    meter_type = meter.meter_types.create(
        name="api_calls",
        unit="requests",
        description="API usage tracking"
    )
    
    # Record usage event
    event = meter.meter_events.record(
        meter_type_id=meter_type.id,
        subject_id="user_123",
        quantity=1.0,
        metadata={"endpoint": "/api/search"}
    )
    
    # Get usage statistics
    stats = meter.meter_events.get_aggregations(
        meter_type_id=meter_type.id,
        subject_id="user_123"
    )
    print(f"Total usage: {stats.total_quantity} {meter_type.unit}")
```

## 🏗️ Core Concepts

### Resource Managers

AgentMeter v0.3.1 organizes functionality into focused resource managers:

```python
meter.projects          # Project management
meter.meter_types       # Meter type definitions  
meter.meter_events      # Usage event recording and querying
meter.users            # User-specific meter management
```

### Async Support

```python
from agentmeter import AsyncAgentMeter

async with AsyncAgentMeter(api_key="your_api_key") as meter:
    # All methods have async equivalents
    meter_type = await meter.meter_types.create(...)
    event = await meter.meter_events.record(...)
    stats = await meter.meter_events.get_aggregations(...)
```

## 🔌 Integrations

### 🚀 Coinbase AgentKit

Build monetized Web3 AI agents:

```python
from agentmeter import AgentMeter

meter = AgentMeter(api_key="your_api_key") 

# Create meter types for different Web3 operations
wallet_queries = meter.meter_types.create(
    name="wallet_queries", 
    unit="queries",
    description="Blockchain wallet queries"
)

trading_operations = meter.meter_types.create(
    name="trading_ops",
    unit="trades", 
    description="Smart contract trading"
)

# Track usage in your AgentKit application
def get_wallet_balance(user_id: str, asset: str):
    # Your Web3 logic here
    balance = wallet.get_balance(asset)
    
    # Record billable event
    meter.meter_events.record(
        meter_type_id=wallet_queries.id,
        subject_id=user_id,
        quantity=1.0,
        metadata={"asset": asset, "operation": "balance_check"}
    )
    
    return balance
```

**[📖 Full Coinbase AgentKit Integration Example](examples/coinbase_agentkit_integration.py)**

### 🤖 LangChain

Automatic LLM usage tracking:

```python
from agentmeter.langchain_integration import LangChainAgentMeterCallback

# Create callback with your meter
callback = LangChainAgentMeterCallback(
    agentmeter_client=meter,
    meter_type_id="llm_usage_meter_id"
)

# Add to any LangChain component
llm = ChatOpenAI(callbacks=[callback])
chain = ConversationChain(llm=llm, callbacks=[callback])

# Usage automatically tracked
result = chain.run("Analyze this data...")
```

**[📖 Full LangChain Integration Example](examples/langchain_integration_meter.py)**

## 💰 Billing Models

### Usage-Based Billing

Perfect for API calls, processing requests, or resource consumption:

```python
# Create usage meter
api_meter = meter.meter_types.create(
    name="api_requests",
    unit="requests"
)

# Record usage
meter.meter_events.record(
    meter_type_id=api_meter.id,
    subject_id="user_123", 
    quantity=1.0
)
```

### Token-Based Billing

Ideal for AI/LLM applications:

```python
# Create token meter
token_meter = meter.meter_types.create(
    name="llm_tokens",
    unit="tokens"
)

# Record token usage
meter.meter_events.record(
    meter_type_id=token_meter.id,
    subject_id="user_123",
    quantity=1500.0,  # Total tokens used
    metadata={
        "input_tokens": 1000,
        "output_tokens": 500,
        "model": "gpt-4"
    }
)
```

### Event-Based Billing

For feature unlocks or one-time charges:

```python
# Create event meter  
feature_meter = meter.meter_types.create(
    name="premium_features",
    unit="unlocks"
)

# Record feature usage
meter.meter_events.record(
    meter_type_id=feature_meter.id,
    subject_id="user_123",
    quantity=1.0,
    metadata={
        "feature": "advanced_analytics",
        "tier": "premium"
    }
)
```

## 📊 Analytics & Reporting

### Usage Aggregations

```python
# Get aggregated usage statistics
stats = meter.meter_events.get_aggregations(
    meter_type_id=meter_type.id,
    subject_id="user_123",
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-01-31T23:59:59Z"
)

print(f"Total usage: {stats.total_quantity}")
print(f"Event count: {stats.total_events}")
print(f"Period: {stats.period_start} to {stats.period_end}")
```

### User Meter Management

```python
# Set user spending limits
user_meter = meter.users.set_meter(
    user_id="user_123",
    threshold_amount=100.0  # $100 monthly limit
)

# Check current usage
current_usage = meter.users.get_meter(user_id="user_123")
print(f"Usage: ${current_usage.current_usage} / ${current_usage.threshold_amount}")

# Reset usage (e.g., monthly reset)
meter.users.reset_meter(user_id="user_123")
```

## 🛠️ Configuration

### Environment Variables

```bash
export AGENTMETER_API_KEY="your_api_key"
export AGENTMETER_BASE_URL="https://api.agentmeter.money"  # Optional
```

### Programmatic Configuration

```python
from agentmeter import AgentMeter

meter = AgentMeter(
    api_key="your_api_key",
    base_url="https://api.agentmeter.money",  # Optional
    timeout=30.0,
    max_retries=3
)
```

## 🔄 Migration from v0.2.0

AgentMeter v0.3.1 maintains 100% backward compatibility. Your existing code continues to work:

```python
# ✅ This still works (legacy API)
from agentmeter import AgentMeterClient
client = AgentMeterClient(api_key="key")
client.record_api_request_pay(api_calls=1, unit_price=0.10)

# ✨ New recommended approach (v0.3.1)
from agentmeter import AgentMeter
with AgentMeter(api_key="key") as meter:
    meter.meter_events.record(meter_type_id="mt_123", subject_id="user", quantity=1.0)
```

For a smooth migration:

1. **Keep existing code working** - No immediate changes required
2. **Gradually adopt new API** - Use v0.3.1 for new features
3. **Migrate when convenient** - Update modules one at a time

**[📖 See complete examples: v0.3.1 vs Legacy](examples/v031_new_features.py)**

## 🔧 Error Handling

```python
from agentmeter import AgentMeter
from agentmeter.exceptions import AuthenticationError, ValidationError, ServerError

try:
    with AgentMeter(api_key="invalid") as meter:
        event = meter.meter_events.record(...)
        
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Data validation failed: {e}")
except ServerError as e:
    print(f"Server error: {e}")
```

## 🧪 Examples & Testing

```bash
# Run the new v0.3.1 examples
python examples/v031_new_features.py
python examples/coinbase_agentkit_integration.py  
python examples/langchain_integration_meter.py
python examples/ecommerce_integration.py

# Run tests
pytest tests/
```

## 📚 Documentation

- **[API Reference](https://docs.agentmeter.money/api)**
- **[Integration Guides](https://docs.agentmeter.money/integrations)**
- **[🗂️ Legacy Documentation (v0.2.0 and earlier)](HISTORICAL_VERSIONS.md)**

## 🤝 Support

- **[GitHub Issues](https://github.com/Pagent-Money/agentmeter-sdk-python/issues)**
- **[Documentation](https://docs.agentmeter.money)**
- **[Email Support](mailto:thomas.yu@knn3.xyz)**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🚀 Ready to get started? Install AgentMeter and start tracking usage in minutes!**

```bash
pip install agentmeter
```