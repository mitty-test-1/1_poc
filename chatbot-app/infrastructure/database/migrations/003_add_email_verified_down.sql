-- Rollback Migration: Remove email_verified field
-- Version: 003
-- Date: 2025-11-17
-- Description: Remove email_verified boolean field

-- Remove email_verified column from users table
ALTER TABLE users DROP COLUMN IF EXISTS email_verified;

-- Rollback completed successfully