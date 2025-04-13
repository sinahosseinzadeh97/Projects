# Module Interfaces and Data Flow

This document defines the interfaces between modules and the data flow throughout the YouTube Q&A system.

## Data Structures

### Video Metadata
```python
class VideoMetadata:
    video_id: str           # YouTube video ID
    title: str              # Video title
    description: str        # Video description
    published_at: datetime  # Publication date
    channel_id: str         # YouTube channel ID
    thumbnail_url: str      # URL to video thumbnail
```

### Transcript Segment
```python
class TranscriptSegment:
    segment_id: str         # Unique identifier for segment
    video_id: str           # Associated video ID
    text: str               # Segment text content
    start_time: float       # Start time in seconds
    duration: float         # Duration in seconds
```

### Embedding
```python
class Embedding:
    segment_id: str         # Associated segment ID
    vector: np.ndarray      # Embedding vector
    dimension: int          # Vector dimension
```

### Query
```python
class Query:
    question: str           # User question
    embedding: np.ndarray   # Question embedding
```

### SearchResult
```python
class SearchResult:
    segment_id: str         # Segment ID
    text: str               # Segment text
    video_id: str           # Video ID
    video_title: str        # Video title
    start_time: float       # Start time in seconds
    similarity: float       # Similarity score
```

### Answer
```python
class Answer:
    question: str           # Original question
    answer_text: str        # Generated answer
    references: List[SearchResult]  # Supporting references
```

## Module Interfaces

### 1. Data Ingestion Module

#### Input:
- Channel ID or Video IDs

#### Output:
- List of VideoMetadata objects
- Dictionary mapping video_id to transcript data

#### Interface:
```python
def fetch_channel_videos(channel_id: str, max_results: int = 50) -> List[VideoMetadata]:
    """Fetch videos from a YouTube channel."""
    pass

def extract_transcript(video_id: str) -> List[dict]:
    """Extract transcript for a specific video."""
    pass

def validate_and_clean_data(video_data: VideoMetadata, transcript_data: List[dict]) -> Tuple[VideoMetadata, List[dict]]:
    """Validate and clean the retrieved data."""
    pass
```

### 2. Data Processing Module

#### Input:
- VideoMetadata objects
- Raw transcript data

#### Output:
- TranscriptSegment objects
- Embedding objects

#### Interface:
```python
def segment_transcript(transcript: List[dict], video_id: str) -> List[TranscriptSegment]:
    """Split transcript into logical segments."""
    pass

def generate_embeddings(segments: List[TranscriptSegment], model_name: str = "all-MiniLM-L6-v2") -> List[Embedding]:
    """Create embeddings for each segment."""
    pass

def associate_metadata(segments: List[TranscriptSegment], embeddings: List[Embedding], 
                       video_data: VideoMetadata) -> Tuple[List[TranscriptSegment], List[Embedding]]:
    """Link metadata with embeddings."""
    pass
```

### 3. Data Storage Module

#### Input:
- VideoMetadata objects
- TranscriptSegment objects
- Embedding objects

#### Output:
- Success/failure status
- Database IDs

#### Interface:
```python
def store_video_metadata(video_data: List[VideoMetadata]) -> List[str]:
    """Save video metadata to database."""
    pass

def store_transcript_segments(segments: List[TranscriptSegment]) -> List[str]:
    """Save transcript segments to database."""
    pass

def build_vector_index(embeddings: List[Embedding], metadata: List[dict]) -> bool:
    """Create and maintain vector index."""
    pass

def save_vector_index(index_path: str) -> bool:
    """Save vector index to disk."""
    pass

def load_vector_index(index_path: str) -> Any:
    """Load vector index from disk."""
    pass
```

### 4. Query Engine Module

#### Input:
- User question (string)
- Vector index

#### Output:
- Answer object with references

