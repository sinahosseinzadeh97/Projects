#!/bin/bash

# Reddit Automation Tool - Deployment Script
# Created by: SinaMohammadHosseinZadeh

# Color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Make script exit on error
set -e

# Print header
echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}    Reddit Automation Tool - Deployment Script    ${NC}"
echo -e "${BLUE}    Created by: SinaMohammadHosseinZadeh         ${NC}"
echo -e "${BLUE}=================================================${NC}"

# Check if docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo -e "${RED}Error: docker is not installed.${NC}" >&2
  echo -e "Please install Docker by following the instructions at:"
  echo -e "https://docs.docker.com/get-docker/"
  exit 1
fi

# Check if docker-compose is installed
if ! [ -x "$(command -v docker-compose)" ]; then
  echo -e "${RED}Error: docker-compose is not installed.${NC}" >&2
  echo -e "Please install Docker Compose by following the instructions at:"
  echo -e "https://docs.docker.com/compose/install/"
  exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}Warning: .env file not found.${NC}"
  
  # Check if .env.example exists
  if [ -f ".env.example" ]; then
    echo -e "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}Please update the .env file with your credentials.${NC}"
  else
    echo -e "${RED}Error: Neither .env nor .env.example found.${NC}"
    echo -e "Please create a .env file with your Reddit API credentials."
    exit 1
  fi
fi

# Generate session secret if not already present in .env
if ! grep -q "SESSION_SECRET" .env; then
  echo -e "${YELLOW}Adding SESSION_SECRET to .env file...${NC}"
  if [ -f "generate_secret.py" ]; then
    python3 generate_secret.py
    echo -e "${GREEN}Session secret added to .env file.${NC}"
  else
    # Generate a random secret without the Python script
    random_secret=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)
    echo "SESSION_SECRET=${random_secret}" >> .env
    echo -e "${GREEN}Session secret added to .env file.${NC}"
  fi
fi

# Check for mandatory environment variables
echo -e "${BLUE}Checking environment variables...${NC}"
required_vars=("REDDIT_USERNAME" "REDDIT_PASSWORD" "REDDIT_CLIENT_ID" "REDDIT_CLIENT_SECRET")
missing_vars=()

for var in "${required_vars[@]}"; do
  if ! grep -q "^${var}=" .env || [ -z "$(grep "^${var}=" .env | cut -d '=' -f2)" ]; then
    missing_vars+=("$var")
  fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
  echo -e "${RED}Error: The following required environment variables are missing or empty:${NC}"
  for var in "${missing_vars[@]}"; do
    echo -e "  - $var"
  done
  echo -e "${YELLOW}Please update your .env file with these values before proceeding.${NC}"
  exit 1
fi

echo -e "${GREEN}All required environment variables are present.${NC}"

# Build and start the Docker containers
echo -e "${BLUE}Building and starting Docker containers...${NC}"
docker-compose up --build -d

# Check if containers are running
echo -e "${BLUE}Checking container status...${NC}"
sleep 5
if [ "$(docker-compose ps | grep 'Up' | wc -l)" -ne 2 ]; then
  echo -e "${RED}Error: Containers failed to start properly.${NC}"
  echo -e "Check the logs with: docker-compose logs"
  exit 1
fi

# Initialize the database if needed
echo -e "${BLUE}Initializing database...${NC}"
docker-compose exec db psql -U postgres -f /docker-entrypoint-initdb.d/db_init.sql || {
  echo -e "${YELLOW}Warning: Could not initialize database. It may already be initialized.${NC}"
}

# Run database updates
echo -e "${BLUE}Applying database updates...${NC}"
docker-compose exec db psql -U postgres -f /docker-entrypoint-initdb.d/db_update.sql || {
  echo -e "${YELLOW}Warning: Could not apply database updates.${NC}"
}

# Print success message
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "The Reddit Automation Bot is now running."
echo -e ""
echo -e "Web Dashboard: http://localhost:5000"
echo -e "API Health Check: http://localhost:5000/api/health"
echo -e ""
echo -e "To view logs: docker-compose logs -f"
echo -e "To stop the application: docker-compose down"
echo -e "${BLUE}=================================================${NC}"
echo -e "Created by: SinaMohammadHosseinZadeh"