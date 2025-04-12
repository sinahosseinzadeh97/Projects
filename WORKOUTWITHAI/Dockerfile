FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including OpenCV and FFmpeg dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories for uploads and static files
RUN mkdir -p uploads static

# Make the entry point script executable
RUN chmod +x run.sh

# Expose ports
EXPOSE 8000

# Default command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
