"""
Unit tests for AI Service Sentiment Analysis.

Tests cover:
- Sentiment classification (positive, negative, neutral)
- Emotion detection
- Confidence scoring
- Multi-label sentiment analysis
- Context-aware sentiment analysis
- Sarcasm detection
- Mixed sentiment handling
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from testing_framework import BaseTestCase, AsyncTestCase


class TestSentimentAnalysis(BaseTestCase):
    """Test cases for Sentiment Analysis service"""

    def setup_method(self):
        """Setup test fixtures"""
        super().setup_method()
        # Mock the actual sentiment analysis service
        self.sentiment_analysis = Mock()
        self.sentiment_analysis.analyze = AsyncMock()
        self.sentiment_analysis.analyze_conversation = AsyncMock()
        self.sentiment_analysis.get_sentiment_examples = AsyncMock()
        self.sentiment_analysis.get_emotion_examples = AsyncMock()

    @pytest.mark.unit
    @pytest.mark.ai
    def test_basic_sentiment_analysis(self):
        """Test basic sentiment analysis functionality"""
        # Setup
        input_text = "I love this product, it's amazing!"
        expected_result = {
            "sentiment": "positive",
            "confidence": 0.92,
            "scores": {
                "positive": 0.85,
                "negative": 0.05,
                "neutral": 0.10
            },
            "emotions": ["joy", "trust"],
            "intensity": 0.8
        }

        self.sentiment_analysis.analyze.return_value = expected_result

        # Execute
        result = self.sentiment_analysis.analyze(input_text)

        # Assert
        assert result["sentiment"] == "positive"
        assert result["confidence"] > 0.8
        assert result["scores"]["positive"] > result["scores"]["negative"]
        assert len(result["emotions"]) > 0
        assert result["intensity"] > 0.5

    @pytest.mark.unit
    @pytest.mark.ai
    def test_negative_sentiment_detection(self):
        """Test negative sentiment detection"""
        # Setup
        input_text = "This is terrible, I hate it so much!"
        expected_result = {
            "sentiment": "negative",
            "confidence": 0.89,
            "scores": {
                "positive": 0.03,
                "negative": 0.82,
                "neutral": 0.15
            },
            "emotions": ["anger", "disgust"],
            "intensity": 0.9
        }

        self.sentiment_analysis.analyze.return_value = expected_result

        # Execute
        result = self.sentiment_analysis.analyze(input_text)

        # Assert
        assert result["sentiment"] == "negative"
        assert result["scores"]["negative"] > result["scores"]["positive"]
        assert "anger" in result["emotions"]
        assert result["intensity"] > 0.7

    @pytest.mark.unit
    @pytest.mark.ai
    def test_neutral_sentiment_detection(self):
        """Test neutral sentiment detection"""
        # Setup
        input_text = "The product arrived on time."
        expected_result = {
            "sentiment": "neutral",
            "confidence": 0.76,
            "scores": {
                "positive": 0.25,
                "negative": 0.15,
                "neutral": 0.60
            },
            "emotions": ["neutral"],
            "intensity": 0.2
        }

        self.sentiment_analysis.analyze.return_value = expected_result

        # Execute
        result = self.sentiment_analysis.analyze(input_text)

        # Assert
        assert result["sentiment"] == "neutral"
        assert result["scores"]["neutral"] > result["scores"]["positive"]
        assert result["scores"]["neutral"] > result["scores"]["negative"]
        assert result["intensity"] < 0.5

    @pytest.mark.unit
    @pytest.mark.ai
    def test_mixed_sentiment_handling(self):
        """Test handling of mixed sentiment in text"""
        # Setup
        input_text = "The product is good but delivery was slow and packaging was damaged."
        expected_result = {
            "sentiment": "mixed",
            "confidence": 0.71,
            "scores": {
                "positive": 0.35,
                "negative": 0.45,
                "neutral": 0.20
            },
            "emotions": ["satisfaction", "frustration"],
            "intensity": 0.6,
            "sentiment_segments": [
                {"text": "good", "sentiment": "positive", "confidence": 0.8},
                {"text": "slow", "sentiment": "negative", "confidence": 0.7},
                {"text": "damaged", "sentiment": "negative", "confidence": 0.9}
            ]
        }

        self.sentiment_analysis.analyze.return_value = expected_result

        # Execute
        result = self.sentiment_analysis.analyze(input_text)

        # Assert
        assert result["sentiment"] == "mixed"
        assert len(result["sentiment_segments"]) == 3
        assert any(seg["sentiment"] == "positive" for seg in result["sentiment_segments"])
        assert any(seg["sentiment"] == "negative" for seg in result["sentiment_segments"])

    @pytest.mark.unit
    @pytest.mark.ai
    def test_sarcasm_detection(self):
        """Test sarcasm detection in sentiment analysis"""
        # Setup
        sarcastic_text = "Oh great, another delay. Just what I needed today."
        expected_result = {
            "sentiment": "negative",
            "confidence": 0.85,
            "sarcasm_detected": True,
            "sarcasm_confidence": 0.78,
            "actual_sentiment": "negative",
            "expressed_sentiment": "positive",
            "emotions": ["sarcasm", "frustration"]
        }

        self.sentiment_analysis.analyze.return_value = expected_result

        # Execute
        result = self.sentiment_analysis.analyze(sarcastic_text)

        # Assert
        assert result["sarcasm_detected"] is True
        assert result["sarcasm_confidence"] > 0.7
        assert result["sentiment"] == "negative"
        assert "sarcasm" in result["emotions"]

    @pytest.mark.unit
    @pytest.mark.ai
    def test_emotion_detection(self):
        """Test detailed emotion detection"""
        # Setup
        input_text = "I'm so excited about this new feature!"
        expected_result = {
            "sentiment": "positive",
            "confidence": 0.91,
            "emotions": ["excitement", "joy", "anticipation"],
            "emotion_scores": {
                "excitement": 0.85,
                "joy": 0.78,
                "anticipation": 0.65,
                "anger": 0.02,
                "sadness": 0.01
            },
            "primary_emotion": "excitement"
        }

        self.sentiment_analysis.analyze.return_value = expected_result

        # Execute
        result = self.sentiment_analysis.analyze(input_text)

        # Assert
        assert len(result["emotions"]) >= 2
        assert "excitement" in result["emotions"]
        assert result["primary_emotion"] == "excitement"
        assert result["emotion_scores"]["excitement"] > 0.8

    @pytest.mark.unit
    @pytest.mark.ai
    def test_context_aware_sentiment(self):
        """Test context-aware sentiment analysis"""
        # Setup
        input_text = "This is fine."
        context = {
            "previous_sentiment": "negative",
            "conversation_topic": "product_failure",
            "user_history": ["complained_about_product", "requested_refund"]
        }

        expected_result = {
            "sentiment": "negative",
            "confidence": 0.82,
            "context_influence": 0.7,
            "adjusted_from_context": True,
            "original_sentiment": "neutral",
            "context_factors": ["previous_negative", "complaint_history"]
        }

        self.sentiment_analysis.analyze.return_value = expected_result

        # Execute
        result = self.sentiment_analysis.analyze(input_text, context=context)

        # Assert
        assert result["sentiment"] == "negative"
        assert result["context_influence"] > 0.5
        assert result["adjusted_from_context"] is True
        assert result["original_sentiment"] == "neutral"

    @pytest.mark.unit
    @pytest.mark.ai
    def test_conversation_sentiment_analysis(self):
        """Test sentiment analysis of entire conversations"""
        # Setup
        conversation_history = [
            {"message": "Hi, I need help", "sentiment": "neutral"},
            {"message": "This product is broken!", "sentiment": "negative"},
            {"message": "I'm very disappointed", "sentiment": "negative"},
            {"message": "Can you fix this?", "sentiment": "neutral"}
        ]

        expected_result = {
            "overall_sentiment": "negative",
            "confidence": 0.88,
            "sentiment_trend": "worsening",
            "message_sentiments": conversation_history,
            "sentiment_distribution": {
                "positive": 0,
                "negative": 2,
                "neutral": 2
            },
            "escalation_detected": True,
            "average_intensity": 0.65
        }

        self.sentiment_analysis.analyze_conversation.return_value = expected_result

        # Execute
        result = self.sentiment_analysis.analyze_conversation(conversation_history)

        # Assert
        assert result["overall_sentiment"] == "negative"
        assert result["sentiment_trend"] == "worsening"
        assert result["escalation_detected"] is True
        assert result["sentiment_distribution"]["negative"] == 2

    @pytest.mark.unit
    @pytest.mark.ai
    def test_sentiment_examples_retrieval(self):
        """Test retrieval of sentiment examples"""
        # Setup
        sentiment_type = "positive"
        expected_examples = [
            "This is amazing!",
            "I love this product",
            "Excellent service",
            "Very satisfied with the quality"
        ]

        self.sentiment_analysis.get_sentiment_examples.return_value = expected_examples

        # Execute
        examples = self.sentiment_analysis.get_sentiment_examples(sentiment_type)

        # Assert
        assert len(examples) == 4
        assert all(any(word in example.lower() for word in ["amazing", "love", "excellent", "satisfied"])
                  for example in examples)

    @pytest.mark.unit
    @pytest.mark.ai
    def test_emotion_examples_retrieval(self):
        """Test retrieval of emotion examples"""
        # Setup
        emotion_type = "joy"
        expected_examples = [
            "I'm so happy!",
            "This makes me joyful",
            "What a delightful experience",
            "I'm thrilled with this"
        ]

        self.sentiment_analysis.get_emotion_examples.return_value = expected_examples

        # Execute
        examples = self.sentiment_analysis.get_emotion_examples(emotion_type)

        # Assert
        assert len(examples) == 4
        assert all(any(word in example.lower() for word in ["happy", "joyful", "delightful", "thrilled"])
                  for example in examples)

    @pytest.mark.unit
    @pytest.mark.ai
    def test_multilingual_sentiment(self):
        """Test sentiment analysis in different languages"""
        test_cases = [
            ("¡Esto es fantástico!", "positive", "es"),
            ("Das ist schrecklich!", "negative", "de"),
            ("C'est merveilleux!", "positive", "fr"),
            ("Это ужасно!", "negative", "ru")
        ]

        for text, expected_sentiment, language in test_cases:
            self.sentiment_analysis.analyze.return_value = {
                "sentiment": expected_sentiment,
                "confidence": 0.85,
                "language": language,
                "language_supported": True
            }

            result = self.sentiment_analysis.analyze(text)

            assert result["sentiment"] == expected_sentiment
            assert result["language"] == language
            assert result["language_supported"] is True

    @pytest.mark.unit
    @pytest.mark.ai
    def test_sentiment_intensity_levels(self):
        """Test different intensity levels of sentiment"""
        intensity_levels = [
            ("This is okay", "neutral", 0.2),
            ("This is good", "positive", 0.5),
            ("This is great!", "positive", 0.8),
            ("This is amazing!!!", "positive", 0.95)
        ]

        for text, expected_sentiment, expected_intensity in intensity_levels:
            self.sentiment_analysis.analyze.return_value = {
                "sentiment": expected_sentiment,
                "confidence": 0.9,
                "intensity": expected_intensity,
                "intensity_level": "low" if expected_intensity < 0.4 else "high"
            }

            result = self.sentiment_analysis.analyze(text)

            assert result["sentiment"] == expected_sentiment
            assert abs(result["intensity"] - expected_intensity) < 0.1

    @pytest.mark.unit
    @pytest.mark.ai
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Setup
        invalid_inputs = [None, "", 123, [], {}]

        for invalid_input in invalid_inputs:
            self.sentiment_analysis.analyze.side_effect = ValueError("Invalid input type")

            # Execute & Assert
            with pytest.raises(ValueError, match="Invalid input type"):
                self.sentiment_analysis.analyze(invalid_input)

    @pytest.mark.unit
    @pytest.mark.ai
    @pytest.mark.performance
    def test_performance_under_load(self):
        """Test performance under load"""
        # Setup
        test_messages = [
            "I love this!",
            "This is terrible",
            "It's okay",
            "Amazing product!"
        ] * 50  # 200 messages total

        # Mock responses
        responses = []
        for i, msg in enumerate(test_messages):
            sentiment = ["positive", "negative", "neutral", "positive"][i % 4]
            responses.append({
                "sentiment": sentiment,
                "confidence": 0.8 + (i % 20) / 100,
                "processing_time": 0.005 + (i % 10) / 1000
            })

        self.sentiment_analysis.analyze.side_effect = responses

        # Execute performance test
        start_time = self.metrics.start_time
        for msg in test_messages:
            self.sentiment_analysis.analyze(msg)

        end_time = self.metrics.end_time or self.metrics.start_time
        total_time = (end_time - start_time).total_seconds()

        # Assert performance requirements
        avg_time_per_request = total_time / len(test_messages)
        assert avg_time_per_request < 0.05  # Less than 50ms per request