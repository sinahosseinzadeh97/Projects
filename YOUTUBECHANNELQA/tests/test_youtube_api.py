"""
Test script for YouTube API module

This script tests the functionality of the YouTube API client module.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.youtube_api.youtube_client import YouTubeClient

class TestYouTubeClient(unittest.TestCase):
    """Test cases for YouTubeClient class."""
    
    def setUp(self):
        """Set up test environment."""
        # Use a test API key for testing
        self.test_api_key = "test_api_key"
        
        # Create a patcher for the build function
        self.build_patcher = patch('src.youtube_api.youtube_client.build')
        self.mock_build = self.build_patcher.start()
        
        # Create mock YouTube API client
        self.mock_youtube = MagicMock()
        self.mock_build.return_value = self.mock_youtube
        
        # Create YouTubeClient instance with test API key
        self.client = YouTubeClient(api_key=self.test_api_key)
    
    def tearDown(self):
        """Clean up after tests."""
        self.build_patcher.stop()
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        self.assertEqual(self.client.api_key, self.test_api_key)
        self.mock_build.assert_called_once_with('youtube', 'v3', developerKey=self.test_api_key)
    
    @patch.dict(os.environ, {'YOUTUBE_API_KEY': 'env_api_key'})
    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        client = YouTubeClient()
        self.assertEqual(client.api_key, 'env_api_key')
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                YouTubeClient()
    
    def test_get_channel_videos(self):
        """Test get_channel_videos method."""
        # Mock search.list and videos.list methods
        mock_search = MagicMock()
        mock_videos = MagicMock()
        self.mock_youtube.search.return_value.list.return_value = mock_search
        self.mock_youtube.videos.return_value.list.return_value = mock_videos
        
        # Mock search response
        mock_search.execute.return_value = {
            'items': [
                {'id': {'videoId': 'video1'}, 'snippet': {'title': 'Test Video 1'}},
                {'id': {'videoId': 'video2'}, 'snippet': {'title': 'Test Video 2'}}
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
                },
                {
                    'id': 'video2',
                    'snippet': {
                        'title': 'Test Video 2',
                        'description': 'Description 2',
                        'publishedAt': '2023-01-02T00:00:00Z',
                        'channelId': 'channel1',
                        'channelTitle': 'Test Channel',
                        'thumbnails': {'high': {'url': 'https://example.com/thumb2.jpg'}}
                    },
                    'contentDetails': {'duration': 'PT3M45S'},
                    'statistics': {'viewCount': '2000', 'likeCount': '200', 'commentCount': '20'}
                }
            ]
        }
        
        # Call the method
        videos = self.client.get_channel_videos('channel1', max_results=2)
        
        # Verify the results
        self.assertEqual(len(videos), 2)
        self.assertEqual(videos[0]['id'], 'video1')
        self.assertEqual(videos[0]['title'], 'Test Video 1')
        self.assertEqual(videos[1]['id'], 'video2')
        self.assertEqual(videos[1]['title'], 'Test Video 2')
        
        # Verify the API calls
        self.mock_youtube.search.return_value.list.assert_called_once_with(
            part='id,snippet',
            channelId='channel1',
            maxResults=2,
            type='video',
            order='date'
        )
        self.mock_youtube.videos.return_value.list.assert_called_once_with(
            part='snippet,contentDetails,statistics',
            id='video1,video2'
        )
    
    def test_get_video_details(self):
        """Test get_video_details method."""
        # Mock videos.list method
        mock_videos = MagicMock()
        self.mock_youtube.videos.return_value.list.return_value = mock_videos
        
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
        
        # Call the method
        video = self.client.get_video_details('video1')
        
        # Verify the results
        self.assertIsNotNone(video)
        self.assertEqual(video['id'], 'video1')
        self.assertEqual(video['title'], 'Test Video 1')
        
        # Verify the API call
        self.mock_youtube.videos.return_value.list.assert_called_once_with(
            part='snippet,contentDetails,statistics',
            id='video1'
        )
    
    def test_get_channel_id_from_url(self):
        """Test get_channel_id_from_url method."""
        # Test direct channel URL
        url = "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw"
        channel_id = self.client.get_channel_id_from_url(url)
        self.assertEqual(channel_id, "UC_x5XG1OV2P6uZZ5FSM9Ttw")
        
        # Test custom URL (requires API call)
        url = "https://www.youtube.com/c/GoogleDevelopers"
        
        # Mock search.list method
        mock_search = MagicMock()
        self.mock_youtube.search.return_value.list.return_value = mock_search
        
        # Mock search response
        mock_search.execute.return_value = {
            'items': [
                {
                    'snippet': {
                        'channelId': 'UC_x5XG1OV2P6uZZ5FSM9Ttw'
                    }
                }
            ]
        }
        
        channel_id = self.client.get_channel_id_from_url(url)
        self.assertEqual(channel_id, "UC_x5XG1OV2P6uZZ5FSM9Ttw")
        
        # Verify the API call
        self.mock_youtube.search.return_value.list.assert_called_once_with(
            part='snippet',
            q='GoogleDevelopers',
            type='channel',
            maxResults=1
        )

if __name__ == '__main__':
    unittest.main()
