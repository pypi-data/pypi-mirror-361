![AgentMeter SDK Banner](cover.png)

# AgentMeter Python SDK

A comprehensive Python SDK for integrating AgentMeter usage tracking and billing into your applications. **Supports three payment types: API Request Pay, Token-based Pay, and Instant Pay.**

## 🚀 What's New in v0.3.1

**Brand new resource-based architecture with full backward compatibility!**

### New Features
- ✨ **Resource-Based API**: Clean, organized client with `meter.projects`, `meter.meter_types`, `meter.meter_events`, `meter.users`
- 🔄 **Async/Await Support**: Full async support with `AsyncAgentMeter` for modern applications  
- 🎯 **Better Error Handling**: Specific exception types (`AuthenticationError`, `ValidationError`, etc.)
- 🛡️ **Enhanced Type Safety**: Updated to Pydantic v2 with improved validation
- 🌐 **Production Ready**: Now uses `api.agentmeter.money` production endpoint
- 🔧 **Modern HTTP**: Switched to `httpx` with built-in retry logic and better performance

### Quick Example (New v0.3.1 API)
```python
from agentmeter import AgentMeter

# New resource-based client
with AgentMeter(api_key="your_api_key") as meter:
    # Create and manage meter types
    meter_type = meter.meter_types.create(
        project_id=project_id,
        name="api_calls", 
        unit="requests"
    )
    
    # Record usage events
    event = meter.meter_events.record(
        meter_type_id=meter_type.id,
        subject_id="user_123",
        quantity=1.0
    )
    
    # Get aggregated usage statistics
    stats = meter.meter_events.get_aggregations(
        meter_type_id=meter_type.id
    )
```

### Backward Compatibility
All existing v0.2.0 code continues to work without any changes. See [examples/v031_new_features.py](examples/v031_new_features.py) for a complete guide.

## 🚀 Featured Integration: Coinbase AgentKit

