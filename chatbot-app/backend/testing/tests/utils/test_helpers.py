"""
Test utilities and helper functions for chatbot backend testing.

This module provides common test utilities, data generators, mock factories,
and assertion helpers used across all test modules.
"""

import json
import uuid
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from unittest.mock import Mock, AsyncMock, MagicMock
import pytest


class TestDataFactory:
    """Factory for generating test data"""

    @staticmethod
    def generate_user_id() -> str:
        """Generate a unique user ID"""
        return f"user_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def generate_conversation_id() -> str:
        """Generate a unique conversation ID"""
        return f"conv_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def generate_message_id() -> str:
        """Generate a unique message ID"""
        return f"msg_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def generate_session_id() -> str:
        """Generate a unique session ID"""
        return f"session_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """Generate a random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def generate_email() -> str:
        """Generate a random email address"""
        username = TestDataFactory.generate_random_string(8)
        domain = random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'example.com'])
        return f"{username}@{domain}"

    @staticmethod
    def generate_phone() -> str:
        """Generate a random phone number"""
        return f"+1{random.randint(2000000000, 9999999999)}"

    @staticmethod
    def generate_timestamp(days_ago: int = 0) -> str:
        """Generate a timestamp string"""
        dt = datetime.now() - timedelta(days=days_ago)
        return dt.isoformat()

    @staticmethod
    def generate_user_profile() -> Dict[str, Any]:
        """Generate a complete user profile"""
        return {
            "user_id": TestDataFactory.generate_user_id(),
            "name": f"{TestDataFactory.generate_random_string(5)} {TestDataFactory.generate_random_string(7)}",
            "email": TestDataFactory.generate_email(),
            "phone": TestDataFactory.generate_phone(),
            "preferences": {
                "language": random.choice(["en", "es", "fr", "de"]),
                "theme": random.choice(["light", "dark"]),
                "notifications": random.choice([True, False])
            },
            "behavioral_traits": {
                "engagement_level": random.choice(["low", "medium", "high"]),
                "communication_style": random.choice(["formal", "casual", "technical"]),
                "response_preference": random.choice(["brief", "detailed", "comprehensive"])
            },
            "engagement_metrics": {
                "total_sessions": random.randint(1, 100),
                "average_session_length": random.uniform(5.0, 60.0),
                "last_active": TestDataFactory.generate_timestamp(random.randint(0, 30))
            },
            "created_at": TestDataFactory.generate_timestamp(random.randint(1, 365)),
            "updated_at": TestDataFactory.generate_timestamp(random.randint(0, 30))
        }

    @staticmethod
    def generate_conversation(user_id: str = None, message_count: int = 5) -> Dict[str, Any]:
        """Generate a conversation with messages"""
        conv_id = TestDataFactory.generate_conversation_id()
        user_id = user_id or TestDataFactory.generate_user_id()

        messages = []
        for i in range(message_count):
            messages.append({
                "message_id": TestDataFactory.generate_message_id(),
                "conversation_id": conv_id,
                "user_id": user_id,
                "content": TestDataFactory.generate_random_string(50 + random.randint(0, 100)),
                "timestamp": TestDataFactory.generate_timestamp(random.randint(0, 1)),
                "sender": random.choice(["user", "assistant"]),
                "metadata": {
                    "channel": random.choice(["web", "mobile", "api"]),
                    "intent": random.choice(["greeting", "question", "booking", "complaint", None])
                }
            })

        return {
            "conversation_id": conv_id,
            "user_id": user_id,
            "messages": messages,
            "created_at": TestDataFactory.generate_timestamp(1),
            "updated_at": TestDataFactory.generate_timestamp(0),
            "status": random.choice(["active", "completed", "archived"]),
            "metadata": {
                "total_messages": message_count,
                "duration_minutes": random.uniform(1, 120),
                "topics": random.sample(["booking", "support", "information", "complaint"], 2)
            }
        }

    @staticmethod
    def generate_ai_request() -> Dict[str, Any]:
        """Generate an AI service request"""
        return {
            "message": TestDataFactory.generate_random_string(100),
            "user_id": TestDataFactory.generate_user_id(),
            "conversation_id": TestDataFactory.generate_conversation_id(),
            "context": {
                "channel": random.choice(["web", "mobile", "api"]),
                "session_id": TestDataFactory.generate_session_id(),
                "previous_intent": random.choice(["greeting", "booking", "question", None])
            },
            "metadata": {
                "language": random.choice(["en", "es", "fr"]),
                "priority": random.choice(["low", "medium", "high"])
            }
        }

    @staticmethod
    def generate_export_request() -> Dict[str, Any]:
        """Generate an export request"""
        return {
            "export_type": random.choice(["conversations", "users", "analytics", "messages"]),
            "format": random.choice(["json", "csv", "xml", "xlsx"]),
            "filters": {
                "date_from": TestDataFactory.generate_timestamp(30),
                "date_to": TestDataFactory.generate_timestamp(0),
                "user_id": TestDataFactory.generate_user_id() if random.choice([True, False]) else None
            },
            "include_metadata": random.choice([True, False]),
            "compression": random.choice([True, False])
        }

    @staticmethod
    def generate_backup_request() -> Dict[str, Any]:
        """Generate a backup request"""
        return {
            "backup_type": random.choice(["full", "incremental"]),
            "include_data": True,
            "include_config": random.choice([True, False]),
            "retention_days": random.randint(7, 365),
            "encryption": random.choice([True, False])
        }


