-- Migration: Add extended schema tables for chatbot application
-- Version: 001
-- Date: 2025-11-17
-- Description: Add user_profiles, admin_logs, personalization_data, ai_models, and analytics_data tables

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    preferences JSONB DEFAULT '{}',
    demographics JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create admin_logs table
CREATE TABLE IF NOT EXISTS admin_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create personalization_data table
CREATE TABLE IF NOT EXISTS personalization_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    behavior_type VARCHAR(100) NOT NULL,
    data_value JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ai_models table
CREATE TABLE IF NOT EXISTS ai_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'available',
    performance_metrics JSONB DEFAULT '{}',
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create analytics_data table
CREATE TABLE IF NOT EXISTS analytics_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    metric_type VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_id ON admin_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_timestamp ON admin_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_personalization_data_user_id ON personalization_data(user_id);
CREATE INDEX IF NOT EXISTS idx_personalization_data_timestamp ON personalization_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_ai_models_name_version ON ai_models(model_name, version);
CREATE INDEX IF NOT EXISTS idx_analytics_data_user_id ON analytics_data(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_data_metric_type ON analytics_data(metric_type);
CREATE INDEX IF NOT EXISTS idx_analytics_data_timestamp ON analytics_data(timestamp);

-- Add trigger to update updated_at timestamp for user_profiles
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default user profiles for existing users
INSERT INTO user_profiles (user_id, preferences, demographics, settings)
SELECT
    id as user_id,
    preferences as preferences,
    '{}' as demographics,
    '{}' as settings
FROM users
WHERE id NOT IN (SELECT user_id FROM user_profiles);

-- Add comments for documentation
COMMENT ON TABLE user_profiles IS 'Extended user information and preferences';
COMMENT ON TABLE admin_logs IS 'Administrative actions and audit trail';
COMMENT ON TABLE personalization_data IS 'User behavior and preference data for personalization';
COMMENT ON TABLE ai_models IS 'AI model configuration and performance data';
COMMENT ON TABLE analytics_data IS 'Usage analytics and metrics data';

-- Migration completed successfully
-- To rollback this migration, run the corresponding down migration