**AgentMeter now officially supports [Coinbase AgentKit](https://github.com/coinbase/agentkit)** - the leading framework for building AI agents that interact with onchain protocols!

```python
from agentmeter.integrations.coinbase import Web3AgentMeter
from cdp import Cdp, Wallet

# Initialize with full Web3 + AgentMeter integration
web3_agent = Web3AgentMeter(
    agentmeter_client=your_client,
    cdp_api_key_name="your_coinbase_key",
    cdp_private_key="your_private_key"
)

# AI-powered trading with automatic billing
@web3_agent.meter_smart_trade(amount=4.99)
async def execute_trade(user_id, asset_from, asset_to, amount):
    return await web3_agent.execute_smart_trade(
        user_id=user_id,
        trade_type="market",
        asset_from=asset_from,
        asset_to=asset_to,
        amount=amount
    )
```

**[🔗 See Complete Coinbase AgentKit Integration Example](examples/coinbase_agentkit_integration.py)**

---

## Table of Contents

- [🚀 Featured Integration: Coinbase AgentKit](#-featured-integration-coinbase-agentkit)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Payment Types](#payment-types)
- [Integration Examples](#integration-examples)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Support](#support)

## Features

🚀 **Coinbase AgentKit Integration**: First-class support for Web3 AI agents  
✅ **Three Payment Models**: API requests, token-based, and instant payments  
✅ **Blockchain-Ready**: Native support for Web3 operations and smart contracts  
✅ **Thread-Safe**: Safe for concurrent usage tracking  
✅ **Context Managers**: Clean resource management with automatic cleanup  
✅ **Decorators**: Easy function-level usage tracking  
✅ **LangChain Integration**: Built-in support for LangChain applications  
✅ **Comprehensive Error Handling**: Robust error handling and retry logic  
✅ **Type Safety**: Full type hints and Pydantic models  

## Payment Types

### 1. API Request Pay
Charge customers based on the number of API calls they make.

```python
# Track API calls
await tracker.track_api_request(user_id="user123", api_calls=1)
```

### 2. Token-based Pay
Charge customers based on input and output tokens consumed by AI models.

```python
# Track token usage
await tracker.track_token_usage(user_id="user123", tokens_in=100, tokens_out=50)
```

### 3. Instant Pay
Charge customers arbitrary amounts immediately for any service.

```python
# Instant payment
await tracker.track_instant_payment(user_id="user123", amount=5.99)
```

## Installation

### Basic Installation

```bash
pip install agentmeter
```

### With Coinbase AgentKit Support

```bash
pip install agentmeter cdp-sdk coinbase-python-sdk
```

### With All Integrations

```bash
pip install agentmeter[all]  # Includes LangChain, Coinbase AgentKit, and more
```

## Quick Start

### Basic Setup

```python
from agentmeter import create_client

# Create client with your credentials
client = create_client(
    api_key="your_api_key",
    project_id="proj_123",
    agent_id="agent_456",
    user_id="user_789"
)
```

### 1. API Request Pay Examples

```python
from agentmeter import meter_api_request_pay, track_api_request_pay

# Method 1: Direct API call
response = client.record_api_request_pay(
    api_calls=1,
    unit_price=0.3,
    metadata={"endpoint": "/api/search"}
)

# Method 2: Decorator
@meter_api_request_pay(client, unit_price=0.3)
def search_api(query):
    return perform_search(query)

result = search_api("python tutorials")

# Method 3: Context manager
with track_api_request_pay(client, project_id, agent_id, unit_price=0.3) as usage:
    # Your API logic here
    usage["api_calls"] = 1
    usage["metadata"]["operation"] = "search"
```

### 2. Token-based Pay Examples

```python
from agentmeter import meter_token_based_pay, track_token_based_pay

# Method 1: Direct API call
response = client.record_token_based_pay(
    tokens_in=1000,
    tokens_out=500,
    input_token_price=0.004,
    output_token_price=0.0001,
    metadata={"model": "gpt-4"}
)

# Method 2: Decorator with token extraction
def extract_tokens(*args, result=None, **kwargs):
    # Extract token counts from your LLM response
    return input_tokens, output_tokens

@meter_token_based_pay(
    client, 
    input_token_price=0.004,
    output_token_price=0.0001,
    tokens_extractor=extract_tokens
)
def llm_call(prompt):
    return model.generate(prompt)

# Method 3: Context manager
with track_token_based_pay(client, project_id, agent_id) as usage:
    # Your LLM logic here
    usage["tokens_in"] = 1000
    usage["tokens_out"] = 500
    usage["metadata"]["model"] = "gpt-4"
```

### 3. Instant Pay Examples

```python
from agentmeter import meter_instant_pay, track_instant_pay

# Method 1: Direct API call
response = client.record_instant_pay(
    amount=4.99,
    description="Premium feature unlock",
    metadata={"feature": "advanced_search"}
)

# Method 2: Conditional decorator
def should_charge(*args, **kwargs):
    return kwargs.get('premium', False)

@meter_instant_pay(
    client,
    amount=4.99,
    description="Premium feature",
    condition_func=should_charge
)
def premium_feature(data, premium=False):
    if premium:
        return advanced_processing(data)
    return basic_processing(data)

# Method 3: Context manager
with track_instant_pay(client, project_id, agent_id) as usage:
    # Your premium feature logic here
    usage["amount"] = 9.99
    usage["metadata"]["feature"] = "ai_analysis"
```

## API Reference

### Core Classes
- `AgentMeterClient` - Main client for API interactions
- `AgentMeterTracker` - Batch tracking with auto-flush
- `AgentMeterConfig` - Configuration management

### Payment Models
- `APIRequestPayEvent` - API request payment events
- `TokenBasedPayEvent` - Token-based payment events  
- `InstantPayEvent` - Instant payment events

### Decorators
- `@meter_api_request_pay` - API request payment decorator
- `@meter_token_based_pay` - Token-based payment decorator
- `@meter_instant_pay` - Instant payment decorator
- `@meter_agent` - Class-level metering decorator

### Context Managers
- `track_api_request_pay()` - API request payment tracking
- `track_token_based_pay()` - Token-based payment tracking
- `track_instant_pay()` - Instant payment tracking

## Integration Examples

### 🌟 Coinbase AgentKit Integration

Build monetized Web3 AI agents with seamless blockchain integration:

```python
from agentmeter import create_client
from examples.coinbase_agentkit_integration import Web3AgentMeter

# Create AgentMeter client
client = create_client(
    api_key="your_api_key",
    project_id="web3_proj",
    agent_id="trading_agent"
)

# Initialize Web3 agent with comprehensive billing
web3_agent = Web3AgentMeter(
    agentmeter_client=client,
    cdp_api_key_name="your_coinbase_key",
    cdp_private_key="your_private_key"
)

# Multi-tier billing for Web3 operations:

# 1. API Request Pay - Blockchain queries ($0.05/call)
balance = web3_agent.get_wallet_balance("user123", "ETH")

# 2. Token-based Pay - AI market analysis ($0.00003/input token)
analysis = web3_agent.analyze_market_conditions("user123", "ETH", "advanced")

# 3. Instant Pay - Premium trading features ($4.99)
trade = web3_agent.execute_smart_trade(
    user_id="user123",
    trade_type="market", 
    asset_from="USDC",
    asset_to="ETH",
    amount=150.0  # Triggers premium billing for large trades
)
```

**[📖 Full Coinbase AgentKit Integration Guide](examples/coinbase_agentkit_integration.py)**

### 🤖 LangChain Integration

Automatically track and bill LLM operations in LangChain applications:

```python
from agentmeter.integrations.langchain import AgentMeterLangChainCallback

# Add AgentMeter callback to LangChain
callback = AgentMeterLangChainCallback(
    client=client,
    project_id="langchain_proj",
    agent_id="llm_agent",
    input_token_price=0.000015,
    output_token_price=0.00002
)

# Automatic token tracking for all LLM calls
llm = ChatOpenAI(callbacks=[callback])
result = llm.predict("Analyze this market data...")
```

**[📖 Full LangChain Integration Guide](examples/langchain_integration_meter.py)**

### 🛒 E-commerce Integration

Monetize AI-powered e-commerce features:

```python
@meter_api_request_pay(client, unit_price=0.05)
def search_products(query, user_id):
    """Product search - $0.05 per search"""
    return perform_ai_search(query)

@meter_token_based_pay(client, tokens_extractor=extract_sentiment_tokens)
def analyze_reviews(product_id, user_id):
    """AI review analysis - charged by token usage"""
    return ai_sentiment_analysis(product_id)

@meter_instant_pay(client, amount=9.99, condition_func=is_premium_feature)
def get_ai_recommendations(user_id, premium=False):
    """Premium AI recommendations - $9.99 instant charge"""
    return generate_premium_recommendations(user_id)
```

**[📖 Full E-commerce Integration Guide](examples/ecommerce_integration.py)**

### User Meter Management

```python
# Set user subscription limits
user_meter = client.set_user_meter(
    threshold_amount=100.0,  # $100 monthly limit
    user_id="user_123"
)

# Check current usage
current_meter = client.get_user_meter(user_id="user_123")
print(f"Usage: ${current_meter.current_usage}/${current_meter.threshold_amount}")

# Manually increment usage
client.increment_user_meter(amount=15.50, user_id="user_123")

# Reset monthly usage
client.reset_user_meter(user_id="user_123")
```

### Project and Billing Management

```python
# Get usage statistics
stats = client.get_meter_stats(timeframe="30 days")
print(f"Total cost: ${stats.total_cost}")
print(f"API calls: {stats.total_api_calls}")
print(f"Tokens: {stats.total_tokens_in + stats.total_tokens_out}")

# List recent events
events = client.get_events(limit=10, user_id="user_123")

# Create billing records
billing_record = client.create_billing_record(
    project_id="proj_123",
    period_start="2024-03-01T00:00:00Z",
    period_end="2024-03-31T23:59:59Z",
    amount=150.00,
    status="pending"
)
```

### Batch Tracking

```python
from agentmeter import AgentMeterTracker

# Create tracker for batched events
tracker = AgentMeterTracker(
    client=client,
    project_id="proj_123",
    agent_id="agent_456",
    auto_flush=True,
    batch_size=10
)

# Track multiple events efficiently
tracker.track_api_request_pay(api_calls=1, unit_price=0.3)
tracker.track_token_based_pay(tokens_in=500, tokens_out=250)
tracker.track_instant_pay(amount=2.99, description="Feature unlock")

# Manually flush if needed
tracker.flush()
```

### E-commerce Integration Example

```python
class EcommerceService:
    def __init__(self, client):
        self.client = client
    
    @meter_api_request_pay(client, unit_price=0.05)
    def search_products(self, query, user_id):
        """Product search - charged per search"""
        return perform_search(query)
    
    @meter_token_based_pay(client, tokens_extractor=extract_review_tokens)
    def analyze_review_sentiment(self, review_text, user_id):
        """AI review analysis - charged by tokens"""
        return ai_analyze_sentiment(review_text)
    
    @meter_instant_pay(client, amount=9.99, condition_func=is_premium_user)
    def get_premium_support(self, issue, user_id, premium=False):
        """Premium support - instant charge"""
        return provide_premium_support(issue)
```

### Class-level Metering

```python
from agentmeter import meter_agent, PaymentType

@meter_agent(
    client, 
    PaymentType.API_REQUEST_PAY, 
    unit_price=0.1,
    methods_to_meter=['search', 'recommend']
)
class SearchAgent:
    def search(self, query):
        """This method will be automatically metered"""
        return perform_search(query)
    
    def recommend(self, user_id):
        """This method will be automatically metered"""
        return get_recommendations(user_id)
    
    def _internal_method(self):
        """Private methods won't be metered"""
        pass
```

## Configuration

### Environment Variables

```bash
export AGENTMETER_API_KEY="your_api_key"
export AGENTMETER_PROJECT_ID="proj_123"
export AGENTMETER_AGENT_ID="agent_456"
```

### Configuration Object

```python
from agentmeter import AgentMeterConfig

config = AgentMeterConfig(
    project_id="proj_123",
    agent_id="agent_456",
    user_id="user_789",
    api_key="your_api_key",
    base_url="https://api.agentmeter.money",
    # Default pricing
    api_request_unit_price=0.001,
    input_token_price=0.000004,
    output_token_price=0.000001
)

client = AgentMeterClient(**config.dict())
```

## Error Handling

```python
from agentmeter import AgentMeterError, AgentMeterAPIError

try:
    response = client.record_api_request_pay(api_calls=1, unit_price=0.3)
except AgentMeterAPIError as e:
    if e.status_code == 401:
        print("Authentication failed - check your API key")
    elif e.status_code == 429:
        print("Rate limited - retry later")
    else:
        print(f"API error: {e}")
except AgentMeterError as e:
    print(f"SDK error: {e}")
```

## Testing

Run the example scripts:

```bash
# 🚀 Coinbase AgentKit integration (Featured)
python examples/coinbase_agentkit_integration.py

# Basic usage examples
python examples/basic_usage_meter.py

# AI/LLM integration examples
python examples/langchain_integration_meter.py
python examples/search_agent_meter.py

# E-commerce integration example
python examples/ecommerce_integration.py

# MCP server integration
python examples/mcp_server_meter.py
```

Run tests:

```bash
pytest tests/
```

## Support

For questions, issues, or support:

- [GitHub Issues](https://github.com/Pagent-Money/agentmeter-sdk-python/issues)
- [Support](mailto:thomas.yu@knn3.xyz)
- [Website](https://agentmeter.money)

## Contact

- 🌐 Website: https://agentmeter.money
- 📧 Email: thomas.yu@knn3.xyz

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.