class MockFactory:
    """Factory for creating mock objects"""

    @staticmethod
    def create_mock_service(service_name: str) -> Mock:
        """Create a mock service with common methods"""
        mock_service = Mock()
        mock_service.name = service_name

        # Add common service methods
        mock_service.start = AsyncMock(return_value=True)
        mock_service.stop = AsyncMock(return_value=True)
        mock_service.health_check = AsyncMock(return_value={"status": "healthy"})
        mock_service.get_status = AsyncMock(return_value={"status": "running"})

        return mock_service

    @staticmethod
    def create_mock_database() -> Mock:
        """Create a mock database connection"""
        mock_db = Mock()

        # Mock connection methods
        mock_db.connect = AsyncMock(return_value=True)
        mock_db.disconnect = AsyncMock(return_value=True)
        mock_db.is_connected = Mock(return_value=True)

        # Mock query methods
        mock_db.execute = AsyncMock(return_value=None)
        mock_db.fetchone = AsyncMock(return_value=None)
        mock_db.fetchall = AsyncMock(return_value=[])
        mock_db.commit = AsyncMock(return_value=True)
        mock_db.rollback = AsyncMock(return_value=True)

        return mock_db

    @staticmethod
    def create_mock_redis() -> Mock:
        """Create a mock Redis client"""
        mock_redis = Mock()

        # Mock Redis methods
        mock_redis.get = Mock(return_value=None)
        mock_redis.set = Mock(return_value=True)
        mock_redis.delete = Mock(return_value=1)
        mock_redis.exists = Mock(return_value=0)
        mock_redis.expire = Mock(return_value=True)
        mock_redis.ttl = Mock(return_value=-1)

        # Mock hash operations
        mock_redis.hget = Mock(return_value=None)
        mock_redis.hset = Mock(return_value=1)
        mock_redis.hgetall = Mock(return_value={})
        mock_redis.hdel = Mock(return_value=1)

        # Mock list operations
        mock_redis.lpush = Mock(return_value=1)
        mock_redis.rpush = Mock(return_value=1)
        mock_redis.lpop = Mock(return_value=None)
        mock_redis.rpop = Mock(return_value=None)
        mock_redis.llen = Mock(return_value=0)

        return mock_redis

    @staticmethod
    def create_mock_http_client() -> Mock:
        """Create a mock HTTP client"""
        mock_client = Mock()

        # Mock HTTP methods
        mock_client.get = AsyncMock()
        mock_client.post = AsyncMock()
        mock_client.put = AsyncMock()
        mock_client.delete = AsyncMock()
        mock_client.patch = AsyncMock()

        # Mock response factory
        def create_mock_response(status_code=200, json_data=None):
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.json = Mock(return_value=json_data or {})
            mock_response.text = Mock(return_value=json.dumps(json_data or {}))
            mock_response.raise_for_status = Mock(return_value=None)
            return mock_response

        # Configure default responses
        mock_client.get.return_value = create_mock_response()
        mock_client.post.return_value = create_mock_response()
        mock_client.put.return_value = create_mock_response()
        mock_client.delete.return_value = create_mock_response()

        return mock_client

    @staticmethod
    def create_mock_ai_model(model_type: str = "nlp") -> Mock:
        """Create a mock AI model"""
        mock_model = Mock()
        mock_model.type = model_type
        mock_model.version = "1.0.0"
        mock_model.is_loaded = True

        if model_type == "nlp":
            mock_model.process = AsyncMock(return_value={
                "tokens": ["hello", "world"],
                "entities": [],
                "sentiment": "neutral"
            })
        elif model_type == "intent":
            mock_model.predict = AsyncMock(return_value={
                "intent": "greeting",
                "confidence": 0.9
            })
        elif model_type == "sentiment":
            mock_model.analyze = AsyncMock(return_value={
                "sentiment": "positive",
                "confidence": 0.85
            })

        mock_model.load = AsyncMock(return_value=True)
        mock_model.unload = AsyncMock(return_value=True)
        mock_model.get_info = AsyncMock(return_value={
            "type": model_type,
            "version": "1.0.0",
            "status": "loaded"
        })

        return mock_model


