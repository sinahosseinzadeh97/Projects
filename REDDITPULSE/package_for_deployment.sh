#!/bin/bash

# Reddit Automation Tool - Deployment Package Script
# Created by: SinaMohammadHosseinZadeh

# Make script exit on error
set -e

# Configuration
PACKAGE_NAME="reddit-automation-tool"
VERSION="1.0.0"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="deployment_package_${TIMESTAMP}"
ARCHIVE_NAME="${PACKAGE_NAME}_${VERSION}_${TIMESTAMP}.tar.gz"

# Welcome message
echo "==============================================="
echo "Reddit Automation Tool - Deployment Package Creator"
echo "Developed by: SinaMohammadHosseinZadeh"
echo "==============================================="
echo "Creating deployment package..."

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Essential Python files
PYTHON_FILES=(
    "main.py"
    "config.py"
    "dashboard.py"
    "logger.py"
    "post_analyzer.py"
    "reddit_bot.py"
    "response_generator.py"
    "scheduler.py"
    "subreddit_monitor.py"
    "test_mode.py"
)

# Template files
TEMPLATE_FILES=(
    $(find templates -name "*.html" -o -name "*.json")
)

# Deployment files
DEPLOYMENT_FILES=(
    "README.md"
    "requirements_for_deployment.txt"
    "Dockerfile"
    "docker-compose.yml"
    "deploy.sh"
    "generate_secret.py"
    ".env.example"
)

# Copy Python files
echo "Copying Python files..."
for file in "${PYTHON_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "${OUTPUT_DIR}/"
        echo " - $file"
    else
        echo " - Warning: $file not found, skipping"
    fi
done

# Create template directory and copy templates
echo "Copying template files..."
mkdir -p "${OUTPUT_DIR}/templates"
for file in "${TEMPLATE_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Create directory structure if needed
        dir=$(dirname "$file")
        mkdir -p "${OUTPUT_DIR}/${dir}"
        cp "$file" "${OUTPUT_DIR}/${file}"
        echo " - $file"
    else
        echo " - Warning: $file not found, skipping"
    fi
done

# Create logs directory
echo "Creating logs directory..."
mkdir -p "${OUTPUT_DIR}/logs"
touch "${OUTPUT_DIR}/logs/.gitkeep"

# Copy deployment files
echo "Copying deployment files..."
for file in "${DEPLOYMENT_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "${OUTPUT_DIR}/"
        echo " - $file"
    else
        echo " - Warning: $file not found, skipping"
    fi
done

# Rename requirements file
mv "${OUTPUT_DIR}/requirements_for_deployment.txt" "${OUTPUT_DIR}/requirements.txt"
echo " - Renamed requirements_for_deployment.txt to requirements.txt"

# Create archive
echo "Creating deployment archive..."
tar -czf "${ARCHIVE_NAME}" -C "${OUTPUT_DIR}/" .
echo "Created ${ARCHIVE_NAME}"

echo "==============================================="
echo "Deployment package created successfully!"
echo "Files are available in: ${OUTPUT_DIR}/"
echo "Archive: ${ARCHIVE_NAME}"
echo "To deploy the application, copy the archive to your server and run:"
echo "  tar -xzf ${ARCHIVE_NAME}"
echo "  cd extracted_directory"
echo "  ./deploy.sh"
echo "==============================================="