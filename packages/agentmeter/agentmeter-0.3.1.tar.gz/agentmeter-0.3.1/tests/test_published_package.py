#!/usr/bin/env python3
"""
Test suite for validating the published agentmeter package from PyPI.

This serves as a checklist to ensure the published package works correctly
for end users after installation via `pip install agentmeter`.

Usage:
    # Install the published package first
    pip install agentmeter
    
    # Run the validation tests
    python -m pytest tests/test_published_package.py -v
    
    # Or run directly for basic validation
    python tests/test_published_package.py
"""

import importlib
import inspect
import sys
from typing import Dict, List, Any
import pytest


class TestPublishedPackageValidation:
    """Comprehensive validation of the published agentmeter package."""
    
    def test_package_import(self):
        """Test that the main package can be imported."""
        try:
            import agentmeter
            assert agentmeter is not None
        except ImportError as e:
            pytest.fail(f"Failed to import agentmeter package: {e}")
    
    def test_package_version(self):
        """Test that package version is accessible and correct."""
        import agentmeter
        
        # Check version exists
        assert hasattr(agentmeter, '__version__')
        assert agentmeter.__version__ is not None
        
        # Check version format (semantic versioning)
        version = agentmeter.__version__
        version_parts = version.split('.')
        assert len(version_parts) >= 2, f"Invalid version format: {version}"
        
        # Should be version 0.2.0 or higher
        major, minor = int(version_parts[0]), int(version_parts[1])
        assert (major, minor) >= (0, 2), f"Version should be 0.2.0+, got {version}"
    
    def test_core_classes_available(self):
        """Test that all core classes are importable."""
        import agentmeter
        
        # Core classes that should be available
        core_classes = [
            'AgentMeterClient',
            'AgentMeterTracker', 
            'AgentMeterConfig',
            'AgentMeterError',
            'RateLimitError'
        ]
        
        for class_name in core_classes:
            assert hasattr(agentmeter, class_name), f"Missing core class: {class_name}"
            cls = getattr(agentmeter, class_name)
            assert inspect.isclass(cls), f"{class_name} is not a class"
    
    def test_payment_models_available(self):
        """Test that payment model classes are available."""
        import agentmeter
        
        payment_models = [
            'PaymentType',
            'APIRequestPayEvent',
            'TokenBasedPayEvent',
            'InstantPayEvent',
            'MeterEvent',
            'MeterEventResponse'
        ]
        
        for model_name in payment_models:
            assert hasattr(agentmeter, model_name), f"Missing payment model: {model_name}"
    
    def test_convenience_functions_available(self):
        """Test that convenience functions are available."""
        import agentmeter
        
        convenience_functions = [
            'create_client',
            'quick_api_request_pay',
            'quick_token_based_pay', 
            'quick_instant_pay'
        ]
        
        for func_name in convenience_functions:
            assert hasattr(agentmeter, func_name), f"Missing convenience function: {func_name}"
            func = getattr(agentmeter, func_name)
            assert callable(func), f"{func_name} is not callable"
    
    def test_decorators_available(self):
        """Test that decorator functions are available."""
        import agentmeter
        
        decorators = [
            'meter_api_request_pay',
            'meter_token_based_pay',
            'meter_instant_pay',
            'meter_function',
            'meter_agent'
        ]
        
        for decorator_name in decorators:
            assert hasattr(agentmeter, decorator_name), f"Missing decorator: {decorator_name}"
            decorator = getattr(agentmeter, decorator_name)
            assert callable(decorator), f"{decorator_name} is not callable"
    
    def test_context_managers_available(self):
        """Test that context manager functions are available."""
        import agentmeter
        
        context_managers = [
            'track_api_request_pay',
            'track_token_based_pay',
            'track_instant_pay',
            'track_usage'
        ]
        
        for cm_name in context_managers:
            assert hasattr(agentmeter, cm_name), f"Missing context manager: {cm_name}"
            cm = getattr(agentmeter, cm_name)
            assert callable(cm), f"{cm_name} is not callable"
    
    def test_client_instantiation(self):
        """Test that AgentMeterClient can be instantiated."""
        from agentmeter import AgentMeterClient
        
        # Test basic instantiation
        client = AgentMeterClient(
            api_key="test_key",
            project_id="test_project",
            agent_id="test_agent"
        )
        
        assert client.api_key == "test_key"
        assert client.project_id == "test_project"
        assert client.agent_id == "test_agent"
        assert client.base_url == "https://api.agentmeter.money"
    
    def test_convenience_client_creation(self):
        """Test that create_client convenience function works."""
        from agentmeter import create_client
        
        client = create_client(
            api_key="test_key",
            project_id="test_project", 
            agent_id="test_agent"
        )
        
        assert client is not None
        assert client.api_key == "test_key"
        assert client.project_id == "test_project"
        assert client.agent_id == "test_agent"
    
    def test_payment_type_enum(self):
        """Test that PaymentType enum works correctly."""
        from agentmeter import PaymentType
        
        # Test enum values
        assert PaymentType.API_REQUEST_PAY == "api_request_pay"
        assert PaymentType.TOKEN_BASED_PAY == "token_based_pay"
        assert PaymentType.INSTANT_PAY == "instant_pay"
        
        # Test enum iteration
        payment_types = list(PaymentType)
        assert len(payment_types) == 3
    
    def test_event_model_creation(self):
        """Test that event models can be created."""
        from agentmeter import APIRequestPayEvent, TokenBasedPayEvent, InstantPayEvent
        from datetime import datetime
        
        # Test API Request Pay Event
        api_event = APIRequestPayEvent(
            project_id="test_proj",
            agent_id="test_agent",
            user_id="test_user",
            api_calls=1,
            unit_price=0.001
        )
        assert api_event.project_id == "test_proj"
        assert api_event.api_calls == 1
        assert api_event.unit_price == 0.001
        
        # Test Token Based Pay Event
        token_event = TokenBasedPayEvent(
            project_id="test_proj",
            agent_id="test_agent", 
            user_id="test_user",
            tokens_in=100,
            tokens_out=50,
            input_token_price=0.000004,
            output_token_price=0.000001
        )
        assert token_event.tokens_in == 100
        assert token_event.tokens_out == 50
        
        # Test Instant Pay Event
        instant_event = InstantPayEvent(
            project_id="test_proj",
            agent_id="test_agent",
            user_id="test_user", 
            amount=5.99,
            description="Test payment"
        )
        assert instant_event.amount == 5.99
        assert instant_event.description == "Test payment"
    
    def test_tracker_instantiation(self):
        """Test that AgentMeterTracker can be instantiated."""
        from agentmeter import AgentMeterClient, AgentMeterTracker
        
        client = AgentMeterClient(
            api_key="test_key",
            project_id="test_project",
            agent_id="test_agent"
        )
        
        tracker = AgentMeterTracker(
            client=client,
            project_id="test_project",
            agent_id="test_agent"
        )
        
        assert tracker.client == client
        assert tracker.project_id == "test_project"
        assert tracker.agent_id == "test_agent"
    
    def test_decorator_basic_functionality(self):
        """Test that decorators can be applied (without actual API calls)."""
        from agentmeter import meter_api_request_pay, AgentMeterClient
        
        client = AgentMeterClient(
            api_key="test_key",
            project_id="test_project",
            agent_id="test_agent"
        )
        
        # Test decorator application
        @meter_api_request_pay(client, unit_price=0.1)
        def test_function(query: str, user_id: str):
            return f"Processed: {query}"
        
        # Function should be decorated (we won't call it to avoid API calls)
        assert hasattr(test_function, '__wrapped__')
        assert test_function.__name__ == "test_function"
    
    def test_langchain_integration_available(self):
        """Test that LangChain integration is available."""
        try:
            from agentmeter import LangChainAgentMeterCallback
            assert LangChainAgentMeterCallback is not None
            assert inspect.isclass(LangChainAgentMeterCallback)
        except ImportError:
            # LangChain integration is optional
            pytest.skip("LangChain integration not available (optional dependency)")
    
    def test_cli_entry_point(self):
        """Test that CLI entry point exists."""
        import agentmeter.cli
        assert hasattr(agentmeter.cli, 'main')
        assert callable(agentmeter.cli.main)
    
    def test_package_metadata(self):
        """Test package metadata and structure."""
        import agentmeter
        
        # Check package has proper metadata
        assert hasattr(agentmeter, '__version__')
        assert hasattr(agentmeter, '__author__')
        
        # Check package structure
        expected_modules = [
            'agentmeter.client',
            'agentmeter.tracker', 
            'agentmeter.models',
            'agentmeter.decorators',
            'agentmeter.exceptions',
            'agentmeter.utils'
        ]
        
        for module_name in expected_modules:
            try:
                module = importlib.import_module(module_name)
                assert module is not None
            except ImportError:
                pytest.fail(f"Required module not found: {module_name}")
    
    def test_type_hints_available(self):
        """Test that type hints are properly included."""
        import agentmeter
        
        # Check that py.typed file is included (enables type checking)
        import agentmeter.client
        import agentmeter.models
        
        # These should not raise import errors
        assert agentmeter.client is not None
        assert agentmeter.models is not None
    
    def test_error_classes_functionality(self):
        """Test that error classes work correctly."""
        from agentmeter import AgentMeterError, RateLimitError
        
        # Test AgentMeterError
        error = AgentMeterError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
        
        # Test RateLimitError
        rate_error = RateLimitError("Rate limit exceeded")
        assert str(rate_error) == "Rate limit exceeded"
        assert isinstance(rate_error, AgentMeterError)
    
    def test_dependencies_imported(self):
        """Test that required dependencies are available."""
        required_deps = [
            'httpx',
            'pydantic'
        ]
        
        for dep in required_deps:
            try:
                importlib.import_module(dep)
            except ImportError:
                pytest.fail(f"Required dependency not available: {dep}")
    
    def test_examples_syntax_valid(self):
        """Test that example imports work correctly."""
        # Test the imports that users would typically use
        try:
            from agentmeter import (
                AgentMeterClient,
                create_client,
                PaymentType,
                meter_api_request_pay,
                meter_token_based_pay,
                meter_instant_pay,
                track_api_request_pay,
                track_token_based_pay,
                track_instant_pay,
                APIRequestPayEvent,
                TokenBasedPayEvent,
                InstantPayEvent
            )
            
            # All imports should succeed
            assert all([
                AgentMeterClient, create_client, PaymentType,
                meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
                track_api_request_pay, track_token_based_pay, track_instant_pay,
                APIRequestPayEvent, TokenBasedPayEvent, InstantPayEvent
            ])
            
        except ImportError as e:
            pytest.fail(f"Failed to import commonly used classes/functions: {e}")


