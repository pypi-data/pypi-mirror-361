"""
Unit Tests for AgentMeter SDK v0.3.1 Models
Tests new data models, validation, serialization, and backward compatibility
"""

import unittest
from datetime import datetime
from agentmeter.models import (
    # New v0.3.1 models
    MeterEvent, MeterEventCreate, MeterType, UsageAggregation,
    # Legacy models (for backward compatibility)
    MeterEventLegacy, AgentMeterConfig
)


class TestMeterEvent(unittest.TestCase):
    """Test MeterEvent model (v0.3.1)"""
    
    def test_create_meter_event(self):
        """Test creating a meter event"""
        event = MeterEvent(
            id="evt_123456",
            meter_type_id="mt_789",
            subject_id="user_001",
            quantity=2.5,
            metadata={"source": "api", "request_id": "req_999"},
            created_at="2024-01-15T10:30:00Z"
        )
        
        self.assertEqual(event.id, "evt_123456")
        self.assertEqual(event.meter_type_id, "mt_789")
        self.assertEqual(event.subject_id, "user_001")
        self.assertEqual(event.quantity, 2.5)
        self.assertEqual(event.metadata["source"], "api")
        self.assertEqual(event.created_at, "2024-01-15T10:30:00Z")
    
    def test_meter_event_with_minimal_data(self):
        """Test creating meter event with minimal required data"""
        event = MeterEvent(
            id="evt_minimal",
            meter_type_id="mt_123",
            subject_id="user_123",
            quantity=1.0,
            created_at="2024-01-15T10:30:00Z"
        )
        
        self.assertEqual(event.id, "evt_minimal")
        self.assertEqual(event.quantity, 1.0)
        self.assertIsNone(event.metadata)
    
    def test_meter_event_serialization(self):
        """Test meter event to/from dict conversion"""
        original_event = MeterEvent(
            id="evt_serialization_test",
            meter_type_id="mt_serialize",
            subject_id="user_serialize",
            quantity=3.14,
            metadata={"test": True, "count": 42},
            created_at="2024-01-15T10:30:00Z"
        )
        
        # Convert to dict
        event_dict = original_event.dict()
        
        self.assertEqual(event_dict["id"], "evt_serialization_test")
        self.assertEqual(event_dict["quantity"], 3.14)
        self.assertEqual(event_dict["metadata"]["test"], True)
        
        # Create new event from dict
        new_event = MeterEvent(**event_dict)
        
        self.assertEqual(new_event.id, original_event.id)
        self.assertEqual(new_event.quantity, original_event.quantity)
        self.assertEqual(new_event.metadata, original_event.metadata)


class TestMeterEventCreate(unittest.TestCase):
    """Test MeterEventCreate model (for API requests)"""
    
    def test_create_meter_event_create(self):
        """Test creating a meter event creation model"""
        event_create = MeterEventCreate(
            meter_type_id="mt_create_test",
            subject_id="user_create",
            quantity=1.5,
            metadata={"operation": "create_user", "duration_ms": 250}
        )
        
        self.assertEqual(event_create.meter_type_id, "mt_create_test")
        self.assertEqual(event_create.subject_id, "user_create")
        self.assertEqual(event_create.quantity, 1.5)
        self.assertEqual(event_create.metadata["operation"], "create_user")
    
    def test_meter_event_create_without_metadata(self):
        """Test creating meter event without metadata"""
        event_create = MeterEventCreate(
            meter_type_id="mt_no_metadata",
            subject_id="user_no_metadata",
            quantity=0.5
        )
        
        self.assertEqual(event_create.meter_type_id, "mt_no_metadata")
        self.assertEqual(event_create.quantity, 0.5)
        self.assertIsNone(event_create.metadata)
    
    def test_meter_event_create_validation(self):
        """Test meter event create validation"""
        # Test quantity must be positive
        with self.assertRaises(ValueError):
            MeterEventCreate(
                meter_type_id="mt_validation",
                subject_id="user_validation",
                quantity=-1.0  # Invalid negative quantity
            )
        
        # Test meter_type_id cannot be empty
        with self.assertRaises(ValueError):
            MeterEventCreate(
                meter_type_id="",  # Empty meter type ID
                subject_id="user_validation",
                quantity=1.0
            )
        
        # Test subject_id cannot be empty
        with self.assertRaises(ValueError):
            MeterEventCreate(
                meter_type_id="mt_validation",
                subject_id="",  # Empty subject ID
                quantity=1.0
            )


