"""
Simple script to extract a YouTube transcript and identify the topic.
"""

import re
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
import numpy as np

def extract_video_id(url):
    """Extract video ID from a YouTube URL."""
    if 'youtu.be' in url:
        video_id = url.split('/')[-1].split('?')[0]
    elif 'youtube.com/watch' in url:
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

def clean_text(text):
    """Clean transcript text by removing extra whitespace, etc."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_transcript_text(transcript):
    """Convert transcript segments to a single text."""
    if not transcript:
        return ""
    return " ".join([clean_text(entry['text']) for entry in transcript])

def analyze_topic(text, num_sentences=5):
    """Extract the most representative sentences to identify the topic."""
    # Split into sentences (simple approach)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if not sentences:
        return "Could not identify topic due to insufficient transcript text."
    
    # If we have very few sentences, just return them all
    if len(sentences) <= num_sentences:
        return "\n".join(sentences)
    
    # Use sentence embeddings to find most central sentences
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(sentences, convert_to_numpy=True)
    
    # Calculate centroid
    centroid = np.mean(embeddings, axis=0)
    
    # Calculate similarity to centroid
    similarities = np.dot(embeddings, centroid) / (np.linalg.norm(embeddings, axis=1) * np.linalg.norm(centroid))
    
    # Get indices of top sentences
    top_indices = np.argsort(similarities)[-num_sentences:]
    
    # Sort indices by position in original text to maintain narrative flow
    top_indices = sorted(top_indices)
    
    # Return top sentences
    return "\n".join([f"{i+1}. {sentences[idx]}" for i, idx in enumerate(top_indices)])

def search_transcript(transcript, query, video_id, num_results=3):
    """Search for relevant sections in the transcript based on a query."""
    if not transcript:
        return []
    
    # Create segments from transcript
    segments = []
    segment_size = 5  # Number of entries per segment
    overlap = 2  # Overlap between segments
    
    # Process transcript into overlapping segments
    for i in range(0, len(transcript), segment_size - overlap):
        end_idx = min(i + segment_size, len(transcript))
        segment_text = " ".join([entry["text"] for entry in transcript[i:end_idx]])
        start_time = transcript[i]["start"]
        segments.append({
            "text": clean_text(segment_text),
            "start_time": start_time,
            "end_idx": end_idx
        })
    
    # Use sentence embeddings to find most relevant segments
    model = SentenceTransformer("all-MiniLM-L6-v2")
    segment_texts = [segment["text"] for segment in segments]
    
    # Generate embeddings for segments and query
    segment_embeddings = model.encode(segment_texts, convert_to_numpy=True)
    query_embedding = model.encode([query], convert_to_numpy=True)[0]
    
    # Calculate similarities
    similarities = np.dot(segment_embeddings, query_embedding) / (
        np.linalg.norm(segment_embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    
    # Get top N results
    top_indices = np.argsort(similarities)[-num_results:][::-1]  # Reverse to get highest first
    
    results = []
    for idx in top_indices:
        segment = segments[idx]
        timestamp = format_timestamp(segment["start_time"])
        results.append({
            "text": segment["text"],
            "start_time": segment["start_time"],
            "timestamp": timestamp,
            "similarity": similarities[idx],
            "video_url": f"https://www.youtube.com/watch?v={video_id}&t={int(segment['start_time'])}"
        })
    
    return results

def format_timestamp(seconds):
    """Format seconds into MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def answer_question(query, transcript, video_id):
    """Answer a question based on the video transcript."""
    if not transcript:
        return "Sorry, I couldn't retrieve the transcript for this video."
    
    # Search for relevant segments
    relevant_segments = search_transcript(transcript, query, video_id)
    
    if not relevant_segments:
        return "I couldn't find information related to your question in this video."
    
    # Format answer with context from the relevant segments
    answer = f"Based on the video, here's what I found about your question:\n\n"
    
    for i, segment in enumerate(relevant_segments):
        answer += f"**Segment {i+1}** (at {segment['timestamp']}):\n"
        answer += f"{segment['text']}\n"
        answer += f"[View in video]({segment['video_url']})\n\n"
    
    return answer

def main():
    """Extract and analyze the topic of a YouTube video."""
    # New video URL
    video_url = "https://www.youtube.com/watch?v=G-fXV-o9QV8"
    
    try:
        # Extract video ID and get transcript
        video_id = extract_video_id(video_url)
        print(f"Processing video ID: {video_id}")
        
        transcript = get_transcript(video_id)
        if not transcript:
            print("Failed to retrieve transcript. Exiting.")
            return
        
        print(f"Retrieved transcript with {len(transcript)} entries")
        
        # Get full text and analyze
        full_text = get_transcript_text(transcript)
        print("\nFull transcript length:", len(full_text), "characters")
        
        print("\n===== VIDEO TOPIC ANALYSIS =====")
        topic_summary = analyze_topic(full_text)
        print(topic_summary)
        
        # Interactive Q&A mode
        print("\n===== INTERACTIVE Q&A =====")
        print("You can now ask questions about the video (type 'exit' to quit):")
        
        while True:
            user_query = input("\nYour question: ")
            if user_query.lower() in ["exit", "quit", "q"]:
                break
            
            print("\nSearching for answer...\n")
            answer = answer_question(user_query, transcript, video_id)
            print(answer)
        
    except Exception as e:
        print(f"Error analyzing video: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 