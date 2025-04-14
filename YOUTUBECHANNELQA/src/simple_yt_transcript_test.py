"""
Simple YouTube Transcript Extraction Test

This script demonstrates how to extract and process a transcript from a YouTube video
without requiring API keys.
"""

import re
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

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

def get_transcript(video_id, languages=['en']):
    """Extract transcript for a specific YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        return transcript
    except Exception as e:
        print(f"Error extracting transcript for video {video_id}: {e}")
        return None

def segment_transcript(transcript, segment_length=100, overlap=20):
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

def generate_embeddings(segments, model_name="all-MiniLM-L6-v2"):
    """Generate embeddings for transcript segments."""
    model = SentenceTransformer(model_name)
    texts = [segment['text'] for segment in segments]
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    for i, segment in enumerate(segments):
        segment['embedding'] = embeddings[i]
    
    return segments

def create_faiss_index(embeddings):
    """Create a FAISS index from embeddings."""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    return index

def test_simple_query(segments, index, query, k=3):
    """Test a simple query against the segments."""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode([query], convert_to_numpy=True)
    
    # Search the index
    D, I = index.search(query_embedding.astype('float32'), k)
    
    print(f"\nQuery: {query}")
    print(f"Top {k} most relevant segments:")
    
    for i, idx in enumerate(I[0]):
        segment = segments[idx]
        print(f"\nSegment {i+1} (Distance: {D[0][i]:.4f}):")
        print(f"  Start Time: {segment['start']:.2f}s")
        print(f"  Text: {segment['text']}")
        print(f"  Video URL: {segment['video_url']}")

def main():
    """Main function to demonstrate functionality."""
    # Specify the YouTube video URL
    video_url = "https://www.youtube.com/watch?v=NtLytfhtrTA&t=1s"
    
    # Extract video ID
    video_id = extract_video_id(video_url)
    print(f"Processing video ID: {video_id}")
    
    # Get transcript
    transcript = get_transcript(video_id)
    if not transcript:
        print("Failed to retrieve transcript. Exiting.")
        return
    
    print(f"Retrieved transcript with {len(transcript)} entries")
    
    # Process transcript into segments
    segments = segment_transcript(transcript, segment_length=300, overlap=50)
    print(f"Created {len(segments)} transcript segments")
    
    # Enhance segments with video metadata
    for segment in segments:
        segment['video_id'] = video_id
        segment['video_url'] = generate_video_url_with_timestamp(video_id, segment['start'])
    
    # Generate embeddings for segments
    segments = generate_embeddings(segments)
    print(f"Generated embeddings for all segments")
    
    # Create FAISS index
    embeddings = np.array([segment['embedding'] for segment in segments])
    index = create_faiss_index(embeddings)
    print(f"Created search index with {index.ntotal} vectors")
    
    # Test with a few sample queries
    test_simple_query(segments, index, "What is the main idea of this video?", k=3)
    
    # Allow the user to ask questions
    print("\n" + "="*80)
    print("You can now ask questions about the video (type 'exit' to quit):")
    
    while True:
        user_query = input("\nYour question: ")
        if user_query.lower() in ['exit', 'quit', 'q']:
            break
        
        test_simple_query(segments, index, user_query, k=3)

if __name__ == "__main__":
    main() 