class TestMeterType(unittest.TestCase):
    """Test MeterType model"""
    
    def test_create_meter_type(self):
        """Test creating a meter type"""
        meter_type = MeterType(
            id="mt_api_requests",
            name="API Requests",
            description="Track API request usage across the platform",
            created_at="2024-01-15T10:30:00Z"
        )
        
        self.assertEqual(meter_type.id, "mt_api_requests")
        self.assertEqual(meter_type.name, "API Requests")
        self.assertEqual(meter_type.description, "Track API request usage across the platform")
        self.assertEqual(meter_type.created_at, "2024-01-15T10:30:00Z")
    
    def test_meter_type_without_description(self):
        """Test creating meter type without description"""
        meter_type = MeterType(
            id="mt_minimal",
            name="Minimal Meter",
            created_at="2024-01-15T10:30:00Z"
        )
        
        self.assertEqual(meter_type.name, "Minimal Meter")
        self.assertIsNone(meter_type.description)
    
    def test_meter_type_serialization(self):
        """Test meter type serialization"""
        original_type = MeterType(
            id="mt_serialization",
            name="Serialization Test",
            description="Test meter type serialization",
            created_at="2024-01-15T10:30:00Z"
        )
        
        # Convert to dict
        type_dict = original_type.dict()
        
        self.assertEqual(type_dict["id"], "mt_serialization")
        self.assertEqual(type_dict["name"], "Serialization Test")
        
        # Create new type from dict
        new_type = MeterType(**type_dict)
        
        self.assertEqual(new_type.id, original_type.id)
        self.assertEqual(new_type.name, original_type.name)
        self.assertEqual(new_type.description, original_type.description)


class TestUsageAggregation(unittest.TestCase):
    """Test UsageAggregation model"""
    
    def test_create_usage_aggregation(self):
        """Test creating usage aggregation"""
        aggregation = UsageAggregation(
            meter_type_id="mt_aggregation_test",
            subject_id="user_aggregation",
            total_quantity=15.75,
            event_count=12,
            period_start="2024-01-01T00:00:00Z",
            period_end="2024-01-01T23:59:59Z"
        )
        
        self.assertEqual(aggregation.meter_type_id, "mt_aggregation_test")
        self.assertEqual(aggregation.subject_id, "user_aggregation")
        self.assertEqual(aggregation.total_quantity, 15.75)
        self.assertEqual(aggregation.event_count, 12)
        self.assertEqual(aggregation.period_start, "2024-01-01T00:00:00Z")
        self.assertEqual(aggregation.period_end, "2024-01-01T23:59:59Z")
    
    def test_usage_aggregation_average_calculation(self):
        """Test average quantity calculation"""
        aggregation = UsageAggregation(
            meter_type_id="mt_average_test",
            subject_id="user_average",
            total_quantity=20.0,
            event_count=4,
            period_start="2024-01-01T00:00:00Z",
            period_end="2024-01-01T23:59:59Z"
        )
        
        # Calculate average manually
        expected_average = aggregation.total_quantity / aggregation.event_count
        self.assertEqual(expected_average, 5.0)
    
    def test_usage_aggregation_zero_events(self):
        """Test aggregation with zero events"""
        aggregation = UsageAggregation(
            meter_type_id="mt_zero_test",
            subject_id="user_zero",
            total_quantity=0.0,
            event_count=0,
            period_start="2024-01-01T00:00:00Z",
            period_end="2024-01-01T23:59:59Z"
        )
        
        self.assertEqual(aggregation.total_quantity, 0.0)
        self.assertEqual(aggregation.event_count, 0)


