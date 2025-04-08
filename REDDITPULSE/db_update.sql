-- Reddit Automation Tool - Database Update Script
-- Created by: SinaMohammadHosseinZadeh
-- Version: 1.0.1

-- Add a version tracking table if it doesn't exist
CREATE TABLE IF NOT EXISTS db_version (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(100) DEFAULT 'system',
    description TEXT
);

-- Check if this update has already been applied
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM db_version WHERE version = '1.0.1') THEN
        -- Record the version before running migrations
        INSERT INTO db_version (version, applied_by, description)
        VALUES ('1.0.1', 'SinaMohammadHosseinZadeh', 'Add analytics tracking and performance metrics');
        
        -- Run migrations for version 1.0.1
        
        -- 1. Add new analytics table
        CREATE TABLE bot_analytics (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            total_responses INTEGER DEFAULT 0,
            successful_responses INTEGER DEFAULT 0,
            failed_responses INTEGER DEFAULT 0,
            avg_relevance_score FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- 2. Add performance metrics table
        CREATE TABLE subreddit_performance (
            id SERIAL PRIMARY KEY,
            subreddit VARCHAR(100) NOT NULL REFERENCES subreddits(name),
            date DATE NOT NULL,
            total_responses INTEGER DEFAULT 0,
            successful_responses INTEGER DEFAULT 0,
            failed_responses INTEGER DEFAULT 0,
            avg_relevance_score FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(subreddit, date)
        );
        
        -- 3. Add trending keywords table
        CREATE TABLE trending_keywords (
            id SERIAL PRIMARY KEY,
            keyword VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            occurrence_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(keyword, date)
        );
        
        -- 4. Add indexes for performance
        CREATE INDEX idx_bot_analytics_date ON bot_analytics(date);
        CREATE INDEX idx_subreddit_performance_date ON subreddit_performance(date);
        CREATE INDEX idx_trending_keywords_date ON trending_keywords(date);
        
        -- 5. Add a new column to bot_responses for response time tracking
        ALTER TABLE bot_responses ADD COLUMN response_time_ms INTEGER;
        
        -- 6. Add a new column to track A/B testing variants
        ALTER TABLE bot_responses ADD COLUMN template_variant VARCHAR(20);
        
        -- Record successful completion
        UPDATE db_version 
        SET description = description || ' - Successfully applied'
        WHERE version = '1.0.1';
        
        -- Output success message
        RAISE NOTICE 'Successfully updated database to version 1.0.1';
    ELSE
        RAISE NOTICE 'Database already at version 1.0.1 or higher';
    END IF;
END
$$;