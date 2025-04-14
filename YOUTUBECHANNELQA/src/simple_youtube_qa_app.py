"""
Simple Streamlit app for YouTube Q&A
"""

import streamlit as st
import numpy as np
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer, util

# Set page configuration
st.set_page_config(
    page_title="YouTube Video Q&A",
    page_icon="🎬",
    layout="wide"
)

# Helper functions
def get_video_id(url_or_id: str) -> str:
    """Extract video ID from URL or return the ID if already provided."""
    if 'youtube.com' in url_or_id or 'youtu.be' in url_or_id:
        # Extract from youtube.com/watch?v=XYZ
        if 'youtube.com/watch' in url_or_id:
            video_id = url_or_id.split('v=')[1].split('&')[0]
        # Extract from youtu.be/XYZ
        elif 'youtu.be' in url_or_id:
            video_id = url_or_id.split('/')[-1].split('?')[0]
        else:
            video_id = url_or_id
    else:
        # Assume it's already a video ID
        video_id = url_or_id
    
    return video_id

def get_transcript(video_id_or_url: str) -> List[Dict]:
    """Get transcript for a YouTube video."""
    video_id = get_video_id(video_id_or_url)
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        st.error(f"Error getting transcript: {str(e)}")
        return None

def format_transcript_segments(transcript: List[Dict]) -> List[Dict]:
    """Format transcript segments for embedding."""
    formatted_segments = []
    
    # Combine segments for better context (window of 3)
    window_size = 3
    
    for i in range(len(transcript)):
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(transcript), i + window_size // 2 + 1)
        
        combined_text = " ".join([segment["text"] for segment in transcript[start_idx:end_idx]])
        start_time = transcript[i]["start"]
        
        formatted_segments.append({
            "id": i,
            "text": combined_text,
            "start_time": start_time,
            "video_id": get_video_id(st.session_state.video_url)
        })
    
    return formatted_segments

def embed_segments(segments: List[Dict], model: SentenceTransformer) -> Dict:
    """Generate embeddings for transcript segments."""
    texts = [segment["text"] for segment in segments]
    
    with st.spinner('Generating embeddings...'):
        embeddings = model.encode(texts, convert_to_tensor=True)
    
    # Store segment info with its embedding
    embedded_segments = {
        "segments": segments,
        "embeddings": embeddings
    }
    
    return embedded_segments

def search_segments(question: str, embedded_segments: Dict, model: SentenceTransformer, top_k: int = 5) -> List[Dict]:
    """Search for relevant segments based on the question."""
    # Embed the question
    question_embedding = model.encode(question, convert_to_tensor=True)
    
    # Calculate similarity scores
    similarities = util.pytorch_cos_sim(question_embedding, embedded_segments["embeddings"])[0]
    
    # Get top-k indices
    top_indices = similarities.argsort(descending=True)[:top_k].tolist()
    
    # Get corresponding segments
    results = []
    for idx in top_indices:
        segment = embedded_segments["segments"][idx]
        score = similarities[idx].item()
        results.append({
            "segment": segment,
            "score": score
        })
    
    return results

def format_time(seconds: float) -> str:
    """Format time in seconds to MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def create_youtube_embed(video_id: str) -> str:
    """Create an iframe HTML for embedding a YouTube video."""
    return f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'

def create_youtube_timestamp_link(video_id: str, start_time: float) -> str:
    """Create a link to a YouTube video at a specific timestamp."""
    return f"https://www.youtube.com/watch?v={video_id}&t={int(start_time)}s"

# Initialize session state
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'model' not in st.session_state:
    st.session_state.model = None
if 'embedded_segments' not in st.session_state:
    st.session_state.embedded_segments = None
if 'video_url' not in st.session_state:
    st.session_state.video_url = ""
if 'video_id' not in st.session_state:
    st.session_state.video_id = ""

# App title
st.title("YouTube Video Q&A")

# Sidebar
with st.sidebar:
    st.header("About")
    st.info(
        "This app uses AI to answer questions about YouTube videos. "
        "Enter a YouTube URL and ask questions about its content."
    )

# Main UI
tab1, tab2 = st.tabs(["Process Video", "Ask Questions"])

with tab1:
    st.header("Process YouTube Video")
    
    # Video URL input
    video_url = st.text_input("Enter YouTube Video URL:", value="https://www.youtube.com/watch?v=-nvJIfQnidw")
    
    if st.button("Process Video"):
        if video_url:
            try:
                st.session_state.video_url = video_url
                st.session_state.video_id = get_video_id(video_url)
                
                # Display video
                st.subheader("Video")
                st.markdown(create_youtube_embed(st.session_state.video_id), unsafe_allow_html=True)
                
                # Get transcript
                with st.spinner("Getting transcript..."):
                    transcript = get_transcript(video_url)
                
                if transcript:
                    st.success(f"Successfully retrieved transcript with {len(transcript)} segments")
                    
                    # Format segments
                    segments = format_transcript_segments(transcript)
                    
                    # Load embedding model
                    with st.spinner("Loading embedding model..."):
                        st.session_state.model = SentenceTransformer('all-MiniLM-L6-v2')
                    
                    # Generate embeddings
                    st.session_state.embedded_segments = embed_segments(segments, st.session_state.model)
                    st.session_state.processed = True
                    
                    st.success("Video processed successfully! Go to the 'Ask Questions' tab to start asking questions.")
                else:
                    st.error("Failed to retrieve transcript. Make sure the video has closed captions available.")
            except Exception as e:
                st.error(f"Error processing video: {str(e)}")
        else:
            st.warning("Please enter a YouTube video URL")

with tab2:
    st.header("Ask Questions")
    
    if not st.session_state.processed:
        st.info("Please process a YouTube video first.")
    else:
        # Display video
        st.subheader("Video")
        st.markdown(create_youtube_embed(st.session_state.video_id), unsafe_allow_html=True)
        
        # Question input
        question = st.text_input("Ask a question about the video content:")
        num_results = st.slider("Number of results", min_value=1, max_value=10, value=3)
        
        if st.button("Ask"):
            if question:
                with st.spinner("Searching for answer..."):
                    # Search for relevant segments
                    results = search_segments(
                        question, 
                        st.session_state.embedded_segments, 
                        st.session_state.model,
                        top_k=num_results
                    )
                
                # Display results
                st.subheader("Results")
                
                for i, result in enumerate(results):
                    segment = result["segment"]
                    score = result["score"]
                    time_str = format_time(segment["start_time"])
                    
                    with st.expander(f"{i+1}. Segment at {time_str} (Relevance: {score:.2f})"):
                        st.markdown(f"**Text:** {segment['text']}")
                        
                        # Create timestamp link
                        timestamp_link = create_youtube_timestamp_link(
                            segment["video_id"], 
                            segment["start_time"]
                        )
                        st.markdown(f"[Watch this segment on YouTube]({timestamp_link})")
            else:
                st.warning("Please enter a question")

# Footer
st.markdown("---")
st.markdown("YouTube Q&A App - Powered by Sentence Transformers") 