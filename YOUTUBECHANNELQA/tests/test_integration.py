"""
Integration test script for YouTube Q&A system

This script tests the integration between different modules of the system.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.youtube_api.youtube_client import YouTubeClient
from src.transcript.transcript_extractor import TranscriptExtractor
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.vector_search.vector_search_engine import VectorSearchEngine
from src.openai_integration.openai_generator import OpenAIGenerator

class TestSystemIntegration(unittest.TestCase):
    """Integration tests for the YouTube Q&A system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create patchers for external APIs
        self.youtube_api_patcher = patch('src.youtube_api.youtube_client.build')
        self.transcript_api_patcher = patch('src.transcript.transcript_extractor.YouTubeTranscriptApi')
        self.sentence_transformer_patcher = patch('src.embeddings.embedding_generator.SentenceTransformer')
        self.faiss_patcher = patch('src.vector_search.vector_search_engine.faiss')
        self.openai_patcher = patch('src.openai_integration.openai_generator.OpenAI')
        
        # Start patchers
        self.mock_youtube_api = self.youtube_api_patcher.start()
        self.mock_transcript_api = self.transcript_api_patcher.start()
        self.mock_sentence_transformer = self.sentence_transformer_patcher.start()
        self.mock_faiss = self.faiss_patcher.start()
        self.mock_openai = self.openai_patcher.start()
        
        # Set up mock returns
        self.setup_youtube_mocks()
        self.setup_transcript_mocks()
        self.setup_embedding_mocks()
        self.setup_openai_mocks()
        
        # Create module instances
        self.youtube_client = YouTubeClient(api_key="test_api_key")
        self.transcript_extractor = TranscriptExtractor()
        self.embedding_generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
        self.vector_search = VectorSearchEngine(dimension=384)
        self.openai_generator = OpenAIGenerator(api_key="test_api_key")
    
    def tearDown(self):
        """Clean up after tests."""
        self.youtube_api_patcher.stop()
        self.transcript_api_patcher.stop()
        self.sentence_transformer_patcher.stop()
        self.faiss_patcher.stop()
        self.openai_patcher.stop()
    
    def setup_youtube_mocks(self):
        """Set up mocks for YouTube API."""
        mock_youtube = MagicMock()
        mock_search = MagicMock()
        mock_videos = MagicMock()
        
        mock_youtube.search.return_value.list.return_value = mock_search
        mock_youtube.videos.return_value.list.return_value = mock_videos
        
        # Mock search response
        mock_search.execute.return_value = {
            'items': [
                {'id': {'videoId': 'video1'}, 'snippet': {'title': 'Test Video 1'}}
            ]
        }
        
        # Mock videos response
        mock_videos.execute.return_value = {
            'items': [
                {
                    'id': 'video1',
                    'snippet': {
                        'title': 'Test Video 1',
                        'description': 'Description 1',
                        'publishedAt': '2023-01-01T00:00:00Z',
                        'channelId': 'channel1',
                        'channelTitle': 'Test Channel',
                        'thumbnails': {'high': {'url': 'https://example.com/thumb1.jpg'}}
                    },
                    'contentDetails': {'duration': 'PT5M30S'},
                    'statistics': {'viewCount': '1000', 'likeCount': '100', 'commentCount': '10'}
                }
            ]
        }
        
        self.mock_youtube_api.return_value = mock_youtube
    
    def setup_transcript_mocks(self):
        """Set up mocks for transcript API."""
        # Mock transcript API response
        mock_transcript = [
            {'text': 'First segment', 'start': 0.0, 'duration': 5.0},
            {'text': 'Second segment', 'start': 5.0, 'duration': 4.0},
            {'text': 'Third segment', 'start': 9.0, 'duration': 6.0}
        ]
        self.mock_transcript_api.get_transcript.return_value = mock_transcript
    
    def setup_embedding_mocks(self):
        """Set up mocks for embedding model."""
        # Create mock model
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.get_max_seq_length.return_value = 512
        
        # Mock embeddings
        mock_embeddings = [
            [0.1, 0.2, 0.3] * 128,  # 384-dimensional vector
            [0.4, 0.5, 0.6] * 128,
            [0.7, 0.8, 0.9] * 128
        ]
        mock_model.encode.return_value = mock_embeddings
        
        self.mock_sentence_transformer.return_value = mock_model
    
    def setup_openai_mocks(self):
        """Set up mocks for OpenAI API."""
        # Mock OpenAI client
        mock_client = MagicMock()
        
        # Mock chat completions
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "The recommended valuation multiple is around 4-6x EBITDA."
        
        mock_client.chat.completions.create.return_value = mock_response
        
        self.mock_openai.return_value = mock_client
    
    def test_end_to_end_flow(self):
        """Test the end-to-end flow from video retrieval to answer generation."""
        # Step 1: Get videos from channel
        videos = self.youtube_client.get_channel_videos('channel1', max_results=1)
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]['id'], 'video1')
        
        # Step 2: Get transcript for video
        video_id = videos[0]['id']
        transcript = self.transcript_extractor.get_transcript(video_id)
        self.assertEqual(len(transcript), 3)
        
        # Step 3: Segment transcript
        segments = self.transcript_extractor.segment_transcript(transcript)
        self.assertGreaterEqual(len(segments), 1)
        
        # Step 4: Generate embeddings for segments
        segments_with_embeddings = self.embedding_generator.generate_embeddings_for_segments(segments)
        self.assertEqual(len(segments_with_embeddings), len(segments))
        self.assertTrue('embedding' in segments_with_embeddings[0])
        
        # Step 5: Create vector index
        embeddings = [segment['embedding'] for segment in segments_with_embeddings]
        self.vector_search.create_index(embeddings)
        
        # Add metadata to vector search
        metadata = []
        for i, segment in enumerate(segments_with_embeddings):
            metadata.append({
                'video_id': video_id,
                'video_title': videos[0]['title'],
                'start_time': segment['start'],
                'text': segment['text']
            })
        self.vector_search.metadata = metadata
        
        # Step 6: Process a query
        query = "What is the recommended valuation multiple?"
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Step 7: Search for similar segments
        distances, indices, result_metadata = self.vector_search.search(query_embedding, k=2)
        self.assertEqual(len(result_metadata), 2)
        
        # Step 8: Generate answer
        answer = self.openai_generator.generate_answer_with_references(query, result_metadata)
        self.assertEqual(answer['question'], query)
        self.assertTrue('answer' in answer)
        self.assertTrue('references' in answer)
        self.assertEqual(len(answer['references']), 2)
    
    def test_error_handling_no_transcript(self):
        """Test error handling when no transcript is available."""
        # Mock transcript API to return None
        self.mock_transcript_api.get_transcript.side_effect = Exception("No transcript available")
        
        # Get videos from channel
        videos = self.youtube_client.get_channel_videos('channel1', max_results=1)
        video_id = videos[0]['id']
        
        # Try to get transcript
        transcript = self.transcript_extractor.get_transcript(video_id)
        self.assertIsNone(transcript)
        
        # Verify the system handles this gracefully
        transcript_text = self.transcript_extractor.get_transcript_as_text(video_id)
        self.assertIsNone(transcript_text)

if __name__ == '__main__':
    unittest.main()