#### Interface:
```python
def process_query(question: str, model_name: str = "all-MiniLM-L6-v2") -> Query:
    """Convert question to embedding."""
    pass

def search_similar_segments(query_embedding: np.ndarray, index, k: int = 5) -> List[SearchResult]:
    """Find relevant segments."""
    pass

def generate_answer(question: str, context: str, model: str = "gpt-3.5-turbo") -> str:
    """Create answer using OpenAI API."""
    pass

def format_response(question: str, answer: str, references: List[SearchResult]) -> Answer:
    """Format the final response with references."""
    pass
```

### 5. API Layer

#### Endpoints:

##### Videos Management
```
GET /api/videos
    - List all processed videos
    - Query params: channel_id, limit, offset

POST /api/videos/process
    - Process new videos from a channel
    - Body: {channel_id: string, max_results: number}

GET /api/videos/{video_id}
    - Get details for a specific video
    - Path params: video_id

GET /api/videos/{video_id}/segments
    - Get transcript segments for a video
    - Path params: video_id
    - Query params: limit, offset
```

##### Question Answering
```
POST /api/ask
    - Ask a question
    - Body: {question: string, k: number}
    - Returns: {answer: string, references: Array}
```

##### System Management
```
GET /api/status
    - Get system status
    - Returns: {status: string, video_count: number, segment_count: number}

POST /api/reindex
    - Rebuild vector index
    - Body: {force: boolean}
```

### 6. Frontend Module

#### Components:
- Channel Selection: Input for YouTube channel URL
- Video Processing: Button to trigger video processing
- Question Input: Text field for user questions
- Answer Display: Area to show generated answers
- Reference Display: Section showing source videos with timestamps

## Data Flow Sequence Diagrams

### Video Processing Flow

```
User -> Frontend: Enter channel ID
Frontend -> API: POST /api/videos/process
API -> DataIngestion: fetch_channel_videos()
DataIngestion -> YouTube API: Request videos
YouTube API -> DataIngestion: Return video data
DataIngestion -> API: Return video metadata
API -> DataIngestion: extract_transcript() for each video
DataIngestion -> YouTube: Request transcripts
YouTube -> DataIngestion: Return transcripts
DataIngestion -> DataProcessing: segment_transcript()
DataProcessing -> DataProcessing: generate_embeddings()
DataProcessing -> DataStorage: store_video_metadata()
DataStorage -> Database: Save video data
DataProcessing -> DataStorage: store_transcript_segments()
DataStorage -> Database: Save segments
DataProcessing -> DataStorage: build_vector_index()
DataStorage -> VectorDB: Save embeddings
API -> Frontend: Return processing status
Frontend -> User: Display processing results
```

### Question Answering Flow

```
User -> Frontend: Enter question
Frontend -> API: POST /api/ask
API -> QueryEngine: process_query()
QueryEngine -> QueryEngine: Convert to embedding
QueryEngine -> DataStorage: Load vector index
DataStorage -> QueryEngine: Return index
QueryEngine -> QueryEngine: search_similar_segments()
QueryEngine -> DataStorage: Get segment details
DataStorage -> QueryEngine: Return segment data
QueryEngine -> QueryEngine: Construct context
QueryEngine -> OpenAI API: generate_answer()
OpenAI API -> QueryEngine: Return generated answer
QueryEngine -> QueryEngine: format_response()
API -> Frontend: Return answer with references
Frontend -> User: Display answer and references
```

## Error Handling

1. **Missing Transcripts**:
   - If a video has no transcript, log warning and skip
   - Return appropriate error message to user

2. **API Failures**:
   - Implement retry logic for transient failures
   - Log errors and provide meaningful error messages

3. **Processing Errors**:
   - Gracefully handle processing failures
   - Maintain system state consistency

4. **Query Errors**:
   - Handle malformed queries
   - Provide feedback when no relevant content is found

## Caching Strategy

1. **API Response Caching**:
   - Cache YouTube API responses to reduce quota usage
   - Set appropriate TTL based on data freshness requirements

2. **Embedding Caching**:
   - Cache embeddings to avoid recomputation
   - Invalidate cache when models change

3. **Query Result Caching**:
   - Cache common queries and their results
   - Implement LRU cache with size limits
