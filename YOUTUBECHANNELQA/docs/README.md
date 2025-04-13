# YouTube Q&A System Documentation

## Overview

The YouTube Q&A System is an interactive question-answering tool that allows users to ask questions about content from educational YouTube channels. The system retrieves relevant information from video transcripts and generates accurate answers with references back to the original source videos.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [API Reference](#api-reference)
6. [Module Documentation](#module-documentation)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [Future Enhancements](#future-enhancements)

## System Architecture

The YouTube Q&A System follows a modular architecture with the following components:

1. **YouTube API Module**: Retrieves videos and metadata from YouTube channels
2. **Transcript Extraction Module**: Extracts and processes transcripts from YouTube videos
3. **Embedding Generation Module**: Generates vector embeddings for transcript segments using Hugging Face models
4. **Vector Search Module**: Indexes and searches transcript embeddings using FAISS
5. **OpenAI Integration Module**: Generates answers based on relevant transcript segments
6. **FastAPI Backend**: Provides REST API endpoints for the system
7. **Streamlit Frontend**: Offers a user-friendly web interface

The system workflow is as follows:

1. User selects a YouTube channel or provides specific videos
2. System retrieves videos and extracts transcripts
3. Transcripts are segmented and converted to vector embeddings
4. User asks a question
5. System finds relevant transcript segments using vector similarity search
6. OpenAI generates an answer based on the relevant segments
7. Answer is presented to the user with references to source videos

## Installation

### Prerequisites

- Python 3.10 or higher
- YouTube Data API v3 key
- OpenAI API key

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/youtube-qa-system.git
   cd youtube-qa-project
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Set up environment variables for API keys:
   ```
   export YOUTUBE_API_KEY="your_youtube_api_key"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

   On Windows:
   ```
   set YOUTUBE_API_KEY=your_youtube_api_key
   set OPENAI_API_KEY=your_openai_api_key
   ```

   Alternatively, you can provide these keys through the settings page in the UI.

2. Configuration options can be modified in the settings page of the Streamlit UI.

## Usage

### Running the System

Run both the backend and frontend:
```
python run.py
```

Run only the backend:
```
python run.py --backend-only
```

Run only the frontend:
```
python run.py --frontend-only
```

### Using the Web Interface

1. Open your browser and navigate to `http://localhost:8501`
2. Go to the Settings page to configure API keys and system settings
3. Process a YouTube channel by entering its ID or URL
4. Navigate to the Ask page to ask questions about the video content
5. View answers with references to the original videos

## API Reference

The system provides a REST API with the following endpoints:

### Status

```
GET /api/v1/status
```

Returns the current system status, including the number of processed videos and segments.

### Videos

```
GET /api/v1/videos
```

Lists all processed videos with optional filtering by channel ID.

Parameters:
- `channel_id` (optional): Filter videos by channel ID
- `limit` (optional): Maximum number of videos to return (default: 20)
- `offset` (optional): Pagination offset (default: 0)

```
GET /api/v1/videos/{video_id}
```

Returns details for a specific video.

```
POST /api/v1/videos/process
```

Processes videos from a YouTube channel.

Request body:
```json
{
  "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
  "max_results": 50
}
```

### Tasks

```
GET /api/v1/tasks/{task_id}
```

Returns the status of a background task.

### Questions

```
POST /api/v1/ask
```

Asks a question about the video content.

Request body:
```json
{
  "question": "What is the recommended valuation multiple?",
  "k": 5,
  "model": "gpt-3.5-turbo"
}
```

## Module Documentation

### YouTube API Module

The YouTube API module (`youtube_client.py`) provides functionality to interact with the YouTube Data API v3 to retrieve videos and their metadata from a specified channel.

Key functions:
- `get_channel_videos`: Retrieves videos from a specific YouTube channel
- `get_video_details`: Gets detailed information about a specific video
- `get_channel_id_from_url`: Extracts channel ID from a YouTube channel URL

### Transcript Extraction Module

The Transcript Extraction module (`transcript_extractor.py`) provides functionality to extract and process transcripts from YouTube videos.

Key functions:
- `get_transcript`: Extracts transcript for a specific YouTube video
- `get_transcript_as_text`: Extracts transcript as plain text
- `segment_transcript`: Splits transcript into logical segments for embedding
- `generate_video_url_with_timestamp`: Generates a YouTube URL with timestamp

### Embedding Generation Module

The Embedding Generation module (`embedding_generator.py`) provides functionality to generate embeddings for transcript segments using Hugging Face's Sentence Transformers models.

Key functions:
- `generate_embedding`: Generates embedding for a single text segment
- `generate_embeddings`: Generates embeddings for multiple text segments
- `generate_embeddings_for_segments`: Generates embeddings for transcript segments
- `compute_similarity`: Computes cosine similarity between two embeddings

### Vector Search Module

The Vector Search module (`vector_search_engine.py`) provides functionality to create and search FAISS indexes for efficient similarity search of transcript segment embeddings.

Key functions:
- `create_index`: Creates a FAISS index from embeddings
- `add_embeddings`: Adds embeddings and their metadata to the index
- `search`: Searches for similar vectors in the index
- `save`: Saves the index and metadata to disk
- `load`: Loads the index and metadata from disk

### OpenAI Integration Module

The OpenAI Integration module (`openai_generator.py`) provides functionality to generate answers to user questions using the OpenAI API based on relevant transcript segments.

Key functions:
- `generate_answer`: Generates an answer to a question based on provided context
- `format_context_from_segments`: Formats transcript segments into a context string
- `generate_answer_with_references`: Generates an answer with references to source videos

## Testing

The system includes comprehensive unit tests and integration tests for all modules.

Run all tests:
```
python -m unittest discover tests
```

Run a specific test:
```
python -m unittest tests.test_youtube_api
```

## Deployment

### Local Deployment

Follow the installation and usage instructions above to deploy the system locally.

### Cloud Deployment

The system can be deployed to cloud platforms like AWS, GCP, or Azure:

1. **Backend (FastAPI)**:
   - Deploy as a containerized application using Docker
   - Use services like AWS ECS, GCP Cloud Run, or Azure Container Instances

2. **Frontend (Streamlit)**:
   - Deploy using Streamlit Sharing or as a containerized application
   - Ensure the frontend can communicate with the backend API

3. **Vector Database**:
   - For production use, consider using managed vector database services like Pinecone or Weaviate instead of FAISS

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Ensure both YouTube API and OpenAI API keys are correctly set
   - Check API key permissions and quotas

2. **Transcript Extraction Failures**:
   - Some videos may not have transcripts available
   - Try different language options if available

3. **Memory Issues with FAISS**:
   - For large collections, use more efficient index types like IVF or HNSW
   - Consider sharding the index for very large collections

4. **OpenAI API Rate Limits**:
   - Implement caching for common questions
   - Add rate limiting in the application

## Future Enhancements

1. **Multi-language Support**:
   - Add support for non-English videos and questions

2. **Advanced Filtering**:
   - Filter videos by topic, date, or other metadata

3. **User Feedback Loop**:
   - Allow users to rate answers and provide feedback

4. **Custom Embedding Models**:
   - Support for fine-tuned embedding models specific to the channel's content

5. **Persistent Storage**:
   - Replace in-memory storage with a proper database

6. **Authentication and User Management**:
   - Add user accounts and personalized settings

7. **Mobile Application**:
   - Develop native mobile applications for iOS and Android
