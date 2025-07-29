"""
Unit Tests for AgentMeter SDK v0.3.1
Tests new architecture with resource managers, async clients, and backward compatibility
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
import time
from datetime import datetime
from agentmeter import (
    # New v0.3.1 architecture
    AgentMeter, AsyncAgentMeter, MeterEvent, MeterEventCreate, MeterType,
    UsageAggregation,
    # Legacy compatibility (should still work)
    AgentMeterClient, create_client
)
from agentmeter.exceptions import (
    AgentMeterError, AuthenticationError, ValidationError, 
    RateLimitError, ServerError
)


class TestAgentMeterClient(unittest.TestCase):
    """Test new AgentMeter v0.3.1 client"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.base_url = "https://api.agentmeter.money"
        
        # Mock successful response data
        self.mock_meter_event = {
            "id": "evt_123",
            "meter_type_id": "mt_123",
            "subject_id": "user_123",
            "quantity": 1.0,
            "metadata": {"test": "data"},
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        self.mock_meter_type = {
            "id": "mt_123",
            "name": "API Requests",
            "description": "Track API request usage",
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    def test_client_initialization(self):
        """Test client initialization"""
        with patch('agentmeter.client.httpx.Client'):
            client = AgentMeter(api_key=self.api_key)
            
            self.assertEqual(client.api_key, self.api_key)
            self.assertEqual(client.base_url, self.base_url)
            self.assertIsNotNone(client.meter_events)
            self.assertIsNotNone(client.meter_types)
            self.assertIsNotNone(client.projects)
            self.assertIsNotNone(client.users)
    
    def test_client_with_custom_base_url(self):
        """Test client with custom base URL"""
        custom_url = "https://custom.agentmeter.money"
        
        with patch('agentmeter.client.httpx.Client'):
            client = AgentMeter(api_key=self.api_key, base_url=custom_url)
            
            self.assertEqual(client.base_url, custom_url)
    
    def test_context_manager(self):
        """Test client as context manager"""
        with patch('agentmeter.client.httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            with AgentMeter(api_key=self.api_key) as client:
                self.assertIsNotNone(client)
                mock_client.close.assert_not_called()  # Should not close yet
            
            mock_client.close.assert_called_once()  # Should close after exit
    
    @patch('agentmeter.resources.meter_events.httpx.Client')
    def test_meter_events_record(self, mock_client_class):
        """Test recording meter events"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = self.mock_meter_event
        mock_client.post.return_value = mock_response
        
        client = AgentMeter(api_key=self.api_key)
        
        event = client.meter_events.record(
            meter_type_id="mt_123",
            subject_id="user_123",
            quantity=1.0,
            metadata={"test": "data"}
        )
        
        self.assertIsInstance(event, MeterEvent)
        self.assertEqual(event.id, "evt_123")
        self.assertEqual(event.quantity, 1.0)
        mock_client.post.assert_called_once()
    
    @patch('agentmeter.resources.meter_events.httpx.Client')
    def test_meter_events_list(self, mock_client_class):
        """Test listing meter events"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.mock_meter_event]
        mock_client.get.return_value = mock_response
        
        client = AgentMeter(api_key=self.api_key)
        
        events = client.meter_events.list(subject_id="user_123", limit=10)
        
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], MeterEvent)
        mock_client.get.assert_called_once()
    
    @patch('agentmeter.resources.meter_types.httpx.Client')
    def test_meter_types_create(self, mock_client_class):
        """Test creating meter types"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = self.mock_meter_type
        mock_client.post.return_value = mock_response
        
        client = AgentMeter(api_key=self.api_key)
        
        meter_type = client.meter_types.create(
            name="API Requests",
            description="Track API request usage"
        )
        
        self.assertIsInstance(meter_type, MeterType)
        self.assertEqual(meter_type.name, "API Requests")
        mock_client.post.assert_called_once()
    
    @patch('agentmeter.resources.meter_types.httpx.Client')
    def test_meter_types_list(self, mock_client_class):
        """Test listing meter types"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.mock_meter_type]
        mock_client.get.return_value = mock_response
        
        client = AgentMeter(api_key=self.api_key)
        
        meter_types = client.meter_types.list()
        
        self.assertIsInstance(meter_types, list)
        self.assertEqual(len(meter_types), 1)
        self.assertIsInstance(meter_types[0], MeterType)
        mock_client.get.assert_called_once()
    
    def test_error_handling_authentication(self):
        """Test authentication error handling"""
        with patch('agentmeter.client.httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "Invalid API key"}
            mock_client.post.return_value = mock_response
            
            client = AgentMeter(api_key="invalid_key")
            
            with self.assertRaises(AuthenticationError):
                client.meter_events.record(
                    meter_type_id="mt_123",
                    subject_id="user_123",
                    quantity=1.0
                )
    
    def test_error_handling_validation(self):
        """Test validation error handling"""
        with patch('agentmeter.client.httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Invalid quantity"}
            mock_client.post.return_value = mock_response
            
            client = AgentMeter(api_key=self.api_key)
            
            with self.assertRaises(ValidationError):
                client.meter_events.record(
                    meter_type_id="mt_123",
                    subject_id="user_123",
                    quantity=-1.0  # Invalid quantity
                )
    
    def test_error_handling_rate_limit(self):
        """Test rate limit error handling"""
        with patch('agentmeter.client.httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {"error": "Rate limit exceeded"}
            mock_client.post.return_value = mock_response
            
            client = AgentMeter(api_key=self.api_key)
            
            with self.assertRaises(RateLimitError):
                client.meter_events.record(
                    meter_type_id="mt_123",
                    subject_id="user_123",
                    quantity=1.0
                )
    
    def test_error_handling_server_error(self):
        """Test server error handling"""
        with patch('agentmeter.client.httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal server error"}
            mock_client.post.return_value = mock_response
            
            client = AgentMeter(api_key=self.api_key)
            
            with self.assertRaises(ServerError):
                client.meter_events.record(
                    meter_type_id="mt_123",
                    subject_id="user_123",
                    quantity=1.0
                )


class TestAsyncAgentMeter(unittest.TestCase):
    """Test AsyncAgentMeter client"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.mock_meter_event = {
            "id": "evt_123",
            "meter_type_id": "mt_123",
            "subject_id": "user_123",
            "quantity": 1.0,
            "metadata": {"test": "data"},
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    async def test_async_client_initialization(self):
        """Test async client initialization"""
        with patch('agentmeter.client.httpx.AsyncClient'):
            async with AsyncAgentMeter(api_key=self.api_key) as client:
                self.assertEqual(client.api_key, self.api_key)
                self.assertIsNotNone(client.meter_events)
    
    async def test_async_meter_events_record(self):
        """Test async meter events recording"""
        with patch('agentmeter.client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = self.mock_meter_event
            mock_client.post.return_value = mock_response
            
            async with AsyncAgentMeter(api_key=self.api_key) as client:
                event = await client.meter_events.record(
                    meter_type_id="mt_123",
                    subject_id="user_123",
                    quantity=1.0
                )
                
                self.assertIsInstance(event, MeterEvent)
                self.assertEqual(event.id, "evt_123")
                mock_client.post.assert_called_once()
    
    def test_async_context_manager(self):
        """Test async client context manager"""
        async def run_test():
            with patch('agentmeter.client.httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value = mock_client
                
                async with AsyncAgentMeter(api_key=self.api_key) as client:
                    self.assertIsNotNone(client)
                    mock_client.aclose.assert_not_called()  # Should not close yet
                
                mock_client.aclose.assert_called_once()  # Should close after exit
        
        asyncio.run(run_test())


class TestLegacyCompatibility(unittest.TestCase):
    """Test backward compatibility with v0.2.0 API"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.project_id = "test_project"
        self.agent_id = "test_agent"
        self.user_id = "test_user"
    
    @patch('agentmeter.models.httpx.Client')
    def test_legacy_client_creation(self, mock_client_class):
        """Test legacy AgentMeterClient still works"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_client.get.return_value = mock_response
        
        # This should still work for backward compatibility
        client = AgentMeterClient(
            api_key=self.api_key,
            project_id=self.project_id,
            agent_id=self.agent_id,
            user_id=self.user_id
        )
        
        self.assertEqual(client.api_key, self.api_key)
        self.assertEqual(client.project_id, self.project_id)
        self.assertEqual(client.agent_id, self.agent_id)
        self.assertEqual(client.user_id, self.user_id)
    
    @patch('agentmeter.models.httpx.Client')
    def test_create_client_helper(self, mock_client_class):
        """Test create_client helper function still works"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_client.get.return_value = mock_response
        
        client = create_client(
            api_key=self.api_key,
            project_id=self.project_id,
            agent_id=self.agent_id,
            user_id=self.user_id
        )
        
        self.assertIsInstance(client, AgentMeterClient)
        self.assertEqual(client.api_key, self.api_key)
    
    @patch('agentmeter.models.httpx.Client')
    def test_legacy_record_methods(self, mock_client_class):
        """Test legacy record methods still work"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock response for meter operations
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "evt_123",
            "total_cost": 0.10,
            "api_calls": 1,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        mock_client.post.return_value = mock_response
        
        client = AgentMeterClient(
            api_key=self.api_key,
            project_id=self.project_id,
            agent_id=self.agent_id,
            user_id=self.user_id
        )
        
        # Test legacy API request method
        response = client.record_api_request_pay(
            api_calls=1,
            unit_price=0.10,
            user_id=self.user_id
        )
        
        self.assertIsNotNone(response)
        mock_client.post.assert_called()


class TestModels(unittest.TestCase):
    """Test new v0.3.1 models"""
    
    def test_meter_event_creation(self):
        """Test MeterEvent model creation"""
        event = MeterEvent(
            id="evt_123",
            meter_type_id="mt_123",
            subject_id="user_123",
            quantity=1.5,
            metadata={"test": "data"},
            created_at="2024-01-01T00:00:00Z"
        )
        
        self.assertEqual(event.id, "evt_123")
        self.assertEqual(event.meter_type_id, "mt_123")
        self.assertEqual(event.subject_id, "user_123")
        self.assertEqual(event.quantity, 1.5)
        self.assertEqual(event.metadata, {"test": "data"})
    
    def test_meter_event_create_model(self):
        """Test MeterEventCreate model"""
        event_create = MeterEventCreate(
            meter_type_id="mt_123",
            subject_id="user_123",
            quantity=2.0,
            metadata={"source": "test"}
        )
        
        self.assertEqual(event_create.meter_type_id, "mt_123")
        self.assertEqual(event_create.subject_id, "user_123")
        self.assertEqual(event_create.quantity, 2.0)
        self.assertEqual(event_create.metadata, {"source": "test"})
    
    def test_meter_type_creation(self):
        """Test MeterType model creation"""
        meter_type = MeterType(
            id="mt_123",
            name="API Requests",
            description="Track API usage",
            created_at="2024-01-01T00:00:00Z"
        )
        
        self.assertEqual(meter_type.id, "mt_123")
        self.assertEqual(meter_type.name, "API Requests")
        self.assertEqual(meter_type.description, "Track API usage")
    
    def test_usage_aggregation_creation(self):
        """Test UsageAggregation model creation"""
        aggregation = UsageAggregation(
            meter_type_id="mt_123",
            subject_id="user_123",
            total_quantity=10.5,
            event_count=5,
            period_start="2024-01-01T00:00:00Z",
            period_end="2024-01-01T23:59:59Z"
        )
        
        self.assertEqual(aggregation.meter_type_id, "mt_123")
        self.assertEqual(aggregation.subject_id, "user_123")
        self.assertEqual(aggregation.total_quantity, 10.5)
        self.assertEqual(aggregation.event_count, 5)


class TestRetryLogic(unittest.TestCase):
    """Test retry logic and error handling"""
    
    @patch('agentmeter.utils.retry.time.sleep')  # Mock sleep to speed up tests
    @patch('agentmeter.client.httpx.Client')
    def test_retry_on_server_error(self, mock_client_class, mock_sleep):
        """Test retry logic on server errors"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # First call fails with 500, second succeeds
        fail_response = Mock()
        fail_response.status_code = 500
        fail_response.json.return_value = {"error": "Server error"}
        
        success_response = Mock()
        success_response.status_code = 201
        success_response.json.return_value = {
            "id": "evt_123",
            "meter_type_id": "mt_123",
            "subject_id": "user_123",
            "quantity": 1.0,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        mock_client.post.side_effect = [fail_response, success_response]
        
        client = AgentMeter(api_key="test_key")
        
        # Should succeed after retry
        event = client.meter_events.record(
            meter_type_id="mt_123",
            subject_id="user_123",
            quantity=1.0
        )
        
        self.assertEqual(event.id, "evt_123")
        self.assertEqual(mock_client.post.call_count, 2)  # Called twice due to retry
        mock_sleep.assert_called()  # Sleep was called for retry delay


class TestValidation(unittest.TestCase):
    """Test input validation"""
    
    def test_meter_event_validation(self):
        """Test meter event validation"""
        with patch('agentmeter.client.httpx.Client'):
            client = AgentMeter(api_key="test_key")
            
            # Test empty meter_type_id
            with self.assertRaises(ValueError):
                client.meter_events.record(
                    meter_type_id="",
                    subject_id="user_123",
                    quantity=1.0
                )
            
            # Test empty subject_id
            with self.assertRaises(ValueError):
                client.meter_events.record(
                    meter_type_id="mt_123",
                    subject_id="",
                    quantity=1.0
                )
            
            # Test negative quantity
            with self.assertRaises(ValueError):
                client.meter_events.record(
                    meter_type_id="mt_123",
                    subject_id="user_123",
                    quantity=-1.0
                )


if __name__ == '__main__':
    unittest.main()