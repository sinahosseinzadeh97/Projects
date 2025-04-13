"""
Test script for Transcript Extraction module

This script tests the functionality of the transcript extraction module.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.transcript.transcript_extractor import TranscriptExtractor

class TestTranscriptExtractor(unittest.TestCase):
    """Test cases for TranscriptExtractor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.extractor = TranscriptExtractor()
    
    @patch('src.transcript.transcript_extractor.YouTubeTranscriptApi')
    def test_get_transcript(self, mock_transcript_api):
        """Test get_transcript method."""
        # Mock transcript API response
        mock_transcript = [
            {'text': 'First segment', 'start': 0.0, 'duration': 5.0},
            {'text': 'Second segment', 'start': 5.0, 'duration': 4.0},
            {'text': 'Third segment', 'start': 9.0, 'duration': 6.0}
        ]
        mock_transcript_api.get_transcript.return_value = mock_transcript
        
        # Call the method
        result = self.extractor.get_transcript('video123', languages=['en'])
        
        # Verify the results
        self.assertEqual(result, mock_transcript)
        
        # Verify the API call
        mock_transcript_api.get_transcript.assert_called_once_with('video123', languages=['en'])
    
    @patch('src.transcript.transcript_extractor.YouTubeTranscriptApi')
    def test_get_transcript_error(self, mock_transcript_api):
        """Test get_transcript method with error."""
        # Mock transcript API error
        mock_transcript_api.get_transcript.side_effect = Exception("Transcript not available")
        
        # Call the method
        result = self.extractor.get_transcript('video123')
        
        # Verify the results
        self.assertIsNone(result)
    
    @patch('src.transcript.transcript_extractor.YouTubeTranscriptApi')
    def test_get_transcript_as_text(self, mock_transcript_api):
        """Test get_transcript_as_text method."""
        # Mock transcript API response
        mock_transcript = [
            {'text': 'First segment', 'start': 0.0, 'duration': 5.0},
            {'text': 'Second segment', 'start': 5.0, 'duration': 4.0},
            {'text': 'Third segment', 'start': 9.0, 'duration': 6.0}
        ]
        mock_transcript_api.get_transcript.return_value = mock_transcript
        
        # Mock formatter
        self.extractor.formatter.format_transcript = MagicMock(return_value="First segment Second segment Third segment")
        
        # Call the method
        result = self.extractor.get_transcript_as_text('video123')
        
        # Verify the results
        self.assertEqual(result, "First segment Second segment Third segment")
        
        # Verify the formatter call
        self.extractor.formatter.format_transcript.assert_called_once_with(mock_transcript)
    
    def test_segment_transcript(self):
        """Test segment_transcript method."""
        # Test transcript
        transcript = [
            {'text': 'This is the first segment of text.', 'start': 0.0, 'duration': 5.0},
            {'text': 'This is the second segment.', 'start': 5.0, 'duration': 4.0},
            {'text': 'This is the third segment of the transcript.', 'start': 9.0, 'duration': 6.0},
            {'text': 'This is the fourth segment.', 'start': 15.0, 'duration': 3.0},
            {'text': 'This is the fifth and final segment.', 'start': 18.0, 'duration': 5.0}
        ]
        
        # Call the method with segment length that should create 2 segments
        result = self.extractor.segment_transcript(transcript, segment_length=60, overlap=10)
        
        # Verify the results
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]['text'].startswith('This is the first segment'))
        self.assertTrue(result[1]['text'].startswith('This is the fourth segment'))
        
        # Test with empty transcript
        result = self.extractor.segment_transcript([], segment_length=100, overlap=20)
        self.assertEqual(result, [])
    
    def test_clean_text(self):
        """Test _clean_text method."""
        # Test with extra whitespace
        text = "  This   has  extra   spaces.  "
        result = self.extractor._clean_text(text)
        self.assertEqual(result, "This has extra spaces.")
    
    def test_generate_video_url_with_timestamp(self):
        """Test generate_video_url_with_timestamp method."""
        # Test with integer timestamp
        result = self.extractor.generate_video_url_with_timestamp('video123', 60)
        self.assertEqual(result, "https://www.youtube.com/watch?v=video123&t=60")
        
        # Test with float timestamp
        result = self.extractor.generate_video_url_with_timestamp('video123', 60.5)
        self.assertEqual(result, "https://www.youtube.com/watch?v=video123&t=60")

if __name__ == '__main__':
    unittest.main()
