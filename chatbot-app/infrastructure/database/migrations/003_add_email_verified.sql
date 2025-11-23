-- Migration: Add email_verified field for OAuth users
-- Version: 003
-- Date: 2025-11-17
-- Description: Add email_verified boolean field to track email verification status

-- Add email_verified column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;

-- Set email_verified to TRUE for existing OAuth users
UPDATE users SET email_verified = TRUE WHERE oauth_provider IS NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN users.email_verified IS 'Whether the user email has been verified';

-- Migration completed successfully
-- To rollback this migration, run the corresponding down migration