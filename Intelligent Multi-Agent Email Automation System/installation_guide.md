# Installation Guide

## Overview

This guide provides step-by-step instructions for installing and configuring the Intelligent Multi-Agent Email Automation System. Follow these instructions to set up both the backend and frontend components of the system.

## Prerequisites

Before beginning the installation, ensure you have the following prerequisites installed on your system:

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows 10+
- **Python**: Version 3.8 or higher
- **Node.js**: Version 14 or higher
- **MongoDB**: Version 4.4 or higher
- **Redis**: Version 6.0 or higher
- **Git**: Latest version

You can verify these installations with the following commands:

```bash
# Check Python version
python3 --version

# Check Node.js version
node --version

# Check MongoDB version
mongod --version

# Check Redis version
redis-server --version

# Check Git version
git --version
```

## System Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 10GB minimum
- **Network**: Internet connection for external integrations

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/email-automation-system.git
cd email-automation-system
```

### 2. Backend Installation

#### 2.1. Create and Activate a Virtual Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 2.2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 2.3. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```
# Database Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=email_automation

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:3000

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Provider Defaults
DEFAULT_BATCH_SIZE=10
DEFAULT_POLLING_INTERVAL=300

# Integration Services
GOOGLE_CALENDAR_API_KEY=your-api-key
SALESFORCE_API_KEY=your-api-key
ASANA_API_KEY=your-api-key
```

Replace the placeholder values with your actual configuration.

#### 2.4. Initialize the Database

```bash
python init_db.py
```

### 3. Frontend Installation

#### 3.1. Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

#### 3.2. Configure Environment Variables

Create a `.env` file in the frontend directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_VERSION=1.0.0
```

### 4. Start the Services

#### 4.1. Start MongoDB and Redis

If MongoDB and Redis are not running as services, start them:

```bash
# Start MongoDB
mongod --dbpath /path/to/data/db

# Start Redis
redis-server
```

#### 4.2. Start the Backend Server

```bash
cd ../backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4.3. Start the Frontend Development Server

In a new terminal:

```bash
cd ../frontend
npm start
```

### 5. Verify Installation

- Backend API should be accessible at: http://localhost:8000
- Frontend application should be accessible at: http://localhost:3000
- API documentation should be accessible at: http://localhost:8000/docs

## Docker Installation (Alternative)

If you prefer to use Docker, follow these steps:

### 1. Install Docker and Docker Compose

Follow the official Docker installation guide for your operating system:
- [Docker Installation Guide](https://docs.docker.com/get-docker/)
- [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/email-automation-system.git
cd email-automation-system
```

### 3. Configure Environment Variables

Create `.env` files for both backend and frontend as described in the standard installation steps.

### 4. Build and Start the Containers

```bash
docker-compose up -d
```

This will build and start all required containers:
- MongoDB
- Redis
- Backend API
- Frontend application

### 5. Verify Docker Installation

- Backend API should be accessible at: http://localhost:8000
- Frontend application should be accessible at: http://localhost:3000
- API documentation should be accessible at: http://localhost:8000/docs

## Production Deployment

For production deployment, additional steps are recommended:

### 1. Security Considerations

- Use HTTPS for all communications
- Set up proper firewall rules
- Use strong, unique passwords
- Implement proper backup strategies

### 2. Backend Production Setup

Update the `.env` file for production:

```
DEBUG=false
CORS_ORIGINS=https://your-production-domain.com
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

Use a production ASGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### 3. Frontend Production Build

Create a production build of the frontend:

```bash
cd frontend
npm run build
```

Serve the static files using Nginx or a similar web server.

### 4. Monitoring and Logging

Set up monitoring and logging for production:

- Use a logging service like ELK Stack or Graylog
- Set up monitoring with Prometheus and Grafana
- Configure alerts for system issues

## Troubleshooting

### Common Installation Issues

#### MongoDB Connection Issues

**Problem**: Cannot connect to MongoDB
**Solution**:
- Verify MongoDB is running: `ps aux | grep mongod`
- Check MongoDB connection string in `.env` file
- Ensure MongoDB port (27017) is not blocked by firewall

#### Redis Connection Issues

**Problem**: Cannot connect to Redis
**Solution**:
- Verify Redis is running: `ps aux | grep redis`
- Check Redis host and port in `.env` file
- Ensure Redis port (6379) is not blocked by firewall

#### Backend Startup Issues

**Problem**: Backend server fails to start
**Solution**:
- Check for error messages in the console
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure MongoDB and Redis are running
- Check `.env` file for correct configuration

#### Frontend Startup Issues

**Problem**: Frontend server fails to start
**Solution**:
- Check for error messages in the console
- Verify all dependencies are installed: `npm install`
- Ensure backend API is running and accessible
- Check `.env` file for correct API URL

### Getting Help

If you encounter issues not covered in this guide:

1. Check the logs for detailed error messages
2. Consult the troubleshooting section in the user guide
3. Search for similar issues in the project repository
4. Contact the support team at support@example.com

## Next Steps

After successful installation:

1. Configure email providers in the system settings
2. Set up external integrations (calendar, CRM, task manager)
3. Customize response templates
4. Configure workflow settings
5. Set up user accounts and permissions

Refer to the User Guide for detailed instructions on using the system.
