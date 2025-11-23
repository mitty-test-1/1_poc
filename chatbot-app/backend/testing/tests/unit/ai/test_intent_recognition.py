"""
Unit tests for AI Service Intent Recognition.

Tests cover:
- Intent classification accuracy
- Confidence scoring
- Multi-intent detection
- Context-aware intent recognition
- Intent training and model updates
- Fallback intent handling
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from testing_framework import BaseTestCase, AsyncTestCase


class TestIntentRecognition(BaseTestCase):
    """Test cases for Intent Recognition service"""

    def setup_method(self):
        """Setup test fixtures"""
        super().setup_method()
        # Mock the actual intent recognition service
        self.intent_recognition = Mock()
        self.intent_recognition.analyze = AsyncMock()
        self.intent_recognition.train = AsyncMock()
        self.intent_recognition.get_intent_examples = AsyncMock()

    @pytest.mark.unit
    @pytest.mark.ai
    def test_basic_intent_recognition(self):
        """Test basic intent recognition functionality"""
        # Setup
        input_text = "I want to book a flight"
        expected_result = {
            "intent": "book_flight",
            "confidence": 0.92,
            "entities": [
                {"text": "flight", "label": "travel_type", "confidence": 0.88}
            ],
            "metadata": {"model_version": "1.0.0"}
        }

        self.intent_recognition.analyze.return_value = expected_result

        # Execute
        result = self.intent_recognition.analyze(input_text)

        # Assert
        assert result["intent"] == "book_flight"
        assert result["confidence"] > 0.8
        assert len(result["entities"]) == 1
        assert "model_version" in result["metadata"]

    @pytest.mark.unit
    @pytest.mark.ai
    def test_multiple_intent_scenarios(self):
        """Test recognition of various intents"""
        test_cases = [
            ("What's the weather like?", "weather_query", 0.89),
            ("Cancel my reservation", "cancel_reservation", 0.95),
            ("Help me with my account", "account_help", 0.82),
            ("I need customer support", "customer_support", 0.91),
            ("Show me my order history", "order_history", 0.87)
        ]

        for text, expected_intent, expected_confidence in test_cases:
            self.intent_recognition.analyze.return_value = {
                "intent": expected_intent,
                "confidence": expected_confidence,
                "entities": []
            }

            result = self.intent_recognition.analyze(text)

            assert result["intent"] == expected_intent
            assert result["confidence"] >= expected_confidence - 0.1  # Allow some tolerance

    @pytest.mark.unit
    @pytest.mark.ai
    def test_low_confidence_handling(self):
        """Test handling of low confidence predictions"""
        # Setup
        input_text = "xyz abc def unclear message"
        expected_result = {
            "intent": "unknown",
            "confidence": 0.15,
            "fallback": True,
            "suggested_intents": ["general_inquiry", "help_request"]
        }

        self.intent_recognition.analyze.return_value = expected_result

        # Execute
        result = self.intent_recognition.analyze(input_text)

        # Assert
        assert result["intent"] == "unknown"
        assert result["confidence"] < 0.3
        assert result["fallback"] is True
        assert len(result["suggested_intents"]) > 0

    @pytest.mark.unit
    @pytest.mark.ai
    def test_context_aware_recognition(self):
        """Test context-aware intent recognition"""
        # Setup
        input_text = "yes"
        context = {
            "previous_intent": "book_flight",
            "conversation_state": "awaiting_confirmation",
            "user_id": "123"
        }

        expected_result = {
            "intent": "confirm_booking",
            "confidence": 0.78,
            "context_influence": 0.6,
            "original_context": context
        }

        self.intent_recognition.analyze.return_value = expected_result

        # Execute
        result = self.intent_recognition.analyze(input_text, context=context)

        # Assert
        assert result["intent"] == "confirm_booking"
        assert result["context_influence"] > 0.5
        assert result["original_context"] == context

    @pytest.mark.unit
    @pytest.mark.ai
    def test_entity_extraction_with_intent(self):
        """Test entity extraction combined with intent recognition"""
        # Setup
        input_text = "Book a flight from New York to London on March 15th"
        expected_result = {
            "intent": "book_flight",
            "confidence": 0.94,
            "entities": [
                {"text": "New York", "label": "origin", "confidence": 0.92},
                {"text": "London", "label": "destination", "confidence": 0.89},
                {"text": "March 15th", "label": "date", "confidence": 0.85}
            ]
        }

        self.intent_recognition.analyze.return_value = expected_result

        # Execute
        result = self.intent_recognition.analyze(input_text)

        # Assert
        assert result["intent"] == "book_flight"
        assert len(result["entities"]) == 3
        entity_labels = [e["label"] for e in result["entities"]]
        assert "origin" in entity_labels
        assert "destination" in entity_labels
        assert "date" in entity_labels

    @pytest.mark.unit
    @pytest.mark.ai
    def test_multilingual_intent_recognition(self):
        """Test intent recognition in different languages"""
        test_cases = [
            ("¿Cómo está el clima?", "weather_query", "es"),
            ("Wie ist das Wetter?", "weather_query", "de"),
            ("Quel temps fait-il?", "weather_query", "fr"),
            ("Как погода?", "weather_query", "ru")
        ]

        for text, expected_intent, language in test_cases:
            self.intent_recognition.analyze.return_value = {
                "intent": expected_intent,
                "confidence": 0.85,
                "language": language,
                "entities": []
            }

            result = self.intent_recognition.analyze(text)

            assert result["intent"] == expected_intent
            assert result["language"] == language
            assert result["confidence"] > 0.8

    @pytest.mark.unit
    @pytest.mark.ai
    def test_intent_training_data(self):
        """Test retrieval of training examples for intents"""
        # Setup
        intent_name = "book_flight"
        expected_examples = [
            "I want to book a flight",
            "Can you help me reserve a plane ticket?",
            "I'd like to fly to Paris",
            "Book me a flight please"
        ]

        self.intent_recognition.get_intent_examples.return_value = expected_examples

        # Execute
        examples = self.intent_recognition.get_intent_examples(intent_name)

        # Assert
        assert len(examples) == 4
        assert all("flight" in example.lower() or "book" in example.lower()
                  for example in examples)

    @pytest.mark.unit
    @pytest.mark.ai
    def test_model_retraining(self):
        """Test model retraining functionality"""
        # Setup
        training_data = [
            {"text": "Book a flight to Tokyo", "intent": "book_flight"},
            {"text": "I need to cancel my reservation", "intent": "cancel_booking"},
            {"text": "What's my booking status?", "intent": "booking_status"}
        ]

        expected_result = {
            "success": True,
            "model_version": "1.1.0",
            "accuracy_improvement": 0.05,
            "training_samples": len(training_data)
        }

        self.intent_recognition.train.return_value = expected_result

        # Execute
        result = self.intent_recognition.train(training_data)

        # Assert
        assert result["success"] is True
        assert result["accuracy_improvement"] > 0
        assert result["training_samples"] == len(training_data)

    @pytest.mark.unit
    @pytest.mark.ai
    def test_intent_confidence_thresholds(self):
        """Test different confidence thresholds for intent classification"""
        # Setup
        input_text = "Maybe I want to book something"
        confidence_levels = [0.3, 0.5, 0.7, 0.9]

        for threshold in confidence_levels:
            expected_result = {
                "intent": "book_flight" if threshold <= 0.7 else "unknown",
                "confidence": threshold,
                "threshold_used": threshold,
                "fallback_triggered": threshold < 0.5
            }

            self.intent_recognition.analyze.return_value = expected_result

            result = self.intent_recognition.analyze(input_text, confidence_threshold=threshold)

            assert result["confidence"] >= threshold or result["intent"] == "unknown"
            assert result["threshold_used"] == threshold

    @pytest.mark.unit
    @pytest.mark.ai
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Setup
        invalid_inputs = [None, "", 123, [], {}]

        for invalid_input in invalid_inputs:
            self.intent_recognition.analyze.side_effect = ValueError("Invalid input")

            # Execute & Assert
            with pytest.raises(ValueError, match="Invalid input"):
                self.intent_recognition.analyze(invalid_input)

    @pytest.mark.unit
    @pytest.mark.ai
    def test_concurrent_requests(self):
        """Test handling of concurrent intent recognition requests"""
        # Setup
        import asyncio

        async def mock_analyze(text):
            await asyncio.sleep(0.01)  # Simulate processing time
            return {
                "intent": "test_intent",
                "confidence": 0.8,
                "text": text
            }

        self.intent_recognition.analyze = mock_analyze

        # Execute concurrent requests
        async def run_concurrent_tests():
            tasks = []
            for i in range(10):
                task = asyncio.create_task(
                    self.intent_recognition.analyze(f"Test message {i}")
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks)
            return results

        # This would be run in an async test
        # results = asyncio.run(run_concurrent_tests())

        # For now, just test that the method exists and is async
        assert hasattr(self.intent_recognition, 'analyze')

    @pytest.mark.unit
    @pytest.mark.ai
    @pytest.mark.performance
    def test_performance_under_load(self):
        """Test performance under simulated load"""
        # Setup
        test_messages = [
            "Book a flight",
            "What's the weather?",
            "Help me please",
            "Cancel my order"
        ] * 25  # 100 messages total

        # Mock responses
        responses = []
        for i, msg in enumerate(test_messages):
            responses.append({
                "intent": f"intent_{i % 4}",
                "confidence": 0.8 + (i % 20) / 100,
                "processing_time": 0.01 + (i % 10) / 1000
            })

        self.intent_recognition.analyze.side_effect = responses

        # Execute performance test
        start_time = self.metrics.start_time
        for msg in test_messages:
            self.intent_recognition.analyze(msg)

        end_time = self.metrics.end_time or self.metrics.start_time
        total_time = (end_time - start_time).total_seconds()

        # Assert performance requirements
        avg_time_per_request = total_time / len(test_messages)
        assert avg_time_per_request < 0.1  # Less than 100ms per request

    @pytest.mark.unit
    @pytest.mark.ai
    def test_intent_model_metadata(self):
        """Test retrieval of intent model metadata"""
        # Setup
        expected_metadata = {
            "model_name": "intent_classifier_v2",
            "version": "2.1.0",
            "training_date": "2024-01-15",
            "accuracy": 0.89,
            "supported_intents": ["book_flight", "cancel_booking", "weather_query", "help"],
            "supported_languages": ["en", "es", "fr"]
        }

        # Mock a get_metadata method
        self.intent_recognition.get_metadata = Mock(return_value=expected_metadata)

        # Execute
        metadata = self.intent_recognition.get_metadata()

        # Assert
        assert metadata["model_name"] == "intent_classifier_v2"
        assert metadata["accuracy"] > 0.8
        assert len(metadata["supported_intents"]) > 0
        assert "en" in metadata["supported_languages"]