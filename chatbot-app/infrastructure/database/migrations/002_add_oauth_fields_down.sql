-- Rollback Migration: Remove OAuth fields from users table
-- Version: 002
-- Date: 2025-11-17
-- Description: Remove OAuth provider, OAuth ID, and picture fields

-- Drop index
DROP INDEX IF EXISTS idx_users_oauth_provider_id;

-- Remove OAuth-related columns from users table
ALTER TABLE users DROP COLUMN IF EXISTS picture;
ALTER TABLE users DROP COLUMN IF EXISTS oauth_id;
ALTER TABLE users DROP COLUMN IF EXISTS oauth_provider;

-- Rollback completed successfully