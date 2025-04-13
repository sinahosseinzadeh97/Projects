"""
Streamlit YouTube Q&A App

This app provides a web interface for asking questions about YouTube videos.
It extracts transcripts, creates embeddings, and performs semantic search.
"""

import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import time

# Set page configuration
st.set_page_config(
    page_title="YouTube Video Q&A",
    page_icon="🎬",
    layout="wide"
)

# Cache expensive operations
@st.cache_resource
def load_embedding_model(model_name="all-MiniLM-L6-v2"):
    """Load and cache the sentence transformer model."""
    return SentenceTransformer(model_name)

@st.cache_data
def extract_video_id(url):
    """Extract video ID from a YouTube URL."""
    if 'youtu.be' in url:
        # Format: https://youtu.be/VIDEO_ID
        video_id = url.split('/')[-1].split('?')[0]
    elif 'youtube.com/watch' in url:
        # Format: https://www.youtube.com/watch?v=VIDEO_ID
        match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
        if match:
            video_id = match.group(1)
        else:
            raise ValueError(f"Could not extract video ID from URL: {url}")
    else:
        raise ValueError(f"Unsupported YouTube URL format: {url}")
        
    return video_id

@st.cache_data
def get_transcript(video_id, languages=['en']):
    """Extract transcript for a specific YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        return transcript
    except Exception as e:
        st.error(f"Error extracting transcript for video {video_id}: {e}")
        return None

@st.cache_data
def segment_transcript(transcript, segment_length=300, overlap=50):
    """Split transcript into logical segments for embedding."""
    if not transcript:
        return []
    
    segments = []
    current_segment = {
        'text': '',
        'start': transcript[0]['start'],
        'duration': 0
    }
    
    for entry in transcript:
        # If adding this entry would exceed segment length, save current segment and start new one
        if len(current_segment['text']) + len(entry['text']) > segment_length and len(current_segment['text']) > 0:
            # Calculate total duration
            current_segment['duration'] = (entry['start'] - current_segment['start'])
            segments.append(current_segment)
            
            # Start new segment with overlap
            overlap_text = current_segment['text'][-overlap:] if overlap > 0 else ''
            current_segment = {
                'text': overlap_text + ' ' + entry['text'],
                'start': entry['start'],
                'duration': 0
            }
        else:
            # Add to current segment
            if current_segment['text']:
                current_segment['text'] += ' ' + entry['text']
            else:
                current_segment['text'] = entry['text']
    
    # Add the last segment if it has content
    if current_segment['text'] and len(current_segment['text']) > 0:
        # Estimate duration for last segment (assuming average duration of previous entries)
        if len(transcript) > 1:
            avg_duration = sum(entry['duration'] for entry in transcript) / len(transcript)
            current_segment['duration'] = avg_duration
        else:
            current_segment['duration'] = transcript[0]['duration']
            
        segments.append(current_segment)
    
    # Clean up segments
    for segment in segments:
        segment['text'] = clean_text(segment['text'])
    
    return segments

def clean_text(text):
    """Clean transcript text by removing extra whitespace, etc."""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def generate_video_url_with_timestamp(video_id, start_time):
    """Generate a YouTube URL that starts at a specific timestamp."""
    return f"https://www.youtube.com/watch?v={video_id}&t={int(start_time)}"

@st.cache_data(show_spinner=False)
def get_embeddings_and_index(segments, _model):
    """
    Generate embeddings and index for transcript segments using the provided model.
    Returns embeddings as a separate entity to avoid recursion issues.
    """
    texts = [segment['text'] for segment in segments]
    embeddings = _model.encode(texts, convert_to_numpy=True)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    
    return embeddings, index

def main():
    """Main Streamlit app function."""
    st.title("YouTube Video Q&A")
    st.write("Ask questions about the content of YouTube videos using embeddings and semantic search.")
    
    # Input for YouTube URL
    url_input = st.text_input(
        "Enter YouTube Video URL:",
        value="https://www.youtube.com/watch?v=NtLytfhtrTA&t=1s",
        help="Paste a YouTube video URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)"
    )
    
    # Process button
    col1, col2 = st.columns([1, 3])
    with col1:
        process_button = st.button("Process Video", type="primary")
    with col2:
        segment_length = st.slider("Segment Length (chars)", 100, 500, 300, 50)
    
    # Initialize session state
    if 'video_processed' not in st.session_state:
        st.session_state.video_processed = False
    if 'segments' not in st.session_state:
        st.session_state.segments = []
    if 'video_id' not in st.session_state:
        st.session_state.video_id = None
    if 'video_title' not in st.session_state:
        st.session_state.video_title = "Unknown"
    if 'model_dimension' not in st.session_state:
        st.session_state.model_dimension = 0
        
    # Load the embedding model
    model = load_embedding_model()
    
    # Process the video when button is clicked
    if process_button and url_input:
        try:
            with st.spinner("Processing video..."):
                # Extract video ID
                video_id = extract_video_id(url_input)
                
                # Get transcript
                transcript = get_transcript(video_id)
                if not transcript:
                    st.error("Failed to retrieve transcript. Please try another video.")
                    st.session_state.video_processed = False
                    return
                
                # Process transcript into segments
                segments = segment_transcript(transcript, segment_length=segment_length)
                
                # If no segments, show error
                if not segments:
                    st.error("No transcript segments could be created. Please try another video.")
                    st.session_state.video_processed = False
                    return
                
                # Enhance segments with video metadata
                for segment in segments:
                    segment['video_id'] = video_id
                    segment['video_url'] = generate_video_url_with_timestamp(video_id, segment['start'])
                
                # Generate embeddings and index
                embeddings, index = get_embeddings_and_index(segments, model)
                
                # Update session state without storing numpy arrays directly
                st.session_state.video_id = video_id
                st.session_state.segments = segments
                st.session_state.video_processed = True
                st.session_state.video_title = "YouTube Video"
                st.session_state.model_dimension = model.get_sentence_embedding_dimension()
                
                # Store cache key for embeddings and index
                st.session_state.segments_key = str(segments)[:100]  # Use a substring as key
                
                # Success message
                st.success(f"Video processed successfully! Created {len(segments)} segments.")
                
                # No need to rerun - changes will be reflected immediately
        
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            st.session_state.video_processed = False
    
    # Display Q&A interface if video is processed
    if st.session_state.video_processed:
        st.markdown("---")
        
        # Embed the YouTube video
        if st.session_state.video_id:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Video")
                video_url = f"https://www.youtube.com/embed/{st.session_state.video_id}"
                st.components.v1.iframe(video_url, height=315)
            with col2:
                st.subheader("Stats")
                st.write(f"**Segments:** {len(st.session_state.segments)}")
                st.write(f"**Embedding Dimensions:** {st.session_state.model_dimension}")
                st.write(f"**Model:** {model.get_sentence_embedding_dimension()}-dimensional embeddings")
        
        # Q&A Section
        st.markdown("---")
        st.header("Ask Questions About the Video")
        
        # Get the question
        question = st.text_input("Your Question:", placeholder="What is the main topic of this video?")
        num_results = st.slider("Number of results to show", 1, 10, 3)
        
        # Button to submit question
        if st.button("Search", type="primary") and question:
            # Get embeddings and index again using the same segments (uses cache)
            embeddings, index = get_embeddings_and_index(st.session_state.segments, model)
                
            with st.spinner("Searching for relevant segments..."):
                # Generate query embedding
                query_embedding = model.encode([question], convert_to_numpy=True)
                
                # Search the index
                D, I = index.search(query_embedding.astype('float32'), num_results)
                
                # Format results
                results = []
                for i, idx in enumerate(I[0]):
                    if idx < len(st.session_state.segments):  # Ensure index is valid
                        segment = st.session_state.segments[idx]
                        results.append({
                            'segment': segment,
                            'distance': float(D[0][i])
                        })
                
                # Display results
                if results:
                    st.subheader("Results")
                    for i, result in enumerate(results):
                        segment = result['segment']
                        distance = result['distance']
                        
                        with st.expander(f"Segment {i+1} (Score: {1/(1+distance):.2f})", expanded=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**Text:** {segment['text']}")
                            with col2:
                                st.markdown(f"**Timestamp:** {int(segment['start']//60)}:{int(segment['start']%60):02d}")
                                timestamp_url = segment['video_url']
                                st.markdown(f"[Watch this segment]({timestamp_url})")
                else:
                    st.warning("No relevant segments found. Try a different question.")
        
        # Display all segments option
        with st.expander("View All Transcript Segments", expanded=False):
            for i, segment in enumerate(st.session_state.segments):
                st.markdown(f"**Segment {i+1}** (Start: {int(segment['start']//60)}:{int(segment['start']%60):02d})")
                st.markdown(segment['text'])
                st.markdown(f"[Link to timestamp]({segment['video_url']})")
                st.markdown("---")

# Run the app
if __name__ == "__main__":
    main() 