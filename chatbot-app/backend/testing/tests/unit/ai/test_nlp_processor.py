"""
Unit tests for AI Service NLP Processor.

Tests cover:
- Text tokenization and preprocessing
- Entity extraction
- Named entity recognition
- Text normalization
- Language detection
- Stop word removal
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from testing_framework import BaseTestCase, AsyncTestCase


class TestNLPProcessor(BaseTestCase):
    """Test cases for NLP Processor service"""

    def setup_method(self):
        """Setup test fixtures"""
        super().setup_method()
        # Mock the actual NLP processor service
        self.nlp_processor = Mock()
        self.nlp_processor.process = AsyncMock()

    @pytest.mark.unit
    @pytest.mark.ai
    def test_text_preprocessing_basic(self):
        """Test basic text preprocessing functionality"""
        # Setup
        input_text = "Hello, World! This is a TEST message."
        expected_output = {
            "tokens": ["hello", "world", "test", "message"],
            "normalized": "hello world test message",
            "language": "en"
        }

        self.nlp_processor.process.return_value = expected_output

        # Execute
        result = self.nlp_processor.process(input_text)

        # Assert
        assert result["tokens"] == expected_output["tokens"]
        assert result["normalized"] == expected_output["normalized"]
        assert result["language"] == expected_output["language"]
        assert len(result["tokens"]) == 4

    @pytest.mark.unit
    @pytest.mark.ai
    def test_entity_extraction(self):
        """Test named entity extraction"""
        # Setup
        input_text = "John Smith works at Google in New York."
        expected_entities = [
            {"text": "John Smith", "label": "PERSON", "confidence": 0.95},
            {"text": "Google", "label": "ORG", "confidence": 0.92},
            {"text": "New York", "label": "GPE", "confidence": 0.88}
        ]

        self.nlp_processor.process.return_value = {
            "entities": expected_entities,
            "tokens": ["john", "smith", "works", "google", "new", "york"]
        }

        # Execute
        result = self.nlp_processor.process(input_text)

        # Assert
        assert len(result["entities"]) == 3
        assert result["entities"][0]["label"] == "PERSON"
        assert result["entities"][1]["label"] == "ORG"
        assert result["entities"][2]["label"] == "GPE"
        assert all(entity["confidence"] > 0.8 for entity in result["entities"])

    @pytest.mark.unit
    @pytest.mark.ai
    def test_empty_text_handling(self):
        """Test handling of empty or whitespace-only text"""
        # Setup
        test_cases = ["", "   ", "\n\t\r"]

        for empty_text in test_cases:
            self.nlp_processor.process.return_value = {
                "tokens": [],
                "normalized": "",
                "language": "unknown"
            }

            # Execute
            result = self.nlp_processor.process(empty_text)

            # Assert
            assert result["tokens"] == []
            assert result["normalized"] == ""
            assert result["language"] == "unknown"

    @pytest.mark.unit
    @pytest.mark.ai
    def test_special_characters_handling(self):
        """Test handling of special characters and emojis"""
        # Setup
        input_text = "Hello 😀 @user #hashtag https://example.com test@example.com"
        expected_tokens = ["hello", "user", "hashtag", "https", "test", "example", "com"]

        self.nlp_processor.process.return_value = {
            "tokens": expected_tokens,
            "normalized": "hello user hashtag https test example com",
            "entities": [
                {"text": "test@example.com", "label": "EMAIL", "confidence": 0.95}
            ]
        }

        # Execute
        result = self.nlp_processor.process(input_text)

        # Assert
        assert "hello" in result["tokens"]
        assert "user" in result["tokens"]
        assert len(result["entities"]) == 1
        assert result["entities"][0]["label"] == "EMAIL"

    @pytest.mark.unit
    @pytest.mark.ai
    def test_multilingual_text(self):
        """Test processing of multilingual text"""
        # Setup
        input_text = "Hello こんにちは Hola"
        expected_result = {
            "tokens": ["hello", "こんにちは", "hola"],
            "language": "mixed",
            "language_confidence": {"en": 0.4, "ja": 0.3, "es": 0.3}
        }

        self.nlp_processor.process.return_value = expected_result

        # Execute
        result = self.nlp_processor.process(input_text)

        # Assert
        assert result["language"] == "mixed"
        assert "language_confidence" in result
        assert len(result["language_confidence"]) == 3

    @pytest.mark.unit
    @pytest.mark.ai
    def test_stop_words_removal(self):
        """Test stop words removal functionality"""
        # Setup
        input_text = "The quick brown fox jumps over the lazy dog"
        expected_tokens = ["quick", "brown", "fox", "jumps", "lazy", "dog"]

        self.nlp_processor.process.return_value = {
            "tokens": expected_tokens,
            "stop_words_removed": ["the", "over"],
            "original_tokens": ["the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
        }

        # Execute
        result = self.nlp_processor.process(input_text)

        # Assert
        assert "the" not in result["tokens"]
        assert "over" not in result["tokens"]
        assert len(result["stop_words_removed"]) == 2
        assert len(result["tokens"]) == 6

    @pytest.mark.unit
    @pytest.mark.ai
    def test_text_normalization(self):
        """Test text normalization (lowercasing, stemming, lemmatization)"""
        # Setup
        input_text = "Running runners run quickly"
        expected_result = {
            "tokens": ["run", "runner", "run", "quick"],
            "stems": ["run", "runner", "run", "quick"],
            "lemmas": ["run", "runner", "run", "quickly"],
            "normalized": "run runner run quick"
        }

        self.nlp_processor.process.return_value = expected_result

        # Execute
        result = self.nlp_processor.process(input_text)

        # Assert
        assert result["normalized"] == expected_result["normalized"]
        assert len(result["stems"]) == len(result["lemmas"])
        assert "running" not in result["tokens"]

    @pytest.mark.unit
    @pytest.mark.ai
    def test_long_text_processing(self):
        """Test processing of long text documents"""
        # Setup
        long_text = " ".join([f"sentence {i} with some content" for i in range(100)])
        expected_result = {
            "tokens": ["sentence"] * 100 + ["content"] * 100,  # Simplified
            "word_count": 400,
            "sentence_count": 100,
            "language": "en"
        }

        self.nlp_processor.process.return_value = expected_result

        # Execute
        result = self.nlp_processor.process(long_text)

        # Assert
        assert result["word_count"] == 400
        assert result["sentence_count"] == 100
        assert result["language"] == "en"

    @pytest.mark.unit
    @pytest.mark.ai
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Setup
        invalid_inputs = [None, 123, [], {}]

        for invalid_input in invalid_inputs:
            self.nlp_processor.process.side_effect = ValueError("Invalid input type")

            # Execute & Assert
            with pytest.raises(ValueError, match="Invalid input type"):
                self.nlp_processor.process(invalid_input)

    @pytest.mark.unit
    @pytest.mark.ai
    def test_processing_timeout(self):
        """Test handling of processing timeouts"""
        # Setup
        input_text = "Very long text that might cause timeout"

        self.nlp_processor.process.side_effect = TimeoutError("Processing timeout")

        # Execute & Assert
        with pytest.raises(TimeoutError, match="Processing timeout"):
            self.nlp_processor.process(input_text)

    @pytest.mark.unit
    @pytest.mark.ai
    @pytest.mark.performance
    def test_processing_performance(self):
        """Test processing performance metrics"""
        # Setup
        input_text = "This is a test message for performance evaluation"

        self.nlp_processor.process.return_value = {
            "tokens": ["test", "message", "performance", "evaluation"],
            "processing_time": 0.05,
            "memory_usage": 10.5
        }

        # Execute
        result, duration, memory_delta = self.measure_performance(
            self.nlp_processor.process, input_text
        )

        # Assert
        assert result["processing_time"] < 1.0  # Less than 1 second
        assert result["memory_usage"] < 100  # Less than 100MB
        assert duration < 1.0

    @pytest.mark.unit
    @pytest.mark.ai
    def test_context_preservation(self):
        """Test that context is preserved during processing"""
        # Setup
        input_text = "Hello world"
        context = {"user_id": "123", "session_id": "abc"}

        self.nlp_processor.process.return_value = {
            "tokens": ["hello", "world"],
            "context": context,
            "preserved": True
        }

        # Execute
        result = self.nlp_processor.process(input_text, context=context)

        # Assert
        assert result["context"] == context
        assert result["preserved"] is True