class AssertionHelpers:
    """Helper functions for common assertions"""

    @staticmethod
    def assert_valid_user_profile(profile: Dict[str, Any]):
        """Assert that a user profile has all required fields"""
        required_fields = ["user_id", "name", "email", "created_at"]
        for field in required_fields:
            assert field in profile, f"Missing required field: {field}"
            assert profile[field], f"Field {field} cannot be empty"

        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        assert re.match(email_pattern, profile["email"]), "Invalid email format"

    @staticmethod
    def assert_valid_conversation(conversation: Dict[str, Any]):
        """Assert that a conversation has all required fields"""
        required_fields = ["conversation_id", "user_id", "messages", "created_at"]
        for field in required_fields:
            assert field in conversation, f"Missing required field: {field}"

        assert isinstance(conversation["messages"], list), "Messages must be a list"
        assert len(conversation["messages"]) > 0, "Conversation must have at least one message"

        # Validate message structure
        for message in conversation["messages"]:
            required_msg_fields = ["message_id", "content", "timestamp", "sender"]
            for field in required_msg_fields:
                assert field in message, f"Message missing required field: {field}"

    @staticmethod
    def assert_valid_ai_response(response: Dict[str, Any]):
        """Assert that an AI response has all required fields"""
        required_fields = ["response", "confidence"]
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"

        assert isinstance(response["confidence"], (int, float)), "Confidence must be numeric"
        assert 0 <= response["confidence"] <= 1, "Confidence must be between 0 and 1"

        if "intent" in response:
            assert isinstance(response["intent"], str), "Intent must be a string"

        if "sentiment" in response:
            assert response["sentiment"] in ["positive", "negative", "neutral", "mixed"], \
                "Invalid sentiment value"

    @staticmethod
    def assert_valid_export_result(result: Dict[str, Any]):
        """Assert that an export result has all required fields"""
        required_fields = ["export_id", "status", "format", "record_count"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        assert result["status"] in ["queued", "processing", "completed", "failed"], \
            "Invalid export status"

        assert result["record_count"] >= 0, "Record count cannot be negative"

        if result["status"] == "completed":
            assert "file_size" in result, "Completed export must have file_size"
            assert "download_url" in result, "Completed export must have download_url"

    @staticmethod
    def assert_valid_backup_result(result: Dict[str, Any]):
        """Assert that a backup result has all required fields"""
        required_fields = ["backup_id", "status", "type", "size"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        assert result["status"] in ["running", "completed", "failed"], "Invalid backup status"
        assert result["type"] in ["full", "incremental"], "Invalid backup type"
        assert result["size"] > 0, "Backup size must be positive"

        if result["status"] == "completed":
            assert "checksum" in result, "Completed backup must have checksum"

    @staticmethod
    def assert_performance_threshold(duration: float, threshold: float, operation: str):
        """Assert that an operation meets performance requirements"""
        assert duration <= threshold, \
            f"{operation} exceeded performance threshold: {duration:.3f}s > {threshold}s"

    @staticmethod
    def assert_memory_usage(memory_mb: float, max_memory: float):
        """Assert that memory usage is within acceptable limits"""
        assert memory_mb <= max_memory, \
            f"Memory usage exceeded limit: {memory_mb:.1f}MB > {max_memory}MB"

    @staticmethod
    def assert_api_response_status(response, expected_status: int = 200):
        """Assert API response status"""
        assert response.status_code == expected_status, \
            f"Expected status {expected_status}, got {response.status_code}"

    @staticmethod
    def assert_api_response_contains(response, key: str, expected_value=None):
        """Assert API response contains specific data"""
        try:
            data = response.json()
        except:
            pytest.fail("Response is not valid JSON")

        assert key in data, f"Key '{key}' not found in response"
        if expected_value is not None:
            assert data[key] == expected_value, f"Expected {expected_value}, got {data[key]}"


class TestFixtureLoader:
    """Utility for loading test fixtures"""

    @staticmethod
    def load_json_fixture(filename: str) -> Dict[str, Any]:
        """Load a JSON fixture file"""
        fixture_path = f"tests/fixtures/{filename}"
        try:
            with open(fixture_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            pytest.fail(f"Fixture file not found: {fixture_path}")
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON in fixture file: {fixture_path}")

    @staticmethod
    def save_json_fixture(filename: str, data: Dict[str, Any]):
        """Save a JSON fixture file"""
        import os
        os.makedirs("tests/fixtures", exist_ok=True)
        fixture_path = f"tests/fixtures/{filename}"

        with open(fixture_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    @staticmethod
    def create_sample_dataset(name: str, size: int = 100) -> List[Dict[str, Any]]:
        """Create a sample dataset for testing"""
        if name == "users":
            return [TestDataFactory.generate_user_profile() for _ in range(size)]
        elif name == "conversations":
            return [TestDataFactory.generate_conversation() for _ in range(size)]
        elif name == "ai_requests":
            return [TestDataFactory.generate_ai_request() for _ in range(size)]
        else:
            return []


# Export all utilities
__all__ = [
    'TestDataFactory',
    'MockFactory',
    'AssertionHelpers',
    'TestFixtureLoader'
]