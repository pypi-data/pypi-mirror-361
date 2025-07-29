 # Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2024-12-19

### Added
- **New Resource-Based Architecture**: Introduced `AgentMeter` and `AsyncAgentMeter` clients with resource managers
  - `meter.projects` - Project management operations
  - `meter.meter_types` - Meter type CRUD operations  
  - `meter.meter_events` - Event recording and querying
  - `meter.users` - User meter management
- **Async Support**: Full async/await support with `AsyncAgentMeter` client
- **New Models**: 
  - `MeterType` - Define different types of meters
  - `MeterEvent` - Individual usage events
  - `MeterEventCreate` - For creating new events
  - `UsageAggregation` - Aggregated usage statistics
- **Enhanced Authentication**: Token-based auth with `TokenAuth` and `APIKeyAuth` classes
- **Improved Error Handling**: Specific exception types (`AuthenticationError`, `ValidationError`, etc.)
- **Retry Logic**: Built-in retry mechanism with exponential backoff and jitter
- **Context Manager Support**: Proper resource cleanup with `with` statements
- **Type Safety**: Enhanced type hints and Pydantic v2 integration

### Changed
- **API Endpoint**: Updated to use `api.agentmeter.money` (production endpoint)
- **HTTP Client**: Switched from `requests` to `httpx` for better async support and features
- **Dependencies**: Updated to Pydantic v2.0+ and httpx 0.24+
- **Error Responses**: Improved error parsing and response handling

### Deprecated
- Legacy `AgentMeterClient` is maintained for backward compatibility but marked as legacy
- Old staging URL endpoints are deprecated in favor of production URLs

### Backward Compatibility
- All existing v0.2.0 code continues to work without changes
- Legacy models and functions are preserved with compatibility aliases
- Existing decorator and tracking functionality remains unchanged
- All examples and integrations work as before

### Migration Guide
```python
# Old way (still works)
from agentmeter import AgentMeterClient
client = AgentMeterClient(api_key="key")

# New way (recommended)
from agentmeter import AgentMeter
with AgentMeter(api_key="key") as meter:
    # Use resource managers
    meter.meter_events.record(...)
    meter.projects.create(...)
```

## [Unreleased]

## [0.1.0] - 2024-01-XX

### Added
- Initial release of AgentMeter Python SDK
- Core `AgentMeterClient` for API interactions
- `AgentMeterTracker` for thread-safe usage tracking
- LangChain integration with `LangChainAgentMeterCallback`
- Decorators for automatic function and agent tracking (`@meter_function`, `@meter_agent`)
- Context managers for manual tracking (`track_usage`, `MeterContext`)
- Comprehensive error handling and retry logic
- Support for multiple event types (API_REQUEST, FUNCTION_CALL, AGENT_EXECUTION, CUSTOM)
- Environment variable configuration support
- Automatic batching and flushing of events
- Token usage estimation utilities
- Complete test suite with pytest
- Examples for basic usage and LangChain integration
- Type hints support (py.typed)

### Features
- **API Integration**: Full support for AgentMeter API endpoints
- **LangChain Compatibility**: Built-in callbacks for LangChain agents and chains
- **Thread Safety**: Safe for use in multi-threaded applications
- **Automatic Tracking**: Decorators and context managers for easy integration
- **Flexible Configuration**: Environment variables and programmatic config
- **Error Handling**: Comprehensive exception handling with retries
- **Token Tracking**: Support for input/output token counting
- **Metadata Support**: Rich metadata collection for debugging and analysis

### Documentation
- Complete README with usage examples
- API reference documentation
- LangChain integration guide
- Configuration options documentation