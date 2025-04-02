FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir openai pydantic python-dotenv streamlit twilio

# Copy the application code
COPY . .

# Create .streamlit directory and config if it doesn't exist
RUN mkdir -p .streamlit
COPY .streamlit/config.toml .streamlit/config.toml

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default port
EXPOSE 5000

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=5000"]