class TestAgentMeterConfig(unittest.TestCase):
    """Test AgentMeterConfig model"""
    
    def test_create_config(self):
        """Test creating AgentMeter configuration"""
        config = AgentMeterConfig(
            api_key="test_api_key_12345",
            base_url="https://api.agentmeter.money",
            timeout=30.0,
            max_retries=3
        )
        
        self.assertEqual(config.api_key, "test_api_key_12345")
        self.assertEqual(config.base_url, "https://api.agentmeter.money")
        self.assertEqual(config.timeout, 30.0)
        self.assertEqual(config.max_retries, 3)
    
    def test_config_with_defaults(self):
        """Test config with default values"""
        config = AgentMeterConfig(
            api_key="minimal_config_key"
        )
        
        self.assertEqual(config.api_key, "minimal_config_key")
        self.assertEqual(config.base_url, "https://api.agentmeter.money")
        self.assertEqual(config.timeout, 30.0)
        self.assertEqual(config.max_retries, 3)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test empty API key
        with self.assertRaises(ValueError):
            AgentMeterConfig(api_key="")
        
        # Test invalid timeout
        with self.assertRaises(ValueError):
            AgentMeterConfig(
                api_key="valid_key",
                timeout=-1.0
            )
        
        # Test invalid max_retries
        with self.assertRaises(ValueError):
            AgentMeterConfig(
                api_key="valid_key",
                max_retries=-1
            )


class TestLegacyCompatibility(unittest.TestCase):
    """Test backward compatibility with legacy models"""
    
    def test_legacy_meter_event(self):
        """Test legacy MeterEventLegacy model still works"""
        legacy_event = MeterEventLegacy(
            id="legacy_evt_123",
            project_id="legacy_project",
            agent_id="legacy_agent",
            user_id="legacy_user",
            payment_type="api_request_pay",
            api_calls=2,
            unit_price=0.15,
            total_cost=0.30,
            timestamp="2024-01-15T10:30:00Z"
        )
        
        self.assertEqual(legacy_event.id, "legacy_evt_123")
        self.assertEqual(legacy_event.project_id, "legacy_project")
        self.assertEqual(legacy_event.payment_type, "api_request_pay")
        self.assertEqual(legacy_event.api_calls, 2)
        self.assertEqual(legacy_event.total_cost, 0.30)
    
    def test_legacy_token_based_event(self):
        """Test legacy token-based event"""
        legacy_event = MeterEventLegacy(
            id="legacy_token_evt",
            project_id="legacy_project",
            agent_id="legacy_agent",
            user_id="legacy_user",
            payment_type="token_based_pay",
            tokens_in=1000,
            tokens_out=500,
            input_token_price=0.00001,
            output_token_price=0.00002,
            total_cost=0.020,
            timestamp="2024-01-15T10:30:00Z"
        )
        
        self.assertEqual(legacy_event.payment_type, "token_based_pay")
        self.assertEqual(legacy_event.tokens_in, 1000)
        self.assertEqual(legacy_event.tokens_out, 500)
        self.assertEqual(legacy_event.total_cost, 0.020)
    
    def test_legacy_instant_pay_event(self):
        """Test legacy instant pay event"""
        legacy_event = MeterEventLegacy(
            id="legacy_instant_evt",
            project_id="legacy_project",
            agent_id="legacy_agent",
            user_id="legacy_user",
            payment_type="instant_pay",
            amount=4.99,
            description="Premium Feature",
            total_cost=4.99,
            timestamp="2024-01-15T10:30:00Z"
        )
        
        self.assertEqual(legacy_event.payment_type, "instant_pay")
        self.assertEqual(legacy_event.amount, 4.99)
        self.assertEqual(legacy_event.description, "Premium Feature")
        self.assertEqual(legacy_event.total_cost, 4.99)


