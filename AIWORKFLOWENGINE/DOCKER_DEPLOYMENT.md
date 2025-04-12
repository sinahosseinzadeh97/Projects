# Docker Deployment Guide for AI Research System

This guide explains how to deploy the AI Research System using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system
- OpenAI API Key (required)
- Twilio account (optional, for SMS notifications)

## Deployment Steps

### 1. Quick Deployment

We've provided a deployment script that handles all the necessary steps:

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

The script will:
1. Check if Docker and Docker Compose are installed
2. Create a .env file if it doesn't exist
3. Verify that an OpenAI API key has been set
4. Build and start the Docker containers
5. Verify that the application is running

### 2. Manual Deployment

If you prefer to deploy manually, follow these steps:

1. Set up environment variables:
```bash
# Copy the example .env file
cp .env.example .env

# Edit the .env file to add your API keys
nano .env  # or use any text editor
```

2. Build and start the Docker containers:
```bash
docker-compose build
docker-compose up -d
```

3. Verify that the application is running:
```bash
# Check container status
docker ps

# View logs
docker-compose logs -f
```

4. Access the application at `http://localhost:5000`

## Managing Your Deployment

- **View logs**: `docker-compose logs -f`
- **Stop the application**: `docker-compose down`
- **Restart the application**: `docker-compose restart`
- **Rebuild after changes**: `docker-compose up -d --build`

## Troubleshooting

### Container fails to start

Check the logs for errors:
```bash
docker-compose logs
```

Common issues:
- Missing or invalid API keys in .env file
- Port 5000 already in use (change the port mapping in docker-compose.yml)
- Insufficient permissions for volume mounts

### Application errors

If the application starts but you encounter errors:
1. Check the logs: `docker-compose logs -f`
2. Verify your OpenAI API key is valid and has sufficient credits
3. Check for network connectivity issues if the application can't reach external services

## Data Persistence

The application uses Docker volumes for persistence:
- `ai-research-cache`: Stores cache data to reduce API calls

Your data will persist even if you restart or rebuild the containers.

## Security Considerations

- The application is exposed on port 5000 by default. Consider using a reverse proxy (like Nginx) for production.
- Secure your .env file as it contains sensitive API keys.
- For production deployments, consider setting up SSL/TLS. 