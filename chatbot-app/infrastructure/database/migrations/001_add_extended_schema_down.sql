-- Rollback Migration: Remove extended schema tables
-- Version: 001 (down)
-- Date: 2025-11-17
-- Description: Remove user_profiles, admin_logs, personalization_data, ai_models, and analytics_data tables

-- Drop triggers
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop indexes
DROP INDEX IF EXISTS idx_user_profiles_user_id;
DROP INDEX IF EXISTS idx_admin_logs_admin_id;
DROP INDEX IF EXISTS idx_admin_logs_timestamp;
DROP INDEX IF EXISTS idx_personalization_data_user_id;
DROP INDEX IF EXISTS idx_personalization_data_timestamp;
DROP INDEX IF EXISTS idx_ai_models_name_version;
DROP INDEX IF EXISTS idx_analytics_data_user_id;
DROP INDEX IF EXISTS idx_analytics_data_metric_type;
DROP INDEX IF EXISTS idx_analytics_data_timestamp;

-- Drop tables (in reverse order due to foreign key constraints)
DROP TABLE IF EXISTS analytics_data;
DROP TABLE IF EXISTS ai_models;
DROP TABLE IF EXISTS personalization_data;
DROP TABLE IF EXISTS admin_logs;
DROP TABLE IF EXISTS user_profiles;

-- Migration rollback completed successfully