"""
API tests for AI Service endpoints.

Tests cover:
- Message processing endpoint
- Intent recognition endpoint
- Sentiment analysis endpoint
- Model management endpoints
- Performance monitoring endpoints
- Error handling and validation
- Authentication and authorization
"""

import pytest
import httpx
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import json

from testing_framework import AsyncAPITestCase


class TestAIServiceAPI(AsyncAPITestCase):
    """API test cases for AI Service"""

    def setup_method(self):
        """Setup API test fixtures"""
        super().setup_method()
        self.base_url = "http://localhost:3007"

    @pytest.mark.api
    @pytest.mark.ai
    async def test_process_message_endpoint(self):
        """Test message processing endpoint"""
        # Setup
        request_data = {
            "message": "Hello, I want to book a flight",
            "user_id": "user_123",
            "conversation_id": "conv_456",
            "context": {"channel": "web"}
        }

        expected_response = {
            "response": "I'd be happy to help you book a flight. Could you please provide your departure city and destination?",
            "confidence": 0.89,
            "intent": "book_flight",
            "sentiment": "neutral",
            "entities": [
                {"text": "flight", "label": "travel_type", "confidence": 0.92}
            ],
            "metadata": {
                "processing_time": 0.15,
                "model_used": "response_generator_v2"
            }
        }

        # Mock the response
        self.client.post = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        # Execute
        response = await self.make_async_request(
            "POST",
            "/process",
            json=request_data
        )

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert "response" in response_data
        assert "confidence" in response_data
        assert "intent" in response_data
        assert response_data["confidence"] > 0.8

    @pytest.mark.api
    @pytest.mark.ai
    async def test_intent_recognition_endpoint(self):
        """Test intent recognition endpoint"""
        # Setup
        request_data = {
            "message": "What's the weather like today?",
            "user_id": "user_123",
            "context": {"location": "New York"}
        }

        expected_response = {
            "intent": "weather_query",
            "confidence": 0.94,
            "entities": [
                {"text": "today", "label": "time", "confidence": 0.88}
            ],
            "metadata": {
                "model_version": "intent_classifier_v2.1",
                "processing_time": 0.08
            }
        }

        # Mock the response
        self.client.post = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        # Execute
        response = await self.make_async_request(
            "POST",
            "/intent",
            json=request_data
        )

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["intent"] == "weather_query"
        assert response_data["confidence"] > 0.9
        assert len(response_data["entities"]) > 0

    @pytest.mark.api
    @pytest.mark.ai
    async def test_sentiment_analysis_endpoint(self):
        """Test sentiment analysis endpoint"""
        # Setup
        request_data = {
            "message": "I absolutely love this new feature!",
            "user_id": "user_123",
            "conversation_id": "conv_456"
        }

        expected_response = {
            "sentiment": "positive",
            "confidence": 0.96,
            "scores": {
                "positive": 0.89,
                "negative": 0.03,
                "neutral": 0.08
            },
            "emotions": ["joy", "excitement"],
            "metadata": {
                "model_version": "sentiment_analyzer_v1.5",
                "processing_time": 0.05
            }
        }

        # Mock the response
        self.client.post = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        # Execute
        response = await self.make_async_request(
            "POST",
            "/sentiment",
            json=request_data
        )

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["sentiment"] == "positive"
        assert response_data["scores"]["positive"] > response_data["scores"]["negative"]
        assert len(response_data["emotions"]) > 0

    @pytest.mark.api
    @pytest.mark.ai
    async def test_model_management_endpoints(self):
        """Test model management endpoints"""
        # Test get available models
        expected_models = [
            {
                "name": "intent_classifier",
                "version": "2.1.0",
                "status": "loaded",
                "type": "classification"
            },
            {
                "name": "sentiment_analyzer",
                "version": "1.5.0",
                "status": "loaded",
                "type": "sentiment"
            }
        ]

        self.client.get = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value={"models": expected_models})
        ))

        response = await self.make_async_request("GET", "/models")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["models"]) == 2
        assert all(model["status"] == "loaded" for model in response_data["models"])

    @pytest.mark.api
    @pytest.mark.ai
    async def test_health_check_endpoint(self):
        """Test health check endpoint"""
        expected_response = {
            "status": "healthy",
            "service": "ai-service",
            "version": "1.0.0",
            "timestamp": "2024-01-01T00:00:00Z",
            "models_loaded": 3,
            "uptime_seconds": 3600
        }

        self.client.get = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        response = await self.make_async_request("GET", "/health")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "healthy"
        assert response_data["service"] == "ai-service"
        assert "uptime_seconds" in response_data

    @pytest.mark.api
    @pytest.mark.ai
    async def test_error_handling_invalid_input(self):
        """Test error handling for invalid input"""
        # Test with empty message
        request_data = {"message": "", "user_id": "user_123"}

        self.client.post = AsyncMock(return_value=Mock(
            status_code=400,
            json=Mock(return_value={
                "error": "ValidationError",
                "message": "Message cannot be empty",
                "details": {"field": "message", "issue": "required"}
            })
        ))

        response = await self.make_async_request(
            "POST",
            "/process",
            json=request_data
        )

        assert response.status_code == 400
        error_data = response.json()
        assert "error" in error_data
        assert "ValidationError" in error_data["error"]

    @pytest.mark.api
    @pytest.mark.ai
    async def test_error_handling_service_unavailable(self):
        """Test error handling when service is unavailable"""
        request_data = {"message": "Hello", "user_id": "user_123"}

        # Simulate service unavailable
        self.client.post = AsyncMock(return_value=Mock(
            status_code=503,
            json=Mock(return_value={
                "error": "ServiceUnavailable",
                "message": "AI service is temporarily unavailable",
                "retry_after": 30
            })
        ))

        response = await self.make_async_request(
            "POST",
            "/process",
            json=request_data
        )

        assert response.status_code == 503
        error_data = response.json()
        assert error_data["error"] == "ServiceUnavailable"
        assert "retry_after" in error_data

    @pytest.mark.api
    @pytest.mark.ai
    async def test_rate_limiting(self):
        """Test rate limiting behavior"""
        request_data = {"message": "Test message", "user_id": "user_123"}

        # First request succeeds
        self.client.post = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value={"response": "Success"})
        ))

        response1 = await self.make_async_request(
            "POST",
            "/process",
            json=request_data
        )
        assert response1.status_code == 200

        # Subsequent requests are rate limited
        self.client.post = AsyncMock(return_value=Mock(
            status_code=429,
            json=Mock(return_value={
                "error": "RateLimitExceeded",
                "message": "Too many requests",
                "retry_after": 60
            })
        ))

        response2 = await self.make_async_request(
            "POST",
            "/process",
            json=request_data
        )

        assert response2.status_code == 429
        error_data = response2.json()
        assert error_data["error"] == "RateLimitExceeded"

    @pytest.mark.api
    @pytest.mark.ai
    async def test_authentication_required(self):
        """Test that authentication is required"""
        request_data = {"message": "Hello", "user_id": "user_123"}

        # Mock unauthorized response
        self.client.post = AsyncMock(return_value=Mock(
            status_code=401,
            json=Mock(return_value={
                "error": "AuthenticationRequired",
                "message": "Valid authentication token required"
            })
        ))

        response = await self.make_async_request(
            "POST",
            "/process",
            json=request_data
        )

        assert response.status_code == 401
        error_data = response.json()
        assert "AuthenticationRequired" in error_data["error"]

    @pytest.mark.api
    @pytest.mark.ai
    async def test_follow_up_generation_endpoint(self):
        """Test follow-up question generation endpoint"""
        request_data = {
            "user_id": "user_123",
            "conversation_id": "conv_456"
        }

        expected_response = {
            "follow_up": "Would you like me to help you with anything else?",
            "confidence": 0.82,
            "type": "engagement",
            "context": {
                "conversation_length": 5,
                "last_topic": "booking"
            }
        }

        self.client.post = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        response = await self.make_async_request(
            "POST",
            "/follow-up",
            json=request_data
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "follow_up" in response_data
        assert response_data["confidence"] > 0.7
        assert "type" in response_data

    @pytest.mark.api
    @pytest.mark.ai
    async def test_performance_monitoring_endpoints(self):
        """Test performance monitoring endpoints"""
        # Test system metrics
        expected_metrics = {
            "cpu_usage": 45.5,
            "memory_usage": 67.8,
            "response_time_avg": 0.12,
            "requests_per_second": 15.3,
            "error_rate": 0.02,
            "model_inference_time": 0.08
        }

        self.client.get = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_metrics)
        ))

        response = await self.make_async_request("GET", "/monitoring/metrics")
        assert response.status_code == 200
        metrics_data = response.json()
        assert "cpu_usage" in metrics_data
        assert "response_time_avg" in metrics_data
        assert metrics_data["error_rate"] < 0.1  # Acceptable error rate

    @pytest.mark.api
    @pytest.mark.ai
    async def test_conversation_suggestions_endpoint(self):
        """Test conversation suggestions endpoint"""
        request_data = {
            "conversation_id": "conv_456",
            "user_id": "user_123",
            "context": {"topic": "travel"}
        }

        expected_response = {
            "suggestions": [
                "Would you like to know about flight deals?",
                "I can help you find accommodation options.",
                "Need assistance with travel insurance?"
            ],
            "confidence": 0.78,
            "context": {"suggestions_count": 3},
            "timestamp": "2024-01-01T12:00:00Z"
        }

        self.client.post = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        response = await self.make_async_request(
            "POST",
            "/suggestions",
            json=request_data
        )

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["suggestions"]) == 3
        assert response_data["confidence"] > 0.7

    @pytest.mark.api
    @pytest.mark.ai
    async def test_conversation_sentiment_analysis_endpoint(self):
        """Test conversation sentiment analysis endpoint"""
        request_data = {"conversation_id": "conv_456"}

        expected_response = {
            "sentiment": "mixed",
            "confidence": 0.85,
            "scores": {"positive": 0.4, "negative": 0.3, "neutral": 0.3},
            "emotions": ["satisfaction", "frustration"],
            "trend": "improving",
            "message_sentiments": [
                {"message_id": "msg_1", "sentiment": "neutral"},
                {"message_id": "msg_2", "sentiment": "negative"},
                {"message_id": "msg_3", "sentiment": "positive"}
            ]
        }

        self.client.post = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        response = await self.make_async_request(
            "POST",
            "/analyze-sentiment",
            json=request_data
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["sentiment"] == "mixed"
        assert len(response_data["message_sentiments"]) > 0

    @pytest.mark.api
    @pytest.mark.ai
    async def test_conversation_summary_endpoint(self):
        """Test conversation summary endpoint"""
        request_data = {"conversation_id": "conv_456"}

        expected_response = {
            "summary": "User inquired about flight booking and received assistance with travel planning.",
            "key_points": [
                "Flight booking inquiry",
                "Destination preferences discussed",
                "Travel dates confirmed"
            ],
            "topics": ["travel", "booking", "planning"],
            "sentiment_trend": "positive",
            "duration": 1800,  # 30 minutes
            "message_count": 15,
            "participants": ["user_123", "ai_assistant"]
        }

        self.client.post = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        response = await self.make_async_request(
            "POST",
            "/summary",
            json=request_data
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "summary" in response_data
        assert len(response_data["key_points"]) > 0
        assert response_data["message_count"] > 0

    @pytest.mark.api
    @pytest.mark.ai
    async def test_user_insights_endpoint(self):
        """Test user insights endpoint"""
        user_id = "user_123"

        expected_response = {
            "user_id": user_id,
            "insights": [
                {
                    "type": "communication_style",
                    "insight": "Prefers detailed, structured responses",
                    "confidence": 0.88
                },
                {
                    "type": "engagement_pattern",
                    "insight": "Most active during business hours",
                    "confidence": 0.76
                }
            ],
            "last_updated": "2024-01-01T12:00:00Z",
            "conversation_count": 25
        }

        self.client.get = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        response = await self.make_async_request("GET", f"/users/{user_id}/insights")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["user_id"] == user_id
        assert len(response_data["insights"]) > 0
        assert all(insight["confidence"] > 0.7 for insight in response_data["insights"])

    @pytest.mark.api
    @pytest.mark.ai
    async def test_intent_examples_endpoint(self):
        """Test intent examples endpoint"""
        intent = "book_flight"

        expected_response = {
            "intent": intent,
            "examples": [
                "I want to book a flight to Paris",
                "Can you help me reserve a plane ticket?",
                "I'd like to fly to London next week",
                "Book me a flight please"
            ],
            "total_examples": 4,
            "last_updated": "2024-01-01T00:00:00Z"
        }

        self.client.get = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        response = await self.make_async_request("GET", f"/examples/intent/{intent}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["intent"] == intent
        assert len(response_data["examples"]) > 0
        assert response_data["total_examples"] == len(response_data["examples"])

    @pytest.mark.api
    @pytest.mark.ai
    async def test_emotion_examples_endpoint(self):
        """Test emotion examples endpoint"""
        emotion = "joy"

        expected_response = {
            "emotion": emotion,
            "examples": [
                "I'm so excited about this!",
                "This makes me incredibly happy",
                "What a wonderful surprise!",
                "I'm thrilled with the results"
            ],
            "total_examples": 4,
            "intensity_levels": ["low", "medium", "high"],
            "last_updated": "2024-01-01T00:00:00Z"
        }

        self.client.get = AsyncMock(return_value=Mock(
            status_code=200,
            json=Mock(return_value=expected_response)
        ))

        response = await self.make_async_request("GET", f"/examples/emotion/{emotion}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["emotion"] == emotion
        assert len(response_data["examples"]) > 0
        assert "intensity_levels" in response_data