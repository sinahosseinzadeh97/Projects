"""
Run script with API keys for the YouTube Q&A system

This script sets the API keys as environment variables and runs the 
FastAPI backend and Streamlit frontend.
"""

import os
import subprocess
import sys

# Set API keys as environment variables
os.environ['YOUTUBE_API_KEY'] = 'your_youtube_api_key_here'
os.environ['OPENAI_API_KEY'] = 'your_openai_api_key_here'

# Run the application
backend_port = 8000
frontend_port = 8505

# Set API base URL for the frontend
os.environ['API_BASE_URL'] = f"http://localhost:{backend_port}/api/v1"

# Run the application
subprocess.run([sys.executable, "run.py", "--backend-port", str(backend_port), "--frontend-port", str(frontend_port)]) 