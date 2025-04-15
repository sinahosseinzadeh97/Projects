# API Documentation

## Overview

The Intelligent Multi-Agent Email Automation System provides a comprehensive RESTful API that allows developers to interact with all aspects of the system. This document details the available endpoints, request/response formats, and authentication requirements.

## Base URL

All API endpoints are relative to the base URL:

```
http://your-server-address:8000
```

For production environments, HTTPS should be used:

```
https://your-server-address
```

## Authentication

### Obtaining an Access Token

All API endpoints (except the health check and root endpoint) require authentication using JWT tokens.

**Endpoint**: `POST /token`

**Request Body**:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes**:
- `200 OK`: Authentication successful
- `401 Unauthorized`: Invalid credentials

### Using the Access Token

Include the access token in the `Authorization` header of all API requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Endpoints

### System Information

#### Get API Information

**Endpoint**: `GET /`

**Description**: Returns basic information about the API.

**Authentication**: Not required

**Response**:
```json
{
  "message": "Welcome to the Intelligent Multi-Agent Email Automation System API",
  "version": "1.0.0",
  "documentation": "/docs"
}
```

**Status Codes**:
- `200 OK`: Request successful

#### Health Check

**Endpoint**: `GET /health`

**Description**: Checks the health status of the API and its dependencies.

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "database": "healthy",
  "cache": "healthy",
  "api": "healthy"
}
```

**Status Codes**:
- `200 OK`: Request successful

#### Get Current User

**Endpoint**: `GET /users/me/`

**Description**: Returns information about the currently authenticated user.

**Authentication**: Required

**Response**:
```json
{
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "disabled": false,
  "roles": ["admin"]
}
```

**Status Codes**:
- `200 OK`: Request successful
- `401 Unauthorized`: Invalid or missing token

### Email Ingestion

#### Create Email Provider

**Endpoint**: `POST /ingestion/providers`

**Description**: Creates a new email provider configuration.

**Authentication**: Required

**Request Body**:
```json
{
  "type": "gmail",
  "server": "imap.gmail.com",
  "username": "your_email@gmail.com",
  "password": "your_password",
  "folder": "INBOX",
  "limit": 10
}
```

**Response**:
```json
{
  "id": "provider_id",
  "type": "gmail",
  "server": "imap.gmail.com",
  "username": "your_email@gmail.com",
  "folder": "INBOX",
  "limit": 10,
  "created_at": "2025-04-14T08:00:00Z"
}
```

**Status Codes**:
- `200 OK`: Provider created successfully
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Invalid or missing token

#### Get Email Providers

**Endpoint**: `GET /ingestion/providers`

**Description**: Returns a list of all email provider configurations.

**Authentication**: Required

**Response**:
```json
[
  {
    "id": "provider_id_1",
    "type": "gmail",
    "server": "imap.gmail.com",
    "username": "your_email@gmail.com",
    "folder": "INBOX",
    "limit": 10,
    "created_at": "2025-04-14T08:00:00Z"
  },
  {
    "id": "provider_id_2",
    "type": "outlook",
    "server": "outlook.office365.com",
    "username": "your_email@outlook.com",
    "folder": "INBOX",
    "limit": 20,
    "created_at": "2025-04-14T09:00:00Z"
  }
]
```

**Status Codes**:
- `200 OK`: Request successful
- `401 Unauthorized`: Invalid or missing token

#### Get Email Provider

**Endpoint**: `GET /ingestion/providers/{provider_id}`

**Description**: Returns a specific email provider configuration.

**Authentication**: Required

**Parameters**:
- `provider_id`: ID of the email provider

**Response**:
```json
{
  "id": "provider_id",
  "type": "gmail",
  "server": "imap.gmail.com",
  "username": "your_email@gmail.com",
  "folder": "INBOX",
  "limit": 10,
  "created_at": "2025-04-14T08:00:00Z"
}
```

**Status Codes**:
- `200 OK`: Request successful
- `404 Not Found`: Provider not found
- `401 Unauthorized`: Invalid or missing token

#### Update Email Provider

**Endpoint**: `PUT /ingestion/providers/{provider_id}`

**Description**: Updates a specific email provider configuration.

**Authentication**: Required

**Parameters**:
- `provider_id`: ID of the email provider

**Request Body**:
```json
{
  "type": "gmail",
  "server": "imap.gmail.com",
  "username": "your_email@gmail.com",
  "password": "your_new_password",
  "folder": "INBOX",
  "limit": 15
}
```

**Response**:
```json
{
  "id": "provider_id",
  "type": "gmail",
  "server": "imap.gmail.com",
  "username": "your_email@gmail.com",
  "folder": "INBOX",
  "limit": 15,
  "created_at": "2025-04-14T08:00:00Z"
}
```

**Status Codes**:
- `200 OK`: Provider updated successfully
- `400 Bad Request`: Invalid request body
- `404 Not Found`: Provider not found
- `401 Unauthorized`: Invalid or missing token

#### Delete Email Provider

**Endpoint**: `DELETE /ingestion/providers/{provider_id}`

**Description**: Deletes a specific email provider configuration.

**Authentication**: Required

**Parameters**:
- `provider_id`: ID of the email provider

**Response**:
```json
{
  "message": "Provider deleted successfully"
}
```

**Status Codes**:
- `200 OK`: Provider deleted successfully
- `404 Not Found`: Provider not found
- `401 Unauthorized`: Invalid or missing token

#### Fetch Emails

**Endpoint**: `POST /ingestion/fetch`

**Description**: Fetches emails from a specific provider.

**Authentication**: Required

**Request Body**:
```json
{
  "provider_id": "provider_id",
  "limit": 10
}
```

**Response**:
```json
{
  "emails_fetched": 5,
  "provider_id": "provider_id",
  "status": "success"
}
```

**Status Codes**:
- `200 OK`: Emails fetched successfully
- `400 Bad Request`: Invalid request body
- `404 Not Found`: Provider not found
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Error fetching emails

### Classification

#### Classify Email

**Endpoint**: `POST /classification/classify`

**Description**: Classifies an email into predefined categories.

**Authentication**: Required

**Request Body**:
```json
{
  "message_id": "message_id",
  "subject": "Project Update Meeting",
  "from_address": "john.doe@example.com",
  "to": "recipient@example.com",
  "cc": "team@example.com",
  "body": "Hello team,\n\nLet's schedule a project update meeting for tomorrow at 2 PM. We need to discuss the current progress and next steps.\n\nRegards,\nJohn",
  "attachments": []
}
```

**Response**:
```json
{
  "message_id": "message_id",
  "predicted_category": "important",
  "confidence": 0.85,
  "category_probabilities": {
    "important": 0.85,
    "promotional": 0.05,
    "support": 0.07,
    "spam": 0.01,
    "other": 0.02
  }
}
```

**Status Codes**:
- `200 OK`: Email classified successfully
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Error classifying email

#### Get Classification Categories

**Endpoint**: `GET /classification/categories`

**Description**: Returns the list of available classification categories.

**Authentication**: Required

**Response**:
```json
{
  "categories": ["important", "promotional", "support", "spam", "other"]
}
```

**Status Codes**:
- `200 OK`: Request successful
- `401 Unauthorized`: Invalid or missing token

### Summarization

#### Summarize Email

**Endpoint**: `POST /summarization/summarize`

**Description**: Generates a summary of an email.

**Authentication**: Required

**Request Body**:
```json
{
  "message_id": "message_id",
  "subject": "Project Update Meeting",
  "from_address": "john.doe@example.com",
  "to": "recipient@example.com",
  "cc": "team@example.com",
  "body": "Hello team,\n\nLet's schedule a project update meeting for tomorrow at 2 PM. We need to discuss the current progress and next steps.\n\nRegards,\nJohn",
  "attachments": [],
  "classification": {
    "predicted_category": "important",
    "confidence": 0.85
  }
}
```

**Response**:
```json
{
  "message_id": "message_id",
  "summary": "Project update meeting scheduled for tomorrow at 2 PM to discuss progress and next steps."
}
```

**Status Codes**:
- `200 OK`: Email summarized successfully
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Error summarizing email

#### Extract Data

**Endpoint**: `POST /summarization/extract`

**Description**: Extracts key data points from an email.

**Authentication**: Required

**Request Body**:
```json
{
  "message_id": "message_id",
  "subject": "Project Update Meeting",
  "from_address": "john.doe@example.com",
  "to": "recipient@example.com",
  "cc": "team@example.com",
  "body": "Hello team,\n\nLet's schedule a project update meeting for tomorrow at 2 PM. We need to discuss the current progress and next steps.\n\nRegards,\nJohn",
  "attachments": [],
  "classification": {
    "predicted_category": "important",
    "confidence": 0.85
  }
}
```

**Response**:
```json
{
  "message_id": "message_id",
  "extractions": {
    "dates_times": [
      {
        "text": "tomorrow at 2 PM",
        "type": "datetime"
      }
    ],
    "contacts": [
      {
        "text": "John",
        "type": "person"
      }
    ],
    "tasks": [
      {
        "text": "discuss the current progress and next steps",
        "type": "task"
      }
    ]
  }
}
```

**Status Codes**:
- `200 OK`: Data extracted successfully
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Error extracting data

### Response Generation

#### Generate Response

**Endpoint**: `POST /response/generate`

**Description**: Generates a response to an email.

**Authentication**: Required

**Request Body**:
```json
{
  "message_id": "message_id",
  "subject": "Project Update Meeting",
  "from_address": "john.doe@example.com",
  "to": "recipient@example.com",
  "cc": "team@example.com",
  "body": "Hello team,\n\nLet's schedule a project update meeting for tomorrow at 2 PM. We need to discuss the current progress and next steps.\n\nRegards,\nJohn",
  "attachments": [],
  "classification": {
    "predicted_category": "important",
    "confidence": 0.85
  },
  "processed_data": {
    "summary": "Project update meeting scheduled for tomorrow at 2 PM to discuss progress and next steps.",
    "extractions": {
      "dates_times": [
        {
          "text": "tomorrow at 2 PM",
          "type": "datetime"
        }
      ],
      "contacts": [
        {
          "text": "John",
          "type": "person"
        }
      ],
      "tasks": [
        {
          "text": "discuss the current progress and next steps",
          "type": "task"
        }
      ]
    }
  }
}
```

**Response**:
```json
{
  "message_id": "message_id",
  "response_text": "Thank you for your important message. I've reviewed it and noted the project update meeting scheduled for tomorrow at 2 PM to discuss progress and next steps. I'll attend as requested.",
  "auto_send": true,
  "confidence": 0.92,
  "category": "important",
  "generation_timestamp": "2025-04-14T08:30:00Z"
}
```

**Status Codes**:
- `200 OK`: Response generated successfully
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Error generating response

#### Get Response Templates

**Endpoint**: `GET /response/templates`

**Description**: Returns the list of available response templates.

**Authentication**: Required

**Query Parameters**:
- `category` (optional): Filter templates by category

**Response**:
```json
[
  {
    "id": "template_id_1",
    "category": "important",
    "template": "Thank you for your important message. I've reviewed it and {summary}. I'll {action} as requested.",
    "timestamp": "2025-04-14T08:00:00Z"
  },
  {
    "id": "template_id_2",
    "category": "support",
    "template": "Thank you for reaching out to our support team. I understand that {summary}. We'll {action} to resolve this issue.",
    "timestamp": "2025-04-14T08:00:00Z"
  }
]
```

**Status Codes**:
- `200 OK`: Request successful
- `401 Unauthorized`: Invalid or missing token

#### Create Response Template

**Endpoint**: `POST /response/templates`

**Description**: Creates a new response template.

**Authentication**: Required

**Request Body**:
```json
{
  "category": "important",
  "template": "Thank you for your important message. I've reviewed it and {summary}. I'll {action} as requested."
}
```

**Response**:
```json
{
  "id": "template_id",
  "category": "important",
  "template": "Thank you for your important message. I've reviewed it and {summary}. I'll {action} as requested.",
  "timestamp": "2025-04-14T08:30:00Z"
}
```

**Status Codes**:
- `200 OK`: Template created successfully
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Invalid or missing token

### Integration

#### Create Calendar Event

**Endpoint**: `POST /integration/calendar`

**Description**: Creates a calendar event based on email content.

**Authentication**: Required

**Request Body**:
```json
{
  "message_id": "message_id",
  "subject": "Project Update Meeting",
  "from_address": "john.doe@example.com",
  "to": "recipient@example.com",
  "cc": "team@example.com",
  "body": "Hello team,\n\nLet's schedule a project update meeting for tomorrow at 2 PM. We need to discuss the current progress and next steps.\n\nRegards,\nJohn",
  "attachments": [],
  "classification": {
    "predicted_category": "important",
    "confidence": 0.85
  },
  "processed_data": {
    "summary": "Project update meeting scheduled for tomorrow at 2 PM to discuss progress and next steps.",
    "extractions": {
      "dates_times": [
        {
          "text": "tomorrow at 2 PM",
          "type": "datetime"
        }
      ],
      "contacts": [
        {
          "text": "John",
          "type": "person"
        }
      ],
      "tasks": [
        {
          "text": "discuss the current progress and next steps",
          "type": "task"
        }
      ]
    }
  }
}
```

**Response**:
```json
{
  "service": "google_calendar",
  "events_created": [
    {
      "id": "event_id",
      "title": "Project Update Meeting",
      "datetime": "2025-04-15T14:00:00Z",
      "description": "Project update meeting to discuss progress and next steps.",
      "attendees": ["john.doe@example.com", "recipient@example.com", "team@example.com"],
      "location": null,
      "duration_minutes": 60
    }
  ],
  "status": "success",
  "timestamp": "2025-04-14T08:30:00Z"
}
```

**Status Codes**:
- `200 OK`: Calendar event created successfully
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Error creating calendar event

#### Update CRM Contacts

**Endpoint**: `POST /integration/crm`

**Description**: Updates CRM contacts based on email content.

**Authentication**: Required

**Request Body**:
```json
{
  "message_id": "message_id",
  "subject": "Project Update Meeting",
  "from_address": "john.doe@example.com",
  "to": "recipient@example.com",
  "cc": "team@example.com",
  "body": "Hello team,\n\nLet's schedule a project update meeting for tomorrow at 2 PM. We need to discuss the current progress and next steps.\n\nRegards,\nJohn",
  "attachments": [],
  "classification": {
    "predicted_category": "important",
    "confidence": 0.85
  },
  "processed_data": {
    "summary": "Project update meeting scheduled for tomorrow at 2 PM to discuss progress and next steps.",
    "extractions": {
      "dates_times": [
        {
          "text": "tomorrow at 2 PM",
          "type": "da
(Content truncated due to size limit. Use line ranges to read in chunks)