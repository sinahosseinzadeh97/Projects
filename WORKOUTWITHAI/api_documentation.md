# Fitness App API Documentation

This document provides detailed information about the Fitness App API endpoints, request/response formats, and usage examples.

## Base URL

- Local Development: `http://localhost:8000`
- Production: Depends on your Kubernetes service configuration

## Authentication

The API uses JWT (JSON Web Token) for authentication. To access protected endpoints, you need to:

1. Obtain a token using the `/token` endpoint
2. Include the token in the `Authorization` header of subsequent requests:
   ```
   Authorization: Bearer <your_token>
   ```

## Endpoints

### Health Check

```
GET /health
```

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

### Authentication

```
POST /token
```

Obtain an access token.

**Request:**
```
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"
```

### User Management

#### Create User

```
POST /users/
```

Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "is_active": true
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"username","password":"password123"}'
```

#### Get Current User

```
GET /users/me/
```

Get information about the currently authenticated user.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "is_active": true
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/users/me/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Workout Management

#### Create Workout

```
POST /workouts/
```

Upload a workout video and create a workout record.

**Request:**
```
Content-Type: multipart/form-data

title: Morning Workout
description: Full body workout session
workout_type: strength
video: [binary file]
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Morning Workout",
  "description": "Full body workout session",
  "workout_type": "strength",
  "video_path": "uploads/8f7d1c4e-5a2b-4f1b-9c8d-3e7f6a5b4c3d.mp4",
  "created_at": "2025-04-11T09:30:00.000Z",
  "analysis_status": "pending",
  "analysis_results": null
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/workouts/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "title=Morning Workout" \
  -F "description=Full body workout session" \
  -F "workout_type=strength" \
  -F "video=@/path/to/workout_video.mp4"
```

#### Get All Workouts

```
GET /workouts/
```

Get all workouts for the current user.

**Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Morning Workout",
    "description": "Full body workout session",
    "workout_type": "strength",
    "video_path": "uploads/8f7d1c4e-5a2b-4f1b-9c8d-3e7f6a5b4c3d.mp4",
    "created_at": "2025-04-11T09:30:00.000Z",
    "analysis_status": "completed",
    "analysis_results": {
      "dominant_exercise": "squat",
      "calories_burned": 150,
      "exercise_counts": {
        "squat": 15,
        "pushup": 10
      }
    }
  }
]
```

**Example:**
```bash
curl -X GET "http://localhost:8000/workouts/?skip=0&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Get Specific Workout

```
GET /workouts/{workout_id}
```

Get details of a specific workout.

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Morning Workout",
  "description": "Full body workout session",
  "workout_type": "strength",
  "video_path": "uploads/8f7d1c4e-5a2b-4f1b-9c8d-3e7f6a5b4c3d.mp4",
  "created_at": "2025-04-11T09:30:00.000Z",
  "analysis_status": "completed",
  "analysis_results": {
    "dominant_exercise": "squat",
    "calories_burned": 150,
    "exercise_counts": {
      "squat": 15,
      "pushup": 10
    }
  }
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/workouts/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### User Statistics

```
GET /users/me/stats
```

Generate statistics for the current user's workouts.

**Response:**
```json
{
  "message": "Statistics generation started",
  "task_id": "8f7d1c4e-5a2b-4f1b-9c8d-3e7f6a5b4c3d"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/users/me/stats" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Error Responses

The API returns appropriate HTTP status codes and error messages:

### 400 Bad Request

```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden

```json
{
  "detail": "Not authorized to access this workout"
}
```

### 404 Not Found

```json
{
  "detail": "Workout not found"
}
```

## API Integration Examples

### Complete User Flow Example

1. Register a new user:
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"username","password":"password123"}'
```

2. Obtain an access token:
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=username&password=password123"
```

3. Upload a workout video:
```bash
curl -X POST "http://localhost:8000/workouts/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "title=Morning Workout" \
  -F "description=Full body workout session" \
  -F "workout_type=strength" \
  -F "video=@/path/to/workout_video.mp4"
```

4. Check workout analysis status:
```bash
curl -X GET "http://localhost:8000/workouts/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

5. Generate user statistics:
```bash
curl -X GET "http://localhost:8000/users/me/stats" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Notes

- Video analysis is performed asynchronously. After uploading a workout video, the `analysis_status` will initially be "pending" and will change to "processing", "completed", or "failed" as the analysis progresses.
- The API uses FastAPI's automatic OpenAPI documentation, which is available at `/docs` and `/redoc` endpoints.