class TestModelValidation(unittest.TestCase):
    """Test model validation and edge cases"""
    
    def test_meter_event_quantity_validation(self):
        """Test meter event quantity validation"""
        # Valid quantities should work
        valid_quantities = [0.0, 0.001, 1.0, 100.0, 999999.99]
        
        for quantity in valid_quantities:
            event = MeterEvent(
                id=f"evt_quantity_{quantity}",
                meter_type_id="mt_validation",
                subject_id="user_validation",
                quantity=quantity,
                created_at="2024-01-15T10:30:00Z"
            )
            self.assertEqual(event.quantity, quantity)
        
        # Invalid quantities should raise errors
        invalid_quantities = [-1.0, -0.001]
        
        for quantity in invalid_quantities:
            with self.assertRaises(ValueError):
                MeterEvent(
                    id=f"evt_invalid_{abs(quantity)}",
                    meter_type_id="mt_validation",
                    subject_id="user_validation",
                    quantity=quantity,
                    created_at="2024-01-15T10:30:00Z"
                )
    
    def test_meter_type_name_validation(self):
        """Test meter type name validation"""
        # Valid names should work
        valid_names = ["API Requests", "Token Usage", "Premium Features", "A"]
        
        for name in valid_names:
            meter_type = MeterType(
                id=f"mt_{name.replace(' ', '_').lower()}",
                name=name,
                created_at="2024-01-15T10:30:00Z"
            )
            self.assertEqual(meter_type.name, name)
        
        # Empty name should raise error
        with self.assertRaises(ValueError):
            MeterType(
                id="mt_empty_name",
                name="",
                created_at="2024-01-15T10:30:00Z"
            )
    
    def test_usage_aggregation_consistency(self):
        """Test usage aggregation data consistency"""
        # Event count should be non-negative
        with self.assertRaises(ValueError):
            UsageAggregation(
                meter_type_id="mt_consistency",
                subject_id="user_consistency",
                total_quantity=10.0,
                event_count=-1,  # Invalid negative count
                period_start="2024-01-01T00:00:00Z",
                period_end="2024-01-01T23:59:59Z"
            )
        
        # Total quantity should be non-negative
        with self.assertRaises(ValueError):
            UsageAggregation(
                meter_type_id="mt_consistency",
                subject_id="user_consistency",
                total_quantity=-5.0,  # Invalid negative total
                event_count=5,
                period_start="2024-01-01T00:00:00Z",
                period_end="2024-01-01T23:59:59Z"
            )


class TestModelSerialization(unittest.TestCase):
    """Test model serialization and deserialization"""
    
    def test_meter_event_json_serialization(self):
        """Test meter event JSON serialization"""
        event = MeterEvent(
            id="evt_json_test",
            meter_type_id="mt_json",
            subject_id="user_json",
            quantity=2.5,
            metadata={"test": True, "count": 42},
            created_at="2024-01-15T10:30:00Z"
        )
        
        # Test JSON serialization
        json_data = event.json()
        self.assertIsInstance(json_data, str)
        
        # Test deserialization
        parsed_event = MeterEvent.parse_raw(json_data)
        self.assertEqual(parsed_event.id, event.id)
        self.assertEqual(parsed_event.quantity, event.quantity)
        self.assertEqual(parsed_event.metadata, event.metadata)
    
    def test_meter_type_json_serialization(self):
        """Test meter type JSON serialization"""
        meter_type = MeterType(
            id="mt_json_test",
            name="JSON Test Meter",
            description="Test JSON serialization",
            created_at="2024-01-15T10:30:00Z"
        )
        
        # Test JSON serialization
        json_data = meter_type.json()
        self.assertIsInstance(json_data, str)
        
        # Test deserialization
        parsed_type = MeterType.parse_raw(json_data)
        self.assertEqual(parsed_type.id, meter_type.id)
        self.assertEqual(parsed_type.name, meter_type.name)
        self.assertEqual(parsed_type.description, meter_type.description)
    
    def test_usage_aggregation_json_serialization(self):
        """Test usage aggregation JSON serialization"""
        aggregation = UsageAggregation(
            meter_type_id="mt_json_agg",
            subject_id="user_json_agg",
            total_quantity=25.5,
            event_count=10,
            period_start="2024-01-01T00:00:00Z",
            period_end="2024-01-01T23:59:59Z"
        )
        
        # Test JSON serialization
        json_data = aggregation.json()
        self.assertIsInstance(json_data, str)
        
        # Test deserialization
        parsed_agg = UsageAggregation.parse_raw(json_data)
        self.assertEqual(parsed_agg.total_quantity, aggregation.total_quantity)
        self.assertEqual(parsed_agg.event_count, aggregation.event_count)
        self.assertEqual(parsed_agg.period_start, aggregation.period_start)


if __name__ == '__main__':
    unittest.main() 