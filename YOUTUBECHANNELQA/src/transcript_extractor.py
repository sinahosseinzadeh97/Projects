"""
Transcript Extraction Module

This module provides functionality to extract and process transcripts from YouTube videos
using the youtube-transcript-api library.
"""

import re
from typing import List, Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

class TranscriptExtractor:
    """Class for extracting and processing YouTube video transcripts."""
    
    def __init__(self):
        """Initialize the transcript extractor."""
        self.formatter = TextFormatter()
    
    def get_transcript(self, video_id: str, languages: List[str] = ['en']) -> Optional[List[Dict[str, Any]]]:
        """
        Extract transcript for a specific YouTube video.
        
        Args:
            video_id (str): YouTube video ID
            languages (List[str], optional): List of language codes to try. Defaults to ['en'].
            
        Returns:
            Optional[List[Dict[str, Any]]]: List of transcript segments or None if not available
        """
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            return transcript
        except Exception as e:
            print(f"Error extracting transcript for video {video_id}: {e}")
            return None
    
    def get_transcript_as_text(self, video_id: str, languages: List[str] = ['en']) -> Optional[str]:
        """
        Extract transcript as plain text for a specific YouTube video.
        
        Args:
            video_id (str): YouTube video ID
            languages (List[str], optional): List of language codes to try. Defaults to ['en'].
            
        Returns:
            Optional[str]: Transcript text or None if not available
        """
        transcript = self.get_transcript(video_id, languages)
        if not transcript:
            return None
        
        return self.formatter.format_transcript(transcript)
    
    def segment_transcript(self, transcript: List[Dict[str, Any]], 
                          segment_length: int = 100, 
                          overlap: int = 20) -> List[Dict[str, Any]]:
        """
        Split transcript into logical segments for embedding.
        
        Args:
            transcript (List[Dict[str, Any]]): Raw transcript from YouTube
            segment_length (int, optional): Target character length for segments. Defaults to 100.
            overlap (int, optional): Character overlap between segments. Defaults to 20.
            
        Returns:
            List[Dict[str, Any]]: List of processed transcript segments
        """
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
            segment['text'] = self._clean_text(segment['text'])
        
        return segments
    
    def _clean_text(self, text: str) -> str:
        """
        Clean transcript text by removing extra whitespace, etc.
        
        Args:
            text (str): Raw transcript text
            
        Returns:
            str: Cleaned transcript text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def generate_video_url_with_timestamp(self, video_id: str, start_time: float) -> str:
        """
        Generate a YouTube URL that starts at a specific timestamp.
        
        Args:
            video_id (str): YouTube video ID
            start_time (float): Start time in seconds
            
        Returns:
            str: YouTube URL with timestamp
        """
        return f"https://www.youtube.com/watch?v={video_id}&t={int(start_time)}"
