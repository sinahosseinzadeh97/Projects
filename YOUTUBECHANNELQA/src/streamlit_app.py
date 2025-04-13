"""
Streamlit UI Module

This module provides a simple web interface for the YouTube Q&A system
using Streamlit.
"""

import os
import requests
import streamlit as st
from typing import List, Dict, Any, Optional

# Set API keys directly (for development only, use environment variables in production)
os.environ['YOUTUBE_API_KEY'] = 'your_youtube_api_key_here'
os.environ['OPENAI_API_KEY'] = 'your_openai_api_key_here'

# Set page configuration
st.set_page_config(
    page_title="YouTube Q&A System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set base URL for API
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000/api/v1')

# Helper functions
def format_time(seconds: float) -> str:
    """Format time in seconds to MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def call_api(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API call to backend."""
    url = f"{API_BASE_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            st.error(f"Unsupported method: {method}")
            return {"error": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {"error": str(e)}

# Sidebar navigation
st.sidebar.title("YouTube Q&A System")
page = st.sidebar.radio("Navigation", ["Dashboard", "Ask", "Settings"])

# Dashboard page
if page == "Dashboard":
    st.title("Dashboard")
    
    # System status
    st.subheader("System Status")
    
    try:
        status = call_api("status")
        
        if "error" not in status:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Videos", status.get("video_count", 0))
            with col2:
                st.metric("Segments", status.get("segment_count", 0))
            with col3:
                st.metric("Status", status.get("status", "Unknown"))
            
            st.info(f"Using embedding model: {status.get('embedding_model', 'Unknown')}")
            st.info(f"Last update: {status.get('last_update', 'Unknown')}")
        else:
            st.error("Could not connect to API. Make sure the backend is running.")
    except Exception as e:
        st.error(f"Error fetching system status: {str(e)}")
    
    # Recent videos
    st.subheader("Recent Videos")
    
    try:
        videos = call_api("videos?limit=5")
        
        if "error" not in videos and videos:
            for video in videos:
                with st.expander(f"{video.get('title', 'Unknown')}"):
                    st.write(f"**Published:** {video.get('published_at', 'Unknown')}")
                    st.write(f"**Channel:** {video.get('channel_title', 'Unknown')}")
                    st.write(f"**Description:** {video.get('description', 'No description')}")
                    st.write(f"[Watch on YouTube](https://www.youtube.com/watch?v={video.get('id', '')})")
        else:
            st.info("No videos processed yet. Go to Settings to process videos from a YouTube channel.")
    except Exception as e:
        st.error(f"Error fetching videos: {str(e)}")

# Ask page
elif page == "Ask":
    st.title("Ask a Question")
    
    # Question input
    question = st.text_input("Enter your question about the video content:")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        k = st.slider("Number of references", min_value=1, max_value=10, value=5)
    with col2:
        model = st.selectbox("OpenAI Model", ["gpt-3.5-turbo", "gpt-4"], index=0)
    
    # Ask button
    if st.button("Ask"):
        if question:
            with st.spinner("Generating answer..."):
                try:
                    # Call API to get answer
                    response = call_api("ask", method="POST", data={
                        "question": question,
                        "k": k,
                        "model": model
                    })
                    
                    if "error" not in response:
                        # Display answer
                        st.subheader("Answer")
                        st.write(response.get("answer", "No answer generated"))
                        
                        # Display references
                        st.subheader("References")
                        references = response.get("references", [])
                        
                        if references:
                            for i, ref in enumerate(references):
                                with st.expander(f"{i+1}. {ref.get('video_title', 'Unknown')} ({format_time(ref.get('start_time', 0))})"):
                                    st.write(f"> {ref.get('text', '')}")
                                    st.write(f"[Watch Video]({ref.get('link', '')})")
                        else:
                            st.info("No references found for this question.")
                    else:
                        st.error(f"Error: {response.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
        else:
            st.warning("Please enter a question.")

# Settings page
elif page == "Settings":
    st.title("Settings")
    
    # Channel configuration
    st.subheader("Channel Configuration")
    
    channel_input = st.text_input("YouTube Channel ID or URL:")
    max_results = st.slider("Max Videos to Process", min_value=5, max_value=100, value=50)
    
    if st.button("Process Channel"):
        if channel_input:
            with st.spinner("Processing channel..."):
                try:
                    # Extract channel ID from URL if needed
                    channel_id = channel_input
                    if "youtube.com" in channel_input:
                        # This is a simplified extraction, the backend has more robust handling
                        if "channel/" in channel_input:
                            channel_id = channel_input.split("channel/")[1].split("/")[0].split("?")[0]
                    
                    # Call API to process channel
                    response = call_api("videos/process", method="POST", data={
                        "channel_id": channel_id,
                        "max_results": max_results
                    })
                    
                    if "error" not in response:
                        st.success(f"Processing started. Task ID: {response.get('task_id', 'Unknown')}")
                        
                        # Display task status
                        task_id = response.get("task_id")
                        if task_id:
                            st.info(f"Status: {response.get('status', 'Unknown')}")
                            st.info(f"Message: {response.get('message', 'Unknown')}")
                            
                            # Add refresh button
                            if st.button("Refresh Status"):
                                task_status = call_api(f"tasks/{task_id}")
                                if "error" not in task_status:
                                    st.info(f"Status: {task_status.get('status', 'Unknown')}")
                                    st.info(f"Message: {task_status.get('message', 'Unknown')}")
                                    st.progress(task_status.get("progress", 0) / 100)
                    else:
                        st.error(f"Error: {response.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error processing channel: {str(e)}")
        else:
            st.warning("Please enter a YouTube Channel ID or URL.")
    
    # API configuration
    st.subheader("API Configuration")
    
    youtube_api_key = st.text_input("YouTube API Key:", value=os.environ.get('YOUTUBE_API_KEY', ''), type="password")
    openai_api_key = st.text_input("OpenAI API Key:", value=os.environ.get('OPENAI_API_KEY', ''), type="password")
    
    if st.button("Save API Keys"):
        # In a real app, these would be securely stored
        # For this demo, we'll just show a success message
        if youtube_api_key and openai_api_key:
            os.environ['YOUTUBE_API_KEY'] = youtube_api_key
            os.environ['OPENAI_API_KEY'] = openai_api_key
            st.success("API keys saved successfully.")
        else:
            st.warning("Please enter both API keys.")
    
    # Model configuration
    st.subheader("Model Configuration")
    
    embedding_model = st.radio(
        "Embedding Model:",
        ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "multi-qa-mpnet-base-dot-v1"],
        index=0
    )
    
    openai_model = st.radio(
        "OpenAI Model:",
        ["gpt-3.5-turbo", "gpt-4"],
        index=0
    )
    
    if st.button("Save Model Configuration"):
        # In a real app, this would update the backend configuration
        # For this demo, we'll just show a success message
        st.success("Model configuration saved successfully.")

# Add footer
st.sidebar.markdown("---")
st.sidebar.info(
    "YouTube Q&A System - v1.0.0\n\n"
    "A content-based question answering system using YouTube videos."
)
