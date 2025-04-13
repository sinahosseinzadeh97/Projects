# Database Schema Design

This document outlines the database schema for the YouTube Q&A system, including tables, relationships, and indexes.

## Overview

The database schema is designed to store:
1. Video metadata from YouTube
2. Transcript segments with timestamps
3. References to embedding vectors (stored in FAISS)
4. User queries and responses (for analytics and caching)

## Schema Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│                 │       │                 │       │                 │
│     videos      │───1:n─┤  transcript_    │───1:1─┤   embeddings    │
│                 │       │    segments     │       │                 │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                                            │
                                                            │
┌─────────────────┐       ┌─────────────────┐              │
│                 │       │                 │              │
│     queries     │───1:n─┤  query_results  │──────n:1─────┘
│                 │       │                 │
└─────────────────┘       └─────────────────┘
```

## Tables

### videos

Stores metadata about YouTube videos.

```sql
CREATE TABLE videos (
    id TEXT PRIMARY KEY,           -- YouTube video ID
    channel_id TEXT NOT NULL,      -- YouTube channel ID
    title TEXT NOT NULL,           -- Video title
    description TEXT,              -- Video description
    published_at TIMESTAMP,        -- Publication date
    thumbnail_url TEXT,            -- URL to video thumbnail
    duration INTEGER,              -- Duration in seconds
    has_transcript BOOLEAN,        -- Whether video has transcript
    processed_at TIMESTAMP,        -- When video was processed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_videos_channel_id ON videos(channel_id);
CREATE INDEX idx_videos_published_at ON videos(published_at);
```

### transcript_segments

Stores individual segments of video transcripts.

```sql
CREATE TABLE transcript_segments (
    id TEXT PRIMARY KEY,           -- Unique segment ID (generated)
    video_id TEXT NOT NULL,        -- Reference to videos.id
    text TEXT NOT NULL,            -- Segment text content
    start_time REAL NOT NULL,      -- Start time in seconds
    duration REAL NOT NULL,        -- Duration in seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE INDEX idx_segments_video_id ON transcript_segments(video_id);
CREATE INDEX idx_segments_text ON transcript_segments(text);
```

### embeddings

Stores metadata about embeddings (actual vectors stored in FAISS).

```sql
CREATE TABLE embeddings (
    id TEXT PRIMARY KEY,           -- Same as segment ID
    segment_id TEXT NOT NULL,      -- Reference to transcript_segments.id
    model_name TEXT NOT NULL,      -- Name of embedding model used
    dimension INTEGER NOT NULL,    -- Embedding dimension
    faiss_index TEXT NOT NULL,     -- Path to FAISS index file
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (segment_id) REFERENCES transcript_segments(id) ON DELETE CASCADE
);

CREATE INDEX idx_embeddings_segment_id ON embeddings(segment_id);
CREATE INDEX idx_embeddings_model_name ON embeddings(model_name);
```

### queries

Stores user queries for analytics and caching.

```sql
CREATE TABLE queries (
    id TEXT PRIMARY KEY,           -- Unique query ID (generated)
    question TEXT NOT NULL,        -- User question
    embedding_model TEXT NOT NULL, -- Embedding model used
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_queries_question ON queries(question);
CREATE INDEX idx_queries_created_at ON queries(created_at);
```

### query_results

Stores results of queries for caching and analytics.

```sql
CREATE TABLE query_results (
    id TEXT PRIMARY KEY,           -- Unique result ID (generated)
    query_id TEXT NOT NULL,        -- Reference to queries.id
    segment_id TEXT NOT NULL,      -- Reference to transcript_segments.id
    similarity REAL NOT NULL,      -- Similarity score
    rank INTEGER NOT NULL,         -- Rank in results
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id) ON DELETE CASCADE,
    FOREIGN KEY (segment_id) REFERENCES transcript_segments(id) ON DELETE CASCADE
);

CREATE INDEX idx_results_query_id ON query_results(query_id);
CREATE INDEX idx_results_segment_id ON query_results(segment_id);
```

### answers

Stores generated answers for caching.

```sql
CREATE TABLE answers (
    id TEXT PRIMARY KEY,           -- Unique answer ID (generated)
    query_id TEXT NOT NULL,        -- Reference to queries.id
    answer_text TEXT NOT NULL,     -- Generated answer
    model_name TEXT NOT NULL,      -- OpenAI model used
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id) ON DELETE CASCADE
);

CREATE INDEX idx_answers_query_id ON answers(query_id);
```

## Data Access Patterns

### Common Queries

1. **Get videos from a channel**:
   ```sql
   SELECT * FROM videos 
   WHERE channel_id = ? 
   ORDER BY published_at DESC 
   LIMIT ? OFFSET ?;
   ```

2. **Get transcript segments for a video**:
   ```sql
   SELECT * FROM transcript_segments 
   WHERE video_id = ? 
   ORDER BY start_time ASC;
   ```

3. **Get segments by IDs (for search results)**:
   ```sql
   SELECT ts.*, v.title as video_title 
   FROM transcript_segments ts
   JOIN videos v ON ts.video_id = v.id
   WHERE ts.id IN (?, ?, ?, ...);
   ```

4. **Check for cached answer**:
   ```sql
   SELECT a.* 
   FROM answers a
   JOIN queries q ON a.query_id = q.id
   WHERE q.question = ?
   ORDER BY a.created_at DESC
   LIMIT 1;
   ```

### Transactions

1. **Store new video with segments**:
   ```sql
   BEGIN TRANSACTION;
   INSERT INTO videos (...) VALUES (...);
   INSERT INTO transcript_segments (...) VALUES (...), (...), ...;
   COMMIT;
   ```

2. **Store query results and answer**:
   ```sql
   BEGIN TRANSACTION;
   INSERT INTO queries (...) VALUES (...);
   INSERT INTO query_results (...) VALUES (...), (...), ...;
   INSERT INTO answers (...) VALUES (...);
   COMMIT;
   ```

## Migration Strategy

The database schema should be managed using a migration tool (e.g., Alembic for SQLAlchemy) to handle schema evolution over time. Initial migrations should:

1. Create base tables
2. Add indexes
3. Add constraints

## Scaling Considerations

1. **Partitioning**:
   - Consider partitioning transcript_segments by video_id for large datasets
   - Consider time-based partitioning for queries and answers

2. **Indexing Strategy**:
   - Full-text search indexes for transcript content
   - Composite indexes for common query patterns

3. **Caching Layer**:
   - Implement Redis cache for frequent queries
   - Cache embeddings in memory for active videos

## Database Selection

1. **Development**: SQLite for simplicity
2. **Production**: PostgreSQL for scalability and advanced features
   - Use PostgreSQL's full-text search capabilities
   - Leverage JSON/JSONB for flexible metadata storage
