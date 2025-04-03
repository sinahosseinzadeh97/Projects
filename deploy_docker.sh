#!/bin/bash
# AI Research System Docker Deployment Script

# Exit on error
set -e

echo "=== AI Research System Docker Deployment ==="
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env to add your API keys before continuing."
    exit 1
fi

# Create cache directory if it doesn't exist
mkdir -p cache

# Check if OpenAI API key is set
if grep -q "sk-your-real-openai-api-key" .env; then
    echo "ERROR: OpenAI API key is not set in .env file."
    echo "Please edit .env and set your OpenAI API key."
    exit 1
fi

# Build and start the containers
echo "Building and starting Docker containers..."
docker compose down || true
docker compose build --no-cache
docker compose up -d

# Check if container is running
if docker ps | grep -q "ai-research-system"; then
    echo
    echo "=== Deployment Successful ==="
    echo "AI Research System is now running at: http://localhost:5000"
    echo
    echo "To view logs: docker compose logs -f"
    echo "To stop the system: docker compose down"
else
    echo
    echo "=== Deployment Failed ==="
    echo "Container is not running. Check logs with: docker compose logs"
    exit 1
fi 