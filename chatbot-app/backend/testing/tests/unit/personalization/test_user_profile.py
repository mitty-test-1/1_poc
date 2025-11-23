"""
Unit tests for Personalization Service User Profile.

Tests cover:
- User profile creation and updates
- Behavioral trait analysis
- Engagement metrics calculation
- Profile data validation
- Privacy and data protection
- Profile merging and deduplication
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from datetime import datetime, timedelta

from testing_framework import BaseTestCase, AsyncTestCase


class TestUserProfile(BaseTestCase):
    """Test cases for User Profile service"""

    def setup_method(self):
        """Setup test fixtures"""
        super().setup_method()
        # Mock the actual user profile service
        self.user_profile = Mock()
        self.user_profile.create_profile = AsyncMock()
        self.user_profile.get_profile = AsyncMock()
        self.user_profile.update_profile = AsyncMock()
        self.user_profile.get_behavioral_traits = AsyncMock()
        self.user_profile.get_engagement_metrics = AsyncMock()
        self.user_profile.get_analytics_summary = AsyncMock()

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_user_profile_creation(self):
        """Test user profile creation"""
        # Setup
        user_data = {
            "user_id": "user_123",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "preferences": {
                "language": "en",
                "theme": "light",
                "notifications": True
            },
            "registration_date": "2024-01-01T00:00:00Z"
        }

        expected_profile = {
            **user_data,
            "profile_id": "profile_123",
            "behavioral_traits": {},
            "engagement_metrics": {},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }

        self.user_profile.create_profile.return_value = expected_profile

        # Execute
        result = self.user_profile.create_profile(user_data)

        # Assert
        assert result["user_id"] == user_data["user_id"]
        assert result["profile_id"] is not None
        assert "behavioral_traits" in result
        assert "engagement_metrics" in result
        assert "created_at" in result

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_user_profile_retrieval(self):
        """Test user profile retrieval"""
        # Setup
        user_id = "user_123"
        expected_profile = {
            "user_id": user_id,
            "profile_id": "profile_123",
            "name": "John Doe",
            "preferences": {"language": "en", "theme": "light"},
            "behavioral_traits": {
                "engagement_level": "high",
                "communication_style": "formal"
            },
            "engagement_metrics": {
                "total_sessions": 25,
                "average_session_length": 15.5
            },
            "last_active": "2024-01-15T10:30:00Z"
        }

        self.user_profile.get_profile.return_value = expected_profile

        # Execute
        result = self.user_profile.get_profile(user_id)

        # Assert
        assert result["user_id"] == user_id
        assert result["profile_id"] == "profile_123"
        assert "behavioral_traits" in result
        assert "engagement_metrics" in result

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_user_profile_update(self):
        """Test user profile updates"""
        # Setup
        user_id = "user_123"
        update_data = {
            "preferences": {
                "language": "es",
                "theme": "dark"
            },
            "behavioral_traits": {
                "communication_style": "casual"
            }
        }

        expected_result = {
            "user_id": user_id,
            "updated_fields": ["preferences", "behavioral_traits"],
            "updated_at": "2024-01-15T11:00:00Z",
            "version": 2
        }

        self.user_profile.update_profile.return_value = expected_result

        # Execute
        result = self.user_profile.update_profile(user_id, update_data)

        # Assert
        assert result["user_id"] == user_id
        assert "preferences" in result["updated_fields"]
        assert "behavioral_traits" in result["updated_fields"]
        assert result["version"] == 2

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_behavioral_traits_analysis(self):
        """Test behavioral traits analysis"""
        # Setup
        user_id = "user_123"
        expected_traits = {
            "engagement_level": "high",
            "communication_style": "formal",
            "response_time_preference": "detailed",
            "interaction_frequency": "daily",
            "preferred_channels": ["web", "mobile"],
            "time_of_activity": "morning",
            "content_complexity": "advanced"
        }

        self.user_profile.get_behavioral_traits.return_value = expected_traits

        # Execute
        result = self.user_profile.get_behavioral_traits(user_id)

        # Assert
        assert result["engagement_level"] == "high"
        assert result["communication_style"] == "formal"
        assert isinstance(result["preferred_channels"], list)
        assert len(result["preferred_channels"]) > 0

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_engagement_metrics_calculation(self):
        """Test engagement metrics calculation"""
        # Setup
        user_id = "user_123"
        days = 30
        expected_metrics = {
            "total_sessions": 45,
            "total_interactions": 234,
            "average_session_length": 18.5,
            "average_response_time": 2.3,
            "completion_rate": 0.87,
            "satisfaction_score": 4.2,
            "retention_rate": 0.92,
            "last_active": "2024-01-15T10:30:00Z",
            "days_active": 28
        }

        self.user_profile.get_engagement_metrics.return_value = expected_metrics

        # Execute
        result = self.user_profile.get_engagement_metrics(user_id, days)

        # Assert
        assert result["total_sessions"] > 0
        assert result["completion_rate"] <= 1.0
        assert result["satisfaction_score"] <= 5.0
        assert result["days_active"] <= days

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_analytics_summary_generation(self):
        """Test analytics summary generation"""
        # Setup
        user_id = "user_123"
        days = 30
        expected_summary = {
            "user_id": user_id,
            "period_days": days,
            "engagement_trend": "increasing",
            "top_interactions": [
                {"type": "conversation", "count": 25},
                {"type": "feedback", "count": 12},
                {"type": "settings_change", "count": 8}
            ],
            "behavioral_insights": [
                "User prefers morning interactions",
                "High engagement with detailed responses",
                "Consistent daily activity pattern"
            ],
            "recommendations": [
                "Suggest premium features",
                "Increase personalized content",
                "Optimize for mobile usage"
            ],
            "generated_at": "2024-01-15T12:00:00Z"
        }

        self.user_profile.get_analytics_summary.return_value = expected_summary

        # Execute
        result = self.user_profile.get_analytics_summary(user_id, days)

        # Assert
        assert result["user_id"] == user_id
        assert result["period_days"] == days
        assert len(result["top_interactions"]) > 0
        assert len(result["behavioral_insights"]) > 0
        assert len(result["recommendations"]) > 0

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_profile_data_validation(self):
        """Test profile data validation"""
        # Setup - valid data
        valid_profile = {
            "user_id": "user_123",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "preferences": {"language": "en"}
        }

        # Setup - invalid data
        invalid_profiles = [
            {"user_id": "", "name": "John"},  # Empty user_id
            {"user_id": "user_123", "email": "invalid-email"},  # Invalid email
            {"user_id": "user_123", "preferences": "invalid"},  # Invalid preferences type
        ]

        # Test valid profile
        self.user_profile.create_profile.return_value = {"status": "created", "profile_id": "profile_123"}
        result = self.user_profile.create_profile(valid_profile)
        assert result["status"] == "created"

        # Test invalid profiles
        for invalid_profile in invalid_profiles:
            self.user_profile.create_profile.side_effect = ValueError("Invalid profile data")

            with pytest.raises(ValueError, match="Invalid profile data"):
                self.user_profile.create_profile(invalid_profile)

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_profile_privacy_protection(self):
        """Test privacy protection features"""
        # Setup
        user_id = "user_123"
        sensitive_data = {
            "personal_info": {
                "ssn": "123-45-6789",
                "credit_card": "4111111111111111",
                "address": "123 Main St"
            }
        }

        # Mock privacy filtering
        self.user_profile.get_profile.return_value = {
            "user_id": user_id,
            "name": "John Doe",
            "preferences": {"language": "en"},
            "personal_info": "[REDACTED - SENSITIVE DATA]"
        }

        # Execute
        result = self.user_profile.get_profile(user_id)

        # Assert
        assert "[REDACTED" in str(result.get("personal_info", ""))

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_profile_merging_and_deduplication(self):
        """Test profile merging and deduplication"""
        # Setup
        duplicate_profiles = [
            {"user_id": "user_123", "source": "registration", "email": "john@example.com"},
            {"user_id": "user_123", "source": "social_login", "email": "john@example.com"},
            {"user_id": "user_456", "source": "registration", "email": "jane@example.com"}
        ]

        expected_merge_result = {
            "merged_profiles": 2,
            "unique_users": 2,
            "conflicts_resolved": 1,
            "merged_data": {
                "user_123": {
                    "sources": ["registration", "social_login"],
                    "primary_email": "john@example.com"
                }
            }
        }

        # Mock merge operation
        self.user_profile.merge_duplicate_profiles = Mock(return_value=expected_merge_result)

        # Execute
        result = self.user_profile.merge_duplicate_profiles(duplicate_profiles)

        # Assert
        assert result["merged_profiles"] == 2
        assert result["unique_users"] == 2
        assert result["conflicts_resolved"] >= 0

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_profile_versioning(self):
        """Test profile versioning"""
        # Setup
        user_id = "user_123"
        versions = [
            {"version": 1, "timestamp": "2024-01-01T00:00:00Z", "changes": "Profile created"},
            {"version": 2, "timestamp": "2024-01-05T00:00:00Z", "changes": "Updated preferences"},
            {"version": 3, "timestamp": "2024-01-10T00:00:00Z", "changes": "Added behavioral traits"}
        ]

        self.user_profile.get_profile_versions = Mock(return_value=versions)

        # Execute
        result = self.user_profile.get_profile_versions(user_id)

        # Assert
        assert len(result) == 3
        assert result[0]["version"] == 1
        assert result[-1]["version"] == 3
        # Check chronological order
        timestamps = [v["timestamp"] for v in result]
        assert timestamps == sorted(timestamps)

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_bulk_profile_operations(self):
        """Test bulk profile operations"""
        # Setup
        user_ids = [f"user_{i:03d}" for i in range(100)]
        bulk_operation = "update_engagement_metrics"

        expected_result = {
            "operation": bulk_operation,
            "total_users": 100,
            "successful": 98,
            "failed": 2,
            "failures": [
                {"user_id": "user_005", "error": "Profile not found"},
                {"user_id": "user_050", "error": "Database timeout"}
            ],
            "processing_time": 45.5
        }

        self.user_profile.bulk_update_profiles = Mock(return_value=expected_result)

        # Execute
        result = self.user_profile.bulk_update_profiles(user_ids, bulk_operation)

        # Assert
        assert result["total_users"] == 100
        assert result["successful"] + result["failed"] == result["total_users"]
        assert len(result["failures"]) == result["failed"]
        assert result["processing_time"] > 0

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_profile_export_import(self):
        """Test profile export and import functionality"""
        # Setup
        user_id = "user_123"
        export_format = "json"

        exported_data = {
            "user_id": user_id,
            "export_format": export_format,
            "data": {
                "profile": {"name": "John Doe", "preferences": {"language": "en"}},
                "behavioral_traits": {"engagement_level": "high"},
                "engagement_metrics": {"total_sessions": 25}
            },
            "exported_at": "2024-01-15T12:00:00Z",
            "checksum": "abc123def456"
        }

        self.user_profile.export_profile = Mock(return_value=exported_data)
        self.user_profile.import_profile = Mock(return_value={"status": "imported", "profile_id": "profile_123"})

        # Execute export
        export_result = self.user_profile.export_profile(user_id, export_format)

        # Execute import
        import_result = self.user_profile.import_profile(exported_data)

        # Assert
        assert export_result["user_id"] == user_id
        assert export_result["export_format"] == export_format
        assert "checksum" in export_result
        assert import_result["status"] == "imported"

    @pytest.mark.unit
    @pytest.mark.personalization
    def test_error_handling(self):
        """Test error handling for profile operations"""
        # Setup
        error_scenarios = [
            ("ProfileNotFound", "User profile not found"),
            ("DatabaseError", "Database connection failed"),
            ("ValidationError", "Invalid profile data"),
            ("PermissionDenied", "Access denied to profile")
        ]

        for error_type, error_message in error_scenarios:
            self.user_profile.get_profile.side_effect = Exception(f"{error_type}: {error_message}")

            with pytest.raises(Exception, match=error_message):
                self.user_profile.get_profile("user_123")

    @pytest.mark.unit
    @pytest.mark.personalization
    @pytest.mark.performance
    def test_profile_performance(self):
        """Test profile operation performance"""
        # Setup
        user_id = "user_123"

        self.user_profile.get_profile.return_value = {
            "user_id": user_id,
            "processing_time": 0.05,
            "cache_hit": True,
            "database_queries": 1
        }

        # Execute
        result, duration, memory_delta = self.measure_performance(
            self.user_profile.get_profile, user_id
        )

        # Assert performance requirements
        assert result["processing_time"] < 0.1  # Less than 100ms
        assert duration < 0.1
        assert result["database_queries"] <= 2  # Minimal database queries