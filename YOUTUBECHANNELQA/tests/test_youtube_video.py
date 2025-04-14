"""
Test script for YouTube Q&A system with a specific video.

This script processes a specific YouTube video, extracts its transcript,
generates embeddings, and allows for asking questions about the content.
"""

import os
import sys
import logging
from typing import Dict, Any, List

# Import system modules
from youtube_client import YouTubeClient
from transcript_extractor import TranscriptExtractor
from embedding_generator import EmbeddingGenerator
from vector_search_engine import VectorSearchEngine
from openai_generator import OpenAIGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeVideoProcessor:
    """Class to process a specific YouTube video and answer questions about it."""
    
    def __init__(self, youtube_api_key: str = None, openai_api_key: str = None):
        """Initialize with API keys."""
        self.youtube_api_key = youtube_api_key or os.environ.get('YOUTUBE_API_KEY')
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        
        if not self.youtube_api_key:
            raise ValueError("YouTube API key is required. Provide it directly or set YOUTUBE_API_KEY environment variable.")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Provide it directly or set OPENAI_API_KEY environment variable.")
            
        # Initialize components
        self.youtube_client = YouTubeClient(api_key=self.youtube_api_key)
        self.transcript_extractor = TranscriptExtractor()
        self.embedding_generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
        self.vector_search = VectorSearchEngine()
        self.openai_generator = OpenAIGenerator(api_key=self.openai_api_key)
        
        # Storage for processed data
        self.video_data = None
        self.transcript = None
        self.segments = None
        self.embeddings = None
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from a YouTube URL."""
        if 'youtu.be' in url:
            # Format: https://youtu.be/VIDEO_ID
            video_id = url.split('/')[-1].split('?')[0]
        elif 'youtube.com/watch' in url:
            # Format: https://www.youtube.com/watch?v=VIDEO_ID
            import re
            match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
            if match:
                video_id = match.group(1)
            else:
                raise ValueError(f"Could not extract video ID from URL: {url}")
        else:
            raise ValueError(f"Unsupported YouTube URL format: {url}")
            
        return video_id
    
    def process_video(self, url: str) -> Dict[str, Any]:
        """Process a YouTube video from its URL."""
        # Extract video ID
        video_id = self.extract_video_id(url)
        logger.info(f"Processing video with ID: {video_id}")
        
        # Get video details
        self.video_data = self.youtube_client.get_video_details(video_id)
        if not self.video_data:
            raise ValueError(f"Could not retrieve video data for ID: {video_id}")
            
        logger.info(f"Retrieved video: {self.video_data['title']}")
        
        # Extract transcript
        self.transcript = self.transcript_extractor.get_transcript(video_id)
        if not self.transcript:
            raise ValueError(f"Could not extract transcript for video ID: {video_id}")
            
        logger.info(f"Extracted transcript with {len(self.transcript)} entries")
        
        # Segment the transcript
        self.segments = self.transcript_extractor.segment_transcript(
            self.transcript, 
            segment_length=300,  # Longer segments for more context
            overlap=50
        )
        
        logger.info(f"Created {len(self.segments)} transcript segments")
        
        # Enhance segments with video metadata
        for segment in self.segments:
            segment['video_id'] = video_id
            segment['video_title'] = self.video_data['title']
            segment['link'] = self.transcript_extractor.generate_video_url_with_timestamp(
                video_id, segment['start']
            )
        
        # Generate embeddings for segments
        self.segments = self.embedding_generator.generate_embeddings_for_segments(self.segments)
        logger.info(f"Generated embeddings for all segments")
        
        # Create vector index
        embeddings = [segment['embedding'] for segment in self.segments]
        self.vector_search.create_index(embeddings)
        self.vector_search.metadata = self.segments
        
        logger.info(f"Created vector search index")
        
        return {
            'video': self.video_data,
            'segments_count': len(self.segments)
        }
    
    def ask_question(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Ask a question about the processed video."""
        if not self.segments or not self.vector_search.index:
            raise ValueError("No video has been processed yet. Call process_video first.")
            
        logger.info(f"Processing question: {question}")
        
        # Generate embedding for the question
        question_embedding = self.embedding_generator.generate_embedding(question)
        
        # Search for relevant segments
        _, _, result_segments = self.vector_search.search(question_embedding, k=k)
        
        logger.info(f"Found {len(result_segments)} relevant segments")
        
        # Generate answer with references
        result = self.openai_generator.generate_answer_with_references(
            question, 
            result_segments
        )
        
        return result

def main():
    """Main entry point for the script."""
    # Check for API keys
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    if not youtube_api_key:
        logger.error("YouTube API key not found. Please set the YOUTUBE_API_KEY environment variable.")
        sys.exit(1)
        
    if not openai_api_key:
        logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Process the specified video
    video_url = "https://www.youtube.com/watch?v=NtLytfhtrTA&t=1s"
    processor = YouTubeVideoProcessor(youtube_api_key, openai_api_key)
    
    try:
        # Process the video
        result = processor.process_video(video_url)
        logger.info(f"Successfully processed video: {result['video']['title']}")
        logger.info(f"Created {result['segments_count']} segments")
        
        # Ask a sample question
        sample_question = "What is the main idea discussed in this video?"
        answer = processor.ask_question(sample_question)
        
        print("\n" + "="*80)
        print(f"Question: {answer['question']}")
        print("-"*80)
        print(f"Answer: {answer['answer']}")
        print("-"*80)
        print("References:")
        for i, ref in enumerate(answer['references']):
            print(f"  {i+1}. {ref['video_title']} ({ref['link']})")
        print("="*80 + "\n")
        
        # Interactive mode
        print("You can now ask questions about the video (type 'exit' to quit):")
        while True:
            user_question = input("\nYour question: ")
            if user_question.lower() in ['exit', 'quit', 'q']:
                break
                
            answer = processor.ask_question(user_question)
            
            print("\n" + "-"*80)
            print(f"Answer: {answer['answer']}")
            print("-"*80)
            print("References:")
            for i, ref in enumerate(answer['references']):
                print(f"  {i+1}. {ref['video_title']} at {ref['start_time']:.1f}s")
                print(f"      {ref['link']}")
            print("-"*80)
            
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 