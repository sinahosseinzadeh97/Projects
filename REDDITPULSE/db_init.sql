-- Reddit Automation Tool - Database Initialization Script
-- Created by: SinaMohammadHosseinZadeh

-- Drop tables if they exist (for clean reinstallation)
DROP TABLE IF EXISTS bot_responses;
DROP TABLE IF EXISTS subreddits;
DROP TABLE IF EXISTS keywords;

-- Create subreddits table
CREATE TABLE subreddits (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create keywords table
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    relevance_weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create bot_responses table
CREATE TABLE bot_responses (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100) NOT NULL,
    post_title TEXT NOT NULL,
    subreddit VARCHAR(100) NOT NULL REFERENCES subreddits(name),
    comment_id VARCHAR(100),
    comment_text TEXT NOT NULL,
    relevance_score FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    template_used VARCHAR(100),
    keywords_matched TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX idx_bot_responses_created_at ON bot_responses(created_at);
CREATE INDEX idx_bot_responses_subreddit ON bot_responses(subreddit);
CREATE INDEX idx_bot_responses_status ON bot_responses(status);

-- Insert default subreddits
INSERT INTO subreddits (name) VALUES 
('health'),
('wellness'),
('alternativemedicine'),
('naturalremedies'),
('holistichealth');

-- Insert default keywords (health category)
INSERT INTO keywords (word, category, relevance_weight) VALUES
('health', 'health', 1.0),
('medicine', 'health', 0.8),
('doctor', 'health', 0.8),
('treatment', 'health', 0.7),
('therapy', 'health', 0.7);

-- Insert default keywords (wellness category)
INSERT INTO keywords (word, category, relevance_weight) VALUES
('wellness', 'wellness', 1.0),
('lifestyle', 'wellness', 0.8),
('mindfulness', 'wellness', 0.9),
('meditation', 'wellness', 0.9),
('balance', 'wellness', 0.7);

-- Insert default keywords (alternative medicine category)
INSERT INTO keywords (word, category, relevance_weight) VALUES
('natural', 'alternative_medicine', 0.9),
('herbal', 'alternative_medicine', 0.9),
('holistic', 'alternative_medicine', 1.0),
('alternative', 'alternative_medicine', 0.8),
('homeopathy', 'alternative_medicine', 0.9),
('acupuncture', 'alternative_medicine', 0.8),
('ayurveda', 'alternative_medicine', 0.8),
('supplement', 'alternative_medicine', 0.7),
('remedy', 'alternative_medicine', 0.8),
('healing', 'alternative_medicine', 0.7);

-- Grant permissions (use in production with caution)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_user;

-- Add a note about the creator
COMMENT ON DATABASE reddit_bot IS 'Reddit Automation Tool database created by SinaMohammadHosseinZadeh';