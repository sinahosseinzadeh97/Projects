FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir openai pydantic python-dotenv streamlit twilio

# Create cache directory for the application
RUN mkdir -p /app/cache

# Copy the application code
COPY . .

# Create .streamlit directory and config if it doesn't exist
RUN mkdir -p .streamlit && \
    if [ ! -f .streamlit/config.toml ]; then \
    echo '[server]\nheadless = true\naddress = "0.0.0.0"\nport = 5000' > .streamlit/config.toml; \
    fi

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default port
EXPOSE 5000

# Create necessary directories and make sure they have correct permissions
RUN mkdir -p /app/cache && chmod -R 777 /app/cache

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]