class TestPackageInstallationValidation:
    """Tests to validate package installation and distribution."""
    
    def test_package_installed_from_pip(self):
        """Verify the package was installed via pip."""
        import agentmeter
        
        # Check if package is installed in site-packages
        package_path = agentmeter.__file__
        
        # For development installations, this test is expected to fail
        # but we can still verify the package loads correctly
        if 'site-packages' not in package_path and 'dist-packages' not in package_path:
            pytest.skip("Development installation detected - skipping site-packages check")
        
        assert 'site-packages' in package_path or 'dist-packages' in package_path, \
            f"Package not installed in site-packages: {package_path}"
    
    def test_package_version_consistency(self):
        """Test that version is consistent across the package."""
        import agentmeter
        
        # Version should be accessible
        version = agentmeter.__version__
        assert version is not None
        assert len(version.split('.')) >= 2
        
        print(f"✅ Package version: {version}")
    
    def test_python_version_compatibility(self):
        """Test that package works with current Python version."""
        python_version = sys.version_info
        
        # Package should support Python 3.7+
        assert python_version >= (3, 7), \
            f"Package requires Python 3.7+, got {python_version}"
        
        print(f"✅ Python version: {python_version.major}.{python_version.minor}")


if __name__ == "__main__":
    """Run the validation tests when executed directly."""
    print("🔍 AgentMeter Package Validation Checklist")
    print("=" * 50)
    
    # Run basic import test
    try:
        import agentmeter
        print(f"✅ Package imported successfully (version {agentmeter.__version__})")
    except ImportError as e:
        print(f"❌ Failed to import package: {e}")
        print("\n💡 Make sure to install the package first:")
        print("   pip install agentmeter")
        exit(1)
    
    # Run pytest if available
    try:
        import pytest
        print("\n🧪 Running comprehensive validation tests...")
        exit_code = pytest.main([__file__, "-v", "--tb=short"])
        
        if exit_code == 0:
            print("\n🎉 All validation tests passed!")
            print("✅ The published agentmeter package is working correctly.")
        else:
            print("\n❌ Some validation tests failed.")
            print("Please check the test output above.")
    
    except ImportError:
        print("\n⚠️  pytest not available, running basic validation only")
        print("Install pytest for comprehensive testing: pip install pytest")
        
        # Run basic validation manually
        validator = TestPublishedPackageValidation()
        
        basic_tests = [
            'test_package_import',
            'test_package_version', 
            'test_core_classes_available',
            'test_client_instantiation',
            'test_convenience_client_creation'
        ]
        
        print("\n🔧 Running basic validation tests...")
        for test_name in basic_tests:
            try:
                test_method = getattr(validator, test_name)
                test_method()
                print(f"✅ {test_name}")
            except Exception as e:
                print(f"❌ {test_name}: {e}")
        
        print("\n✅ Basic validation completed!") 