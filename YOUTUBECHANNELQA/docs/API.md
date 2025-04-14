# API Documentation

## Overview

The YouTube Q&A System provides a REST API built with FastAPI that allows developers to integrate the question-answering functionality into their own applications. This document provides detailed information about the available endpoints, request/response formats, and authentication.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

API requests require an API key for authentication. The key should be included in the request header:

```
Authorization: Bearer YOUR_API_KEY
```

In the current implementation, API keys are configured through environment variables. In a production environment, this would be replaced with a proper authentication system.

## Endpoints

### Status

#### Get System Status

```
GET /status
```

Returns the current system status, including the number of processed videos and segments.

**Response**

```json
{
  "status": "healthy",
  "video_count": 25,
  "segment_count": 1250,
  "embedding_model": "all-MiniLM-L6-v2",
  "last_update": "2023-01-01T00:00:00Z"
}
```

### Videos

#### List Videos

```
GET /videos
```

Lists all processed videos with optional filtering by channel ID.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| channel_id | string | (Optional) Filter videos by channel ID |
| limit | integer | (Optional) Maximum number of videos to return (default: 20) |
| offset | integer | (Optional) Pagination offset (default: 0) |

**Response**

```json
[
  {
    "id": "abc123",
    "title": "Business Valuation Explained",
    "description": "Learn how to value a business...",
    "published_at": "2023-01-01T00:00:00Z",
    "thumbnail_url": "https://example.com/thumb1.jpg",
    "duration": "PT5M30S",
    "channel_title": "Business Education"
  },
  {
    "id": "def456",
    "title": "Selling Your Business",
    "description": "Tips for selling your business...",
    "published_at": "2023-01-02T00:00:00Z",
    "thumbnail_url": "https://example.com/thumb2.jpg",
    "duration": "PT10M15S",
    "channel_title": "Business Education"
  }
]
```

#### Get Video Details

```
GET /videos/{video_id}
```

Returns details for a specific video.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| video_id | string | YouTube video ID |

**Response**

```json
{
  "id": "abc123",
  "title": "Business Valuation Explained",
  "description": "Learn how to value a business...",
  "published_at": "2023-01-01T00:00:00Z",
  "thumbnail_url": "https://example.com/thumb1.jpg",
  "duration": "PT5M30S",
  "channel_title": "Business Education"
}
```

#### Process Videos

```
POST /videos/process
```

Processes videos from a YouTube channel.

**Request Body**

```json
{
  "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
  "max_results": 50
}
```

**Response**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Processing videos from channel UC_x5XG1OV2P6uZZ5FSM9Ttw"
}
```

### Tasks

#### Get Task Status

```
GET /tasks/{task_id}
```

Returns the status of a background task.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| task_id | string | Task ID returned from /videos/process |

**Response**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "Task completed successfully",
  "progress": 100,
  "result": {
    "processed_videos": 45,
    "failed_videos": 5,
    "total_segments": 2250
  }
}
```

### Questions

#### Ask Question

```
POST /ask
```

Asks a question about the video content.

**Request Body**

```json
{
  "question": "What is the recommended valuation multiple?",
  "k": 5,
  "model": "gpt-3.5-turbo"
}
```

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| question | string | The question to ask |
| k | integer | (Optional) Number of relevant segments to use (default: 5) |
| model | string | (Optional) OpenAI model to use (default: "gpt-3.5-turbo") |

**Response**

```json
{
  "question": "What is the recommended valuation multiple?",
  "answer": "Based on the video content, the recommended valuation multiple for most businesses is typically 4-6x EBITDA. For service businesses specifically, the multiple also ranges between 4-6 times EBITDA, with the exact multiple depending on factors like growth rate and client concentration.",
  "references": [
    {
      "video_id": "abc123",
      "video_title": "Business Valuation Explained",
      "start_time": 135.5,
      "text": "The recommended valuation multiple is typically 4-6x EBITDA for most businesses.",
      "link": "https://www.youtube.com/watch?v=abc123&t=135"
    },
    {
      "video_id": "def456",
      "video_title": "Selling Your Business",
      "start_time": 930.2,
      "text": "For service businesses, expect multiples between 4-6 times EBITDA depending on growth rate and client concentration.",
      "link": "https://www.youtube.com/watch?v=def456&t=930"
    }
  ]
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- 200: Success
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (invalid or missing API key)
- 404: Not Found (resource not found)
- 500: Internal Server Error

Error responses include a JSON object with an error message:

```json
{
  "detail": "Error message describing the problem"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Clients are limited to:

- 100 requests per minute for most endpoints
- 10 requests per minute for the /ask endpoint

When rate limits are exceeded, the API returns a 429 Too Many Requests status code.

## Pagination

List endpoints support pagination using the `limit` and `offset` parameters:

- `limit`: Maximum number of items to return (default: 20, max: 100)
- `offset`: Number of items to skip (default: 0)

## Versioning

The API uses URL versioning (v1) to ensure backward compatibility as new features are added.

## Examples

### Python Example

```python
import requests

API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "your_api_key"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Process videos from a channel
response = requests.post(
    f"{API_BASE_URL}/videos/process",
    headers=headers,
    json={
        "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "max_results": 50
    }
)
task = response.json()
task_id = task["task_id"]

# Check task status
response = requests.get(
    f"{API_BASE_URL}/tasks/{task_id}",
    headers=headers
)
task_status = response.json()

# Ask a question
response = requests.post(
    f"{API_BASE_URL}/ask",
    headers=headers,
    json={
        "question": "What is the recommended valuation multiple?",
        "k": 5,
        "model": "gpt-3.5-turbo"
    }
)
answer = response.json()
print(answer["answer"])
for ref in answer["references"]:
    print(f"Source: {ref['video_title']} at {ref['start_time']}")
    print(f"Link: {ref['link']}")
```

### JavaScript Example

```javascript
const API_BASE_URL = "http://localhost:8000/api/v1";
const API_KEY = "your_api_key";

const headers = {
  "Authorization": `Bearer ${API_KEY}`,
  "Content-Type": "application/json"
};

// Process videos from a channel
fetch(`${API_BASE_URL}/videos/process`, {
  method: "POST",
  headers: headers,
  body: JSON.stringify({
    channel_id: "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    max_results: 50
  })
})
.then(response => response.json())
.then(task => {
  const taskId = task.task_id;
  
  // Check task status
  return fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    headers: headers
  });
})
.then(response => response.json())
.then(taskStatus => {
  console.log("Task status:", taskStatus.status);
  
  // Ask a question
  return fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({
      question: "What is the recommended valuation multiple?",
      k: 5,
      model: "gpt-3.5-turbo"
    })
  });
})
.then(response => response.json())
.then(answer => {
  console.log("Answer:", answer.answer);
  answer.references.forEach(ref => {
    console.log(`Source: ${ref.video_title} at ${ref.start_time}`);
    console.log(`Link: ${ref.link}`);
  });
})
.catch(error => console.error("Error:", error));
```
