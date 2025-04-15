# Intelligent Multi-Agent Email Automation System

## Overview

The Intelligent Multi-Agent Email Automation System is a comprehensive platform that automates email management through multiple specialized agents. The system automatically processes incoming emails by reading, classifying, summarizing, and generating responses with minimal human intervention, while also integrating with external services such as calendars and CRMs to streamline productivity.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Key Features](#key-features)
3. [Components](#components)
   - [Email Ingestion Agent](#email-ingestion-agent)
   - [Classification Agent](#classification-agent)
   - [Summarization & Extraction Agent](#summarization--extraction-agent)
   - [Response Generation Agent](#response-generation-agent)
   - [Integration & Orchestration Agent](#integration--orchestration-agent)
   - [Management Dashboard](#management-dashboard)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [API Reference](#api-reference)
8. [Frontend Guide](#frontend-guide)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)
11. [Security Considerations](#security-considerations)
12. [Future Enhancements](#future-enhancements)

## System Architecture

The system follows a microservices architecture with specialized agents that work together to process emails. Each agent is responsible for a specific task in the email processing pipeline:

![System Architecture](./diagrams/system_architecture.md)

The system uses MongoDB for data storage, Redis for caching, and FastAPI for the backend API. The frontend is built with React and Material-UI.

## Key Features

- **Automated Email Processing**: Automatically retrieve, classify, summarize, and respond to emails
- **Intelligent Classification**: Categorize emails into predefined classes (important, promotional, support, etc.)
- **Smart Summarization**: Generate concise summaries of email content
- **Context-Aware Responses**: Create intelligent reply drafts based on email content and classification
- **External Integrations**: Connect with calendar systems, CRMs, and task managers
- **Management Dashboard**: Monitor system performance and manage email processing
- **Customizable Settings**: Configure system behavior to match specific needs
- **Secure Authentication**: Protect access with JWT-based authentication
- **Comprehensive Analytics**: Track email processing metrics and system performance

## Components

### Email Ingestion Agent

The Email Ingestion Agent connects to email providers, retrieves emails, and prepares them for processing by other agents.

**Key Functions**:
- Connect to email providers using IMAP/SMTP protocols and APIs
- Retrieve emails from multiple accounts and providers
- Parse email content and metadata
- Forward processed emails to subsequent agents

### Classification Agent

The Classification Agent analyzes email content and categorizes emails into predefined classes.

**Key Functions**:
- Analyze email content and metadata
- Classify emails into categories (important, promotional, support, spam, etc.)
- Assign priority levels to emails
- Filter out irrelevant emails

### Summarization & Extraction Agent

The Summarization & Extraction Agent generates concise summaries of email content and extracts key data points.

**Key Functions**:
- Create brief summaries of email content
- Extract important dates, times, and deadlines
- Identify contact information
- Recognize action items and tasks

### Response Generation Agent

The Response Generation Agent creates intelligent and context-aware reply drafts.

**Key Functions**:
- Generate appropriate responses based on email content and classification
- Use templates as starting points for responses
- Provide auto-send recommendations
- Allow for manual review of generated responses

### Integration & Orchestration Agent

The Integration & Orchestration Agent coordinates between agents and manages external integrations.

**Key Functions**:
- Orchestrate the workflow between different agents
- Integrate with calendar systems for scheduling
- Connect with CRMs for contact management
- Link with task management systems
- Handle email sending operations

### Management Dashboard

The Management Dashboard provides a user interface for monitoring and control.

**Key Functions**:
- Display real-time system status and performance metrics
- Allow manual override of automated decisions
- Provide detailed logging and analytics
- Configure system settings and preferences

## Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB 4.4+
- Redis 6.0+

### Backend Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/email-automation-system.git
   cd email-automation-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Installation

1. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

3. Start the frontend development server:
   ```bash
   npm start
   ```

## Configuration

The system can be configured through the `config/default_config.json` file or through environment variables. The main configuration sections are:

- **Database**: MongoDB connection settings
- **Cache**: Redis connection settings
- **API**: FastAPI server settings
- **Email Ingestion**: Email retrieval settings
- **Classification**: Email classification settings
- **Summarization**: Text summarization settings
- **Response Generation**: Response creation settings
- **Integration**: External service integration settings
- **Logging**: Logging configuration

Example configuration:

```json
{
    "database": {
        "mongodb_url": "mongodb://localhost:27017",
        "database_name": "email_automation"
    },
    "cache": {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0
    },
    "api": {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": true,
        "cors_origins": ["*"]
    },
    "email_ingestion": {
        "batch_size": 10,
        "polling_interval": 300
    }
}
```

## Usage

### Setting Up Email Providers

1. Log in to the system using your credentials
2. Navigate to the Settings page
3. Under "Email Ingestion Settings", add your email provider details:
   - Provider type (Gmail, Outlook, etc.)
   - Server address
   - Username and password
   - Folder to monitor
4. Save the settings

### Managing Email Processing

1. Navigate to the Dashboard to view system status
2. Use the "Fetch New Emails" button to manually trigger email retrieval
3. View processed emails in the Email List page
4. Review and edit generated responses as needed
5. Monitor system performance through the Analytics page

### Configuring Integrations

1. Navigate to the Integrations page
2. Connect to external services:
   - Calendar systems (Google Calendar, Outlook, etc.)
   - CRM systems (Salesforce, HubSpot, etc.)
   - Task management systems (Asana, Trello, etc.)
3. Configure integration settings
4. Test connections to ensure proper functionality

## API Reference

The system provides a RESTful API for interacting with the email automation system. All endpoints require authentication using JWT tokens.

### Authentication

```
POST /token
```

Request body:
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### Email Ingestion

```
POST /ingestion/providers
```

Request body:
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

```
POST /ingestion/fetch
```

Request body:
```json
{
    "provider_id": "provider_id_here"
}
```

### Classification

```
POST /classification/classify
```

Request body:
```json
{
    "message_id": "message_id_here",
    "subject": "Email subject",
    "from_address": "sender@example.com",
    "to": "recipient@example.com",
    "body": "Email body text here"
}
```

### Summarization

```
POST /summarization/summarize
```

Request body:
```json
{
    "message_id": "message_id_here",
    "subject": "Email subject",
    "from_address": "sender@example.com",
    "to": "recipient@example.com",
    "body": "Email body text here"
}
```

### Response Generation

```
POST /response/generate
```

Request body:
```json
{
    "message_id": "message_id_here",
    "subject": "Email subject",
    "from_address": "sender@example.com",
    "to": "recipient@example.com",
    "body": "Email body text here",
    "classification": {
        "predicted_category": "important",
        "confidence": 0.85
    },
    "processed_data": {
        "summary": "Email summary here",
        "extractions": {
            "dates_times": [],
            "contacts": [],
            "tasks": []
        }
    }
}
```

### Integration

```
POST /integration/workflow
```

Request body:
```json
[
    {
        "message_id": "message_id_here",
        "subject": "Email subject",
        "from_address": "sender@example.com",
        "to": "recipient@example.com",
        "body": "Email body text here",
        "classification": {
            "predicted_category": "important",
            "confidence": 0.85
        },
        "processed_data": {
            "summary": "Email summary here",
            "extractions": {
                "dates_times": [],
                "contacts": [],
                "tasks": []
            }
        },
        "response_data": {
            "response_text": "Response text here",
            "auto_send": true,
            "confidence": 0.92
        }
    }
]
```

## Frontend Guide

The frontend provides a user-friendly interface for interacting with the email automation system. The main pages are:

### Dashboard

The Dashboard provides an overview of system status and recent activity. It displays:
- Email processing statistics
- Recent emails
- Quick action buttons

### Email List

The Email List page displays all processed emails with their classification, summary, and response status. It allows:
- Searching and filtering emails
- Viewing email details
- Managing responses
- Triggering email fetching

### Settings

The Settings page allows configuration of system behavior, including:
- Email ingestion settings
- Classification settings
- Summarization settings
- Response generation settings
- Integration settings

### Integrations

The Integrations page manages connections to external services:
- Calendar systems
- CRM systems
- Task management systems

### Analytics

The Analytics page provides detailed metrics on system performance:
- Email volume charts
- Category distribution
- Response rates
- Integration usage statistics

## Testing

The system includes comprehensive test suites for all components:

- **Unit Tests**: Test individual components and functions
- **API Tests**: Test API endpoints
- **Frontend Tests**: Test UI components
- **Integration Tests**: Test end-to-end workflows

To run the tests:

```bash
cd tests
./run_tests.sh
```

## Troubleshooting

### Common Issues

1. **Connection to Email Provider Fails**
   - Check your credentials
   - Ensure IMAP/SMTP is enabled for your email account
   - Verify firewall settings

2. **Database Connection Issues**
   - Check MongoDB connection string
   - Ensure MongoDB service is running
   - Verify network connectivity

3. **Classification Accuracy Problems**
   - Adjust confidence threshold in settings
   - Provide more training examples
   - Review classification model settings

4. **Integration Service Errors**
   - Verify API keys and credentials
   - Check service status
   - Review integration logs

### Logging

The system logs are stored in the `logs` directory. Check these logs for detailed error information:

- `email_automation.log`: Main system log
- `api_requests.log`: API request log
- `error.log`: Error-specific log

## Security Considerations

The system implements several security measures:

- **Authentication**: JWT-based authentication for API access
- **Password Security**: Bcrypt hashing for password storage
- **API Security**: HTTPS for all API communications
- **Data Protection**: Encrypted storage of sensitive information
- **Access Control**: Role-based access control for different functions

## Future Enhancements

Planned future enhancements include:

- **Multi-language Support**: Process emails in multiple languages
- **Advanced NLP Models**: Improve classification and summarization accuracy
- **Mobile Application**: Provide mobile access to the system
- **Voice Integration**: Add voice assistant capabilities
- **Expanded Integrations**: Connect with more external services
- **AI-Powered Analytics**: Advanced analytics with predictive capabilities
