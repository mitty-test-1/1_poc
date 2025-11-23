"""
Pytest configuration and global fixtures for chatbot backend testing.

This file contains pytest configuration, global fixtures, and test setup
that is shared across all test modules.
"""

import pytest
import asyncio
import os
import sys
from typing import Dict, Any, Generator
from pathlib import Path

# Add the testing framework to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from testing_framework import (
    TestConfig,
    TestEnvironment,
    ServiceType,
    TestDataGenerator,
    TestFixtureManager,
    MockService,
    AIServiceTestUtils,
    DataServiceTestUtils,
    PersonalizationServiceTestUtils
)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "ai: AI service tests")
    config.addinivalue_line("markers", "data: Data service tests")
    config.addinivalue_line("markers", "personalization: Personalization service tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file paths"""
    for item in items:
        # Add service markers based on file path
        if "test_ai" in str(item.fspath):
            item.add_marker(pytest.mark.ai)
        elif "test_data" in str(item.fspath):
            item.add_marker(pytest.mark.data)
        elif "test_personalization" in str(item.fspath):
            item.add_marker(pytest.mark.personalization)

        # Add test type markers based on file naming
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        else:
            item.add_marker(pytest.mark.unit)


# Global fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """Global test configuration fixture"""
    config = TestConfig()

    # Set configuration based on environment variables
    config.base_url = os.getenv("TEST_BASE_URL", "http://localhost:3000")
    config.enable_coverage = os.getenv("TEST_COVERAGE", "true").lower() == "true"
    config.mock_external_services = os.getenv("TEST_MOCK_EXTERNAL", "true").lower() == "true"
    config.enable_performance_monitoring = os.getenv("TEST_PERFORMANCE", "false").lower() == "true"

    # Set test environment based on pytest markers
    test_env = os.getenv("TEST_ENVIRONMENT", "unit")
    if test_env == "integration":
        config.environment = TestEnvironment.INTEGRATION
    elif test_env == "api":
        config.environment = TestEnvironment.API
    elif test_env == "performance":
        config.environment = TestEnvironment.PERFORMANCE
    elif test_env == "e2e":
        config.environment = TestEnvironment.E2E
    else:
        config.environment = TestEnvironment.UNIT

    return config


@pytest.fixture(scope="session")
def test_data_generator():
    """Global test data generator fixture"""
    return TestDataGenerator()


@pytest.fixture(scope="session")
def fixture_manager():
    """Global fixture manager fixture"""
    fixtures_path = Path(__file__).parent / "tests" / "fixtures"
    return TestFixtureManager(str(fixtures_path))


@pytest.fixture(scope="session")
def mock_services():
    """Global mock services fixture"""
    return {
        "ai": MockService(ServiceType.AI),
        "data": MockService(ServiceType.DATA),
        "personalization": MockService(ServiceType.PERSONALIZATION),
        "auth": MockService(ServiceType.AUTH),
        "chat": MockService(ServiceType.CHAT),
        "gateway": MockService(ServiceType.GATEWAY)
    }


@pytest.fixture
def ai_test_utils():
    """AI service test utilities fixture"""
    return AIServiceTestUtils()


@pytest.fixture
def data_test_utils():
    """Data service test utilities fixture"""
    return DataServiceTestUtils()


@pytest.fixture
def personalization_test_utils():
    """Personalization service test utilities fixture"""
    return PersonalizationServiceTestUtils()


@pytest.fixture
def sample_user(test_data_generator):
    """Sample user data fixture"""
    return test_data_generator.generate_user_profile()


@pytest.fixture
def sample_conversation(test_data_generator):
    """Sample conversation data fixture"""
    return {
        "conversation_id": test_data_generator.generate_conversation_id(),
        "user_id": test_data_generator.generate_user_id(),
        "messages": [
            test_data_generator.generate_message(),
            test_data_generator.generate_message(),
            test_data_generator.generate_message()
        ],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_ai_request(test_data_generator):
    """Sample AI request data fixture"""
    return test_data_generator.generate_ai_request()


@pytest.fixture
def sample_export_request():
    """Sample export request data fixture"""
    return {
        "export_type": "conversations",
        "format": "json",
        "filters": {
            "date_from": "2024-01-01",
            "date_to": "2024-01-31"
        },
        "include_metadata": True,
        "compression": False
    }


@pytest.fixture
def sample_backup_request():
    """Sample backup request data fixture"""
    return {
        "backup_type": "full",
        "include_data": True,
        "include_config": True,
        "retention_days": 30
    }


@pytest.fixture
def sample_user_profile():
    """Sample user profile data fixture"""
    return {
        "user_id": "user_123",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "preferences": {
            "language": "en",
            "theme": "light",
            "notifications": True
        },
        "behavioral_traits": {
            "engagement_level": "high",
            "communication_style": "formal",
            "response_preference": "detailed"
        },
        "engagement_metrics": {
            "total_conversations": 25,
            "average_session_length": 15.5,
            "last_active": "2024-01-15T10:30:00Z"
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }


@pytest.fixture
def sample_segment():
    """Sample user segment data fixture"""
    return {
        "segment_id": "segment_001",
        "name": "High Engagement Users",
        "description": "Users with high engagement metrics",
        "user_count": 150,
        "criteria": {
            "engagement_score": {"gt": 0.8},
            "session_count": {"gt": 10}
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_ab_test():
    """Sample A/B test data fixture"""
    return {
        "test_name": "response_length_test",
        "description": "Test different response lengths",
        "variants": [
            {"name": "short", "weight": 0.5, "config": {"max_length": 100}},
            {"name": "long", "weight": 0.5, "config": {"max_length": 500}}
        ],
        "target_audience": {
            "segment_ids": ["segment_001"],
            "user_count": 1000
        },
        "metrics": ["response_time", "user_satisfaction", "completion_rate"],
        "duration_days": 14,
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_redis():
    """Mock Redis client fixture"""
    from unittest.mock import Mock
    redis_mock = Mock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = 1
    redis_mock.exists.return_value = 0
    return redis_mock


@pytest.fixture
def mock_database():
    """Mock database connection fixture"""
    from unittest.mock import Mock, AsyncMock
    db_mock = Mock()
    db_mock.execute = AsyncMock(return_value=None)
    db_mock.fetchone = AsyncMock(return_value=None)
    db_mock.fetchall = AsyncMock(return_value=[])
    db_mock.commit = AsyncMock(return_value=None)
    return db_mock


@pytest.fixture
def mock_http_client():
    """Mock HTTP client fixture"""
    from unittest.mock import Mock, AsyncMock
    http_mock = Mock()
    http_mock.get = AsyncMock()
    http_mock.post = AsyncMock()
    http_mock.put = AsyncMock()
    http_mock.delete = AsyncMock()
    return http_mock


@pytest.fixture
def mock_external_api():
    """Mock external API fixture"""
    from unittest.mock import Mock, AsyncMock
    api_mock = Mock()
    api_mock.call = AsyncMock(return_value={"status": "success"})
    api_mock.authenticate = AsyncMock(return_value={"token": "mock_token"})
    return api_mock


@pytest.fixture
def temp_directory(tmp_path):
    """Temporary directory fixture"""
    return tmp_path


@pytest.fixture
def test_logger():
    """Test logger fixture"""
    import logging
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    yield logger

    # Clean up
    logger.removeHandler(handler)


# Environment setup fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    # Set test environment variables
    os.environ.setdefault("TESTING", "true")
    os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
    os.environ.setdefault("JWT_SECRET", "test_jwt_secret_key_for_testing_only")

    yield

    # Cleanup can be added here if needed


@pytest.fixture(scope="session", autouse=True)
def setup_asyncio_event_loop():
    """Setup asyncio event loop for the test session"""
    # This fixture ensures we have a proper event loop for async tests
    pass


# Performance monitoring fixtures
@pytest.fixture
def performance_monitor():
    """Performance monitor fixture"""
    from testing_framework import PerformanceTestCase
    return PerformanceTestCase()


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield

    # Add any cleanup logic here
    # For example: clean up temporary files, reset mocks, etc.


# Service-specific fixtures
@pytest.fixture
def ai_service_config(test_config):
    """AI service specific configuration"""
    config = test_config
    config.service_type = ServiceType.AI
    config.base_url = os.getenv("AI_SERVICE_URL", "http://localhost:3007")
    return config


@pytest.fixture
def data_service_config(test_config):
    """Data service specific configuration"""
    config = test_config
    config.service_type = ServiceType.DATA
    config.base_url = os.getenv("DATA_SERVICE_URL", "http://localhost:3006")
    return config


@pytest.fixture
def personalization_service_config(test_config):
    """Personalization service specific configuration"""
    config = test_config
    config.service_type = ServiceType.PERSONALIZATION
    config.base_url = os.getenv("PERSONALIZATION_SERVICE_URL", "http://localhost:3005")
    return config


@pytest.fixture
def auth_service_config(test_config):
    """Auth service specific configuration"""
    config = test_config
    config.service_type = ServiceType.AUTH
    config.base_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:3004")
    return config


@pytest.fixture
def chat_service_config(test_config):
    """Chat service specific configuration"""
    config = test_config
    config.service_type = ServiceType.CHAT
    config.base_url = os.getenv("CHAT_SERVICE_URL", "http://localhost:3003")
    return config


@pytest.fixture
def gateway_service_config(test_config):
    """Gateway service specific configuration"""
    config = test_config
    config.service_type = ServiceType.GATEWAY
    config.base_url = os.getenv("GATEWAY_SERVICE_URL", "http://localhost:3000")
    return config


# Test data fixtures for different scenarios
@pytest.fixture
def large_conversation_dataset(test_data_generator):
    """Large conversation dataset for performance testing"""
    conversations = []
    for i in range(1000):
        conversation = {
            "conversation_id": f"conv_{i:04d}",
            "user_id": f"user_{i % 100:03d}",
            "messages": [
                test_data_generator.generate_message() for _ in range(10)
            ],
            "created_at": "2024-01-01T00:00:00Z",
            "metadata": {"test_data": True}
        }
        conversations.append(conversation)
    return conversations


@pytest.fixture
def diverse_user_profiles():
    """Diverse user profiles for testing personalization"""
    return [
        {
            "user_id": "user_001",
            "behavioral_traits": {"engagement_level": "high", "communication_style": "formal"},
            "preferences": {"language": "en", "response_length": "detailed"}
        },
        {
            "user_id": "user_002",
            "behavioral_traits": {"engagement_level": "medium", "communication_style": "casual"},
            "preferences": {"language": "es", "response_length": "brief"}
        },
        {
            "user_id": "user_003",
            "behavioral_traits": {"engagement_level": "low", "communication_style": "technical"},
            "preferences": {"language": "fr", "response_length": "comprehensive"}
        }
    ]


@pytest.fixture
def mock_ml_models():
    """Mock ML models for testing"""
    from unittest.mock import Mock

    # Mock NLP model
    nlp_model = Mock()
    nlp_model.process.return_value = {
        "entities": [{"text": "test", "label": "MISC", "confidence": 0.95}],
        "tokens": ["Hello", "world"],
        "sentiment": "positive"
    }

    # Mock intent classifier
    intent_model = Mock()
    intent_model.predict.return_value = {
        "intent": "greeting",
        "confidence": 0.89
    }

    # Mock sentiment analyzer
    sentiment_model = Mock()
    sentiment_model.analyze.return_value = {
        "sentiment": "positive",
        "confidence": 0.92,
        "scores": {"positive": 0.8, "negative": 0.1, "neutral": 0.1}
    }

    return {
        "nlp": nlp_model,
        "intent": intent_model,
        "sentiment": sentiment_model
    }


# Export fixtures for use in test modules
__all__ = [
    'test_config',
    'test_data_generator',
    'fixture_manager',
    'mock_services',
    'ai_test_utils',
    'data_test_utils',
    'personalization_test_utils',
    'sample_user',
    'sample_conversation',
    'sample_ai_request',
    'sample_export_request',
    'sample_backup_request',
    'sample_user_profile',
    'sample_segment',
    'sample_ab_test',
    'mock_redis',
    'mock_database',
    'mock_http_client',
    'mock_external_api',
    'temp_directory',
    'test_logger',
    'performance_monitor',
    'ai_service_config',
    'data_service_config',
    'personalization_service_config',
    'auth_service_config',
    'chat_service_config',
    'gateway_service_config',
    'large_conversation_dataset',
    'diverse_user_profiles',
    'mock_ml_models'
]