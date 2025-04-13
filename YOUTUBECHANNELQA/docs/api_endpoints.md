# API Endpoints Design

This document defines the RESTful API endpoints for the YouTube Q&A system, including request/response formats, authentication, and error handling.

## Base URL

```
/api/v1
```

## Authentication

All API endpoints require authentication using an API key provided in the request header:

```
Authorization: Bearer {api_key}
```

## Endpoints

### Video Management

#### List Videos

```
GET /videos
```

Query Parameters:
- `channel_id` (optional): Filter by YouTube channel ID
- `limit` (optional): Maximum number of results (default: 20)
- `offset` (optional): Pagination offset (default: 0)

Response:
```json
{
  "total": 100,
  "limit": 20,
  "offset": 0,
  "videos": [
    {
      "id": "abc123",
      "title": "Video Title",
      "description": "Video description",
      "published_at": "2023-01-01T00:00:00Z",
      "thumbnail_url": "https://example.com/thumbnail.jpg",
      "duration": 600,
      "has_transcript": true
    },
    ...
  ]
}
```

#### Get Video Details

```
GET /videos/{video_id}
```

Path Parameters:
- `video_id`: YouTube video ID

Response:
```json
{
  "id": "abc123",
  "title": "Video Title",
  "description": "Video description",
  "published_at": "2023-01-01T00:00:00Z",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "duration": 600,
  "has_transcript": true,
  "channel_id": "channel123",
  "segment_count": 150
}
```

#### Process Videos from Channel

```
POST /videos/process
```

Request Body:
```json
{
  "channel_id": "channel123",
  "max_results": 50
}
```

Response:
```json
{
  "task_id": "task123",
  "status": "processing",
  "message": "Processing videos from channel",
  "estimated_completion": "2023-01-01T01:00:00Z"
}
```

#### Get Video Transcript Segments

```
GET /videos/{video_id}/segments
```

Path Parameters:
- `video_id`: YouTube video ID

Query Parameters:
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

Response:
```json
{
  "video_id": "abc123",
  "total_segments": 150,
  "limit": 100,
  "offset": 0,
  "segments": [
    {
      "id": "seg123",
      "text": "Transcript segment text",
      "start_time": 10.5,
      "duration": 5.2
    },
    ...
  ]
}
```

### Question Answering

#### Ask Question

```
POST /ask
```

Request Body:
```json
{
  "question": "What is the recommended company valuation multiple?",
  "k": 5,
  "model": "gpt-3.5-turbo"
}
```

Response:
```json
{
  "question": "What is the recommended company valuation multiple?",
  "answer": "Based on the referenced content, the recommended valuation multiple is around 4-6x EBITDA.",
  "references": [
    {
      "video_id": "abc123",
      "video_title": "Video Title",
      "segment_id": "seg123",
      "text": "The recommended valuation multiple is typically 4-6x EBITDA for most businesses.",
      "start_time": 120.5,
      "link": "https://www.youtube.com/watch?v=abc123&t=120"
    },
    ...
  ]
}
```

### System Management

#### Get System Status

```
GET /status
```

Response:
```json
{
  "status": "healthy",
  "video_count": 100,
  "segment_count": 15000,
  "embedding_model": "all-MiniLM-L6-v2",
  "last_update": "2023-01-01T00:00:00Z",
  "api_version": "1.0.0"
}
```

#### Rebuild Vector Index

```
POST /reindex
```

Request Body:
```json
{
  "force": true,
  "model": "all-MiniLM-L6-v2"
}
```

Response:
```json
{
  "task_id": "task456",
  "status": "processing",
  "message": "Rebuilding vector index",
  "estimated_completion": "2023-01-01T02:00:00Z"
}
```

#### Get Task Status

```
GET /tasks/{task_id}
```

Path Parameters:
- `task_id`: Task identifier

Response:
```json
{
  "task_id": "task123",
  "status": "completed",
  "message": "Task completed successfully",
  "progress": 100,
  "result": {
    "processed_videos": 50,
    "failed_videos": 2,
    "total_segments": 7500
  }
}
```

## Error Handling

All API endpoints use standard HTTP status codes and return error details in a consistent format:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Invalid request parameters",
    "details": {
      "field": "channel_id",
      "issue": "Channel ID is required"
    }
  }
}
```

Common error codes:
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid API key
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- Public endpoints: 60 requests per minute
- Authenticated endpoints: 300 requests per minute

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 299
X-RateLimit-Reset: 1609459200
```

## Pagination

List endpoints support pagination using `limit` and `offset` parameters:

- `limit`: Maximum number of results to return (default varies by endpoint)
- `offset`: Number of results to skip (default: 0)

Response includes pagination metadata:
```json
{
  "total": 100,
  "limit": 20,
  "offset": 0,
  "items": [...]
}
```

## Versioning

API is versioned in the URL path (`/api/v1`). Breaking changes will be introduced in new API versions.

## CORS

API supports Cross-Origin Resource Sharing (CORS) for browser-based clients:

- Allowed origins: Configurable in server settings
- Allowed methods: GET, POST, OPTIONS
- Allowed headers: Content-Type, Authorization

## Documentation

API documentation is available using OpenAPI/Swagger:

- OpenAPI specification: `/api/v1/openapi.json`
- Swagger UI: `/api/v1/docs`
- ReDoc: `/api/v1/redoc`
