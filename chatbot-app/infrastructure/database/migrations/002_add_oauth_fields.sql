-- Migration: Add OAuth fields to users table
-- Version: 002
-- Date: 2025-11-17
-- Description: Add OAuth provider, OAuth ID, and picture fields to support OAuth authentication

-- Add OAuth-related columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS oauth_id VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS picture VARCHAR(500);

-- Create index for OAuth lookups
CREATE INDEX IF NOT EXISTS idx_users_oauth_provider_id ON users(oauth_provider, oauth_id);

-- Add comments for documentation
COMMENT ON COLUMN users.oauth_provider IS 'OAuth provider (google, github, microsoft)';
COMMENT ON COLUMN users.oauth_id IS 'OAuth provider user ID';
COMMENT ON COLUMN users.picture IS 'User profile picture URL from OAuth provider';

-- Migration completed successfully
-- To rollback this migration, run the corresponding down migration