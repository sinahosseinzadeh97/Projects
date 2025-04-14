# YouTube Q&A System Architecture

## System Overview

The YouTube Q&A system is designed to provide content-based question answering using videos from a YouTube channel. The system processes video transcripts, creates semantic embeddings, and uses these to retrieve relevant content when users ask questions. The architecture follows a modular design with clear separation of concerns.

## High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Data Ingestion │────▶│  Data Processing│────▶│  Data Storage   │
│     Module      │     │     Module      │     │     Module      │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │◀───▶│   API Layer     │◀───▶│  Query Engine   │
│     Module      │     │                 │     │     Module      │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Core Modules

### 1. Data Ingestion Module

**Purpose**: Retrieve videos and transcripts from YouTube.

**Components**:
- YouTube API Client: Connects to YouTube Data API to fetch video metadata
- Transcript Extractor: Retrieves and processes video transcripts
- Data Validator: Ensures data quality and completeness

**Key Functions**:
- `fetch_channel_videos(channel_id)`: Retrieves list of videos from a channel
- `extract_transcript(video_id)`: Extracts transcript for a specific video
- `validate_and_clean_data(video_data, transcript_data)`: Validates and cleans the retrieved data

### 2. Data Processing Module

**Purpose**: Process transcripts and generate embeddings.

**Components**:
- Transcript Segmenter: Splits transcripts into meaningful segments
- Embedding Generator: Creates vector embeddings for transcript segments
- Metadata Processor: Associates metadata with embeddings

**Key Functions**:
- `segment_transcript(transcript)`: Splits transcript into logical segments
- `generate_embeddings(segments)`: Creates embeddings for each segment
- `associate_metadata(segments, embeddings, video_data)`: Links metadata with embeddings

### 3. Data Storage Module

**Purpose**: Store videos, transcripts, embeddings, and metadata.

**Components**:
- Video Database: Stores video metadata
- Transcript Database: Stores processed transcript segments
- Vector Index: Stores embeddings for efficient similarity search

**Key Functions**:
- `store_video_metadata(video_data)`: Saves video metadata to database
- `store_transcript_segments(segments)`: Saves transcript segments to database
- `build_vector_index(embeddings, metadata)`: Creates and maintains vector index

### 4. Query Engine Module

**Purpose**: Process user queries and generate answers.

**Components**:
- Query Processor: Converts user questions into embeddings
- Similarity Searcher: Finds relevant transcript segments
- Answer Generator: Creates answers using OpenAI API

**Key Functions**:
- `process_query(question)`: Converts question to embedding
- `search_similar_segments(query_embedding)`: Finds relevant segments
- `generate_answer(question, context)`: Creates answer using OpenAI API

### 5. API Layer

**Purpose**: Provide RESTful API endpoints for frontend and external services.

**Components**:
- FastAPI Application: Handles HTTP requests and responses
- Authentication Handler: Manages API keys and security
- Request Validator: Validates incoming requests

**Key Endpoints**:
- `/api/videos`: Endpoints for video management
- `/api/ask`: Endpoint for question answering
- `/api/admin`: Endpoints for system administration

### 6. Frontend Module

**Purpose**: Provide user interface for interacting with the system.

**Components**:
- Streamlit Application: Simple web interface for demonstration
- Query Interface: Allows users to ask questions
- Results Display: Shows answers with references

## Data Flow

1. **Ingestion Flow**:
   - System retrieves videos from YouTube channel
   - Transcripts are extracted and validated
   - Video metadata and transcripts are stored

2. **Processing Flow**:
   - Transcripts are segmented into chunks
   - Embeddings are generated for each segment
   - Vector index is built from embeddings

3. **Query Flow**:
   - User submits question via frontend
   - Question is converted to embedding
   - Similar segments are retrieved from vector index
   - Context is constructed from segments
   - Answer is generated using OpenAI API
   - Response with answer and references is returned to user

## Technical Stack

- **Backend**: Python, FastAPI
- **Frontend**: Streamlit
- **Databases**: SQLite (development), PostgreSQL (production)
- **Vector Search**: FAISS
- **Embedding Models**: Hugging Face Sentence Transformers
- **LLM Integration**: OpenAI API
- **API Integration**: YouTube Data API

## Scalability Considerations

- **Horizontal Scaling**: API layer can be scaled horizontally
- **Batch Processing**: Video processing can be done in batches
- **Caching**: Implement caching for common queries
- **Background Tasks**: Use background workers for processing tasks

## Security Considerations

- **API Key Management**: Secure storage of YouTube and OpenAI API keys
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **Input Validation**: Validate all user inputs
- **Error Handling**: Proper error handling to prevent information leakage

## Deployment Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Web Server    │────▶│  API Server     │────▶│  Database Server│
│   (Nginx)       │     │  (FastAPI)      │     │  (PostgreSQL)   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │                 │
                        │  Worker Servers │
                        │  (Background    │
                        │   Processing)   │
                        │                 │
                        └─────────────────┘
```
