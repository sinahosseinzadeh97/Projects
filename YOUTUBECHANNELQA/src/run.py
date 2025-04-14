"""
Main run script for the YouTube Q&A system

This script runs both the FastAPI backend and Streamlit frontend.
It can also run just the backend or just the frontend based on command line arguments.
"""

import os
import argparse
import subprocess
import time
import signal
import sys
import threading

def parse_args():
    parser = argparse.ArgumentParser(description='Run the YouTube Q&A system')
    parser.add_argument('--backend-only', action='store_true', help='Run only the backend')
    parser.add_argument('--frontend-only', action='store_true', help='Run only the frontend')
    parser.add_argument('--backend-port', type=int, default=8000, help='Port for the backend')
    parser.add_argument('--frontend-port', type=int, default=8501, help='Port for the frontend')
    return parser.parse_args()

def setup_environment(backend_port):
    # Set API keys (if not already set in environment)
    if 'YOUTUBE_API_KEY' not in os.environ:
        os.environ['YOUTUBE_API_KEY'] = 'your_youtube_api_key_here'
    if 'OPENAI_API_KEY' not in os.environ:
        os.environ['OPENAI_API_KEY'] = 'your_openai_api_key_here'
    
    # Set API base URL for the frontend
    os.environ['API_BASE_URL'] = f"http://localhost:{backend_port}/api/v1"

def start_backend(port=8080):
    """Start the FastAPI backend server."""
    print(f"Starting FastAPI backend on port {port}...")
    
    # Set API keys directly in environment for the backend
    os.environ['YOUTUBE_API_KEY'] = 'your_youtube_api_key_here'
    os.environ['OPENAI_API_KEY'] = 'your_openai_api_key_here'
    
    # Start the backend server
    backend_process = subprocess.Popen(
        ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to start
    time.sleep(2)
    
    # Check if the server started successfully
    if backend_process.poll() is not None:
        print("Error starting backend server:")
        print(backend_process.stderr.read())
        sys.exit(1)
    
    print(f"Backend server running on http://localhost:{port}")
    return backend_process

def start_frontend(port=8505, backend_port=8080):
    """Start the Streamlit frontend."""
    print(f"Starting Streamlit frontend on port {port}...")
    
    # Set environment variable for backend URL
    os.environ['API_BASE_URL'] = f"http://localhost:{backend_port}/api/v1"
    
    # Start the frontend server
    frontend_process = subprocess.Popen(
        ["streamlit", "run", "streamlit_app.py", "--server.port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to start
    time.sleep(5)
    
    # Check if the server started successfully
    if frontend_process.poll() is not None:
        print("Error starting frontend server:")
        print(frontend_process.stderr.read())
        sys.exit(1)
    
    print(f"Frontend server running on http://localhost:{port}")
    return frontend_process

def main():
    """Main function to run the YouTube Q&A system."""
    parser = argparse.ArgumentParser(description="Run the YouTube Q&A system")
    parser.add_argument("--backend-port", type=int, default=8080, help="Port for the FastAPI backend")
    parser.add_argument("--frontend-port", type=int, default=8505, help="Port for the Streamlit frontend")
    parser.add_argument("--backend-only", action="store_true", help="Run only the backend")
    parser.add_argument("--frontend-only", action="store_true", help="Run only the frontend")
    
    args = parser.parse_args()
    
    # Store processes to terminate later
    processes = []
    
    try:
        # Start backend if needed
        if not args.frontend_only:
            backend_process = start_backend(port=args.backend_port)
            processes.append(backend_process)
        
        # Start frontend if needed
        if not args.backend_only:
            frontend_process = start_frontend(port=args.frontend_port, backend_port=args.backend_port)
            processes.append(frontend_process)
        
        print("\nYouTube Q&A system is running!")
        print("Press Ctrl+C to stop the servers.")
        
        # Keep the script running
        while all(process.poll() is None for process in processes):
            time.sleep(1)
        
        # If we get here, one of the processes has terminated
        for process in processes:
            if process.poll() is not None:
                print(f"Process terminated with exit code {process.poll()}")
                print(process.stderr.read())
    
    except KeyboardInterrupt:
        print("\nStopping servers...")
    
    finally:
        # Terminate all processes
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("Servers stopped.")

if __name__ == "__main__":
    main()
