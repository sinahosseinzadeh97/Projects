"""
Simple end-to-end test for a YouTube QA flow.
This script:
1. Gets the transcript for a YouTube video
2. Generates embeddings for the transcript segments
3. Simulates a simple QA flow using semantic search
"""

import numpy as np
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer, util

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
        print(f"Getting transcript for video ID: {video_id}")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error getting transcript: {str(e)}")
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
            "video_id": "-nvJIfQnidw"  # Hard-coded for this test
        })
    
    return formatted_segments

def embed_segments(segments: List[Dict], model: SentenceTransformer) -> Dict:
    """Generate embeddings for transcript segments."""
    texts = [segment["text"] for segment in segments]
    
    print(f"Generating embeddings for {len(texts)} segments...")
    embeddings = model.encode(texts, convert_to_tensor=True)
    
    # Store segment info with its embedding
    embedded_segments = {
        "segments": segments,
        "embeddings": embeddings
    }
    
    return embedded_segments

def search_segments(question: str, embedded_segments: Dict, model: SentenceTransformer, top_k: int = 3) -> List[Dict]:
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

def answer_question(question: str, results: List[Dict]) -> str:
    """Generate a simple answer based on the search results."""
    # For this simple test, we'll just concatenate the retrieved segments
    answer = f"Based on the video content, here's what I found:\n\n"
    
    for i, result in enumerate(results):
        segment = result["segment"]
        score = result["score"]
        
        answer += f"{i+1}. [{segment['start_time']:.2f}s] {segment['text']} (relevance: {score:.4f})\n\n"
    
    return answer

def run_qa_test(video_url: str, questions: List[str]):
    """Run the end-to-end QA test."""
    print("=== Starting YouTube QA Test ===")
    
    # Step 1: Get transcript
    transcript = get_transcript(video_url)
    if not transcript:
        print("Failed to get transcript. Aborting test.")
        return
    
    print(f"Successfully retrieved transcript with {len(transcript)} segments")
    
    # Step 2: Format transcript segments
    segments = format_transcript_segments(transcript)
    print(f"Formatted {len(segments)} segments")
    
    # Step 3: Load embedding model
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded successfully")
    
    # Step 4: Generate embeddings
    embedded_segments = embed_segments(segments, model)
    print("Embeddings generated successfully")
    
    # Step 5: Answer questions
    print("\n=== Answering Questions ===\n")
    
    for i, question in enumerate(questions):
        print(f"Q{i+1}: {question}")
        
        # Search for relevant segments
        results = search_segments(question, embedded_segments, model)
        
        # Generate answer
        answer = answer_question(question, results)
        
        print(f"A{i+1}: {answer}")
        print("-" * 80)

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=-nvJIfQnidw"
    
    questions = [
        "How can you validate a startup idea without building it?",
        "What methods did Justin Mayers discuss for startup validation?",
        "What are the key takeaways from this video?"
    ]
    
    run_qa_test(video_url, questions) 