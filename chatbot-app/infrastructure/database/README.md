# Database Schema Documentation

## Overview
This document describes the extended database schema for the chatbot application, including the new tables added for enhanced functionality.

## Tables

### Existing Tables
- `users` - User accounts and authentication
- `conversations` - Chat conversations between users and admins
- `messages` - Individual messages within conversations

### New Tables

#### user_profiles
Extended user information and preferences.

**Columns:**
- `user_id` (UUID, FK to users.id) - Primary key and foreign key
- `preferences` (JSONB) - User preferences and settings
- `demographics` (JSONB) - User demographic information
- `settings` (JSONB) - Application-specific settings
- `created_at` (TIMESTAMP) - Profile creation timestamp
- `updated_at` (TIMESTAMP) - Last update timestamp (auto-updated)

**Indexes:** `idx_user_profiles_user_id`

#### admin_logs
Administrative actions and audit trail.

**Columns:**
- `id` (UUID) - Primary key
- `admin_id` (UUID, FK to users.id) - Admin who performed the action
- `action` (VARCHAR(100)) - Type of action performed
- `target_table` (VARCHAR(100)) - Table affected by the action
- `target_id` (UUID) - ID of the affected record
- `old_values` (JSONB) - Previous values before the action
- `new_values` (JSONB) - New values after the action
- `timestamp` (TIMESTAMP) - When the action occurred

**Indexes:** `idx_admin_logs_admin_id`, `idx_admin_logs_timestamp`

#### personalization_data
User behavior and preference data for personalization.

**Columns:**
- `id` (UUID) - Primary key
- `user_id` (UUID, FK to users.id) - User this data belongs to
- `behavior_type` (VARCHAR(100)) - Type of behavior (e.g., 'conversation', 'click', 'preference')
- `data_value` (JSONB) - Structured data about the behavior
- `timestamp` (TIMESTAMP) - When the behavior occurred

**Indexes:** `idx_personalization_data_user_id`, `idx_personalization_data_timestamp`

#### ai_models
AI model configuration and performance data.

**Columns:**
- `id` (UUID) - Primary key
- `model_name` (VARCHAR(255)) - Name of the AI model
- `version` (VARCHAR(50)) - Version of the model
- `status` (VARCHAR(50)) - Current status (available, training, deprecated)
- `performance_metrics` (JSONB) - Performance metrics and benchmarks
- `config` (JSONB) - Model configuration parameters
- `created_at` (TIMESTAMP) - When the model was created

**Indexes:** `idx_ai_models_name_version`

#### analytics_data
Usage analytics and metrics data.

**Columns:**
- `id` (UUID) - Primary key
- `user_id` (UUID, FK to users.id, nullable) - Associated user (null for system metrics)
- `metric_type` (VARCHAR(100)) - Type of metric being tracked
- `value` (FLOAT) - Numeric value of the metric
- `timestamp` (TIMESTAMP) - When the metric was recorded
- `metadata` (JSONB) - Additional context about the metric

**Indexes:** `idx_analytics_data_user_id`, `idx_analytics_data_metric_type`, `idx_analytics_data_timestamp`

## Migration

### Running Migrations
Use the migration script to apply schema changes:

```bash
# Apply all pending migrations
python migrate.py up

# Apply specific migration
python migrate.py up 001

# Rollback migrations
python migrate.py down 001

# Check migration status
python migrate.py status
```

### Migration Files
- `001_add_extended_schema.sql` - Adds all new tables and indexes
- `001_add_extended_schema_down.sql` - Removes all new tables and indexes

## SQLAlchemy Models

The `chatbot-app/backend/data/src/models/database.py` file contains SQLAlchemy ORM models for all tables.

### Key Features
- Proper foreign key relationships
- Automatic timestamp handling
- JSONB support for flexible data storage
- Comprehensive indexing for performance

### Usage Example
```python
from models.database import UserProfile, get_session_local

# Create a new user profile
SessionLocal = get_session_local()
with SessionLocal() as session:
    profile = UserProfile(
        user_id=user_id,
        preferences={"theme": "dark"},
        demographics={"age": 25}
    )
    session.add(profile)
    session.commit()
```

## Backward Compatibility

The schema changes maintain backward compatibility:
- Existing tables remain unchanged
- New tables are additive only
- Foreign key constraints ensure data integrity
- Migration scripts include rollback capabilities

## Performance Considerations

- All foreign keys are indexed
- Timestamp columns are indexed for time-based queries
- JSONB columns allow flexible querying with GIN indexes
- Composite indexes on commonly queried column combinations

## Data Types

- UUID for all primary keys (consistent with existing schema)
- JSONB for flexible structured data storage
- TIMESTAMP for all temporal data
- Appropriate VARCHAR lengths for string constraints