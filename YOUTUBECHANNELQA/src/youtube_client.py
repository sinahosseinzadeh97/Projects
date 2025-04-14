"""
YouTube API Client Module

This module provides functionality to interact with the YouTube Data API v3
to retrieve videos and their metadata from a specified channel.
"""

import os
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeClient:
    """Client for interacting with the YouTube Data API."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the YouTube client.
        
        Args:
            api_key (str, optional): YouTube API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.environ.get('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key is required. Provide it directly or set YOUTUBE_API_KEY environment variable.")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve videos from a specific YouTube channel.
        
        Args:
            channel_id (str): YouTube channel ID
            max_results (int, optional): Maximum number of videos to retrieve. Defaults to 50.
            
        Returns:
            List[Dict[str, Any]]: List of video metadata dictionaries
        """
        try:
            # First, search for videos in the channel
            search_response = self.youtube.search().list(
                part='id,snippet',
                channelId=channel_id,
                maxResults=max_results,
                type='video',
                order='date'  # Get most recent videos first
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            if not video_ids:
                return []
            
            # Then, get detailed information about those videos
            videos_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()
            
            videos = []
            for item in videos_response.get('items', []):
                video = {
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
                    'duration': item['contentDetails']['duration'],
                    'view_count': item['statistics'].get('viewCount', 0),
                    'like_count': item['statistics'].get('likeCount', 0),
                    'comment_count': item['statistics'].get('commentCount', 0)
                }
                videos.append(video)
            
            return videos
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []
    
    def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific video.
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            Optional[Dict[str, Any]]: Video metadata dictionary or None if not found
        """
        try:
            response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            
            items = response.get('items', [])
            if not items:
                return None
            
            item = items[0]
            video = {
                'id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'channel_id': item['snippet']['channelId'],
                'channel_title': item['snippet']['channelTitle'],
                'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
                'duration': item['contentDetails']['duration'],
                'view_count': item['statistics'].get('viewCount', 0),
                'like_count': item['statistics'].get('likeCount', 0),
                'comment_count': item['statistics'].get('commentCount', 0)
            }
            
            return video
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None
    
    def get_channel_id_from_username(self, username: str) -> Optional[str]:
        """
        Get channel ID from a YouTube username.
        
        Args:
            username (str): YouTube username
            
        Returns:
            Optional[str]: Channel ID or None if not found
        """
        try:
            response = self.youtube.channels().list(
                part='id',
                forUsername=username
            ).execute()
            
            items = response.get('items', [])
            if not items:
                return None
            
            return items[0]['id']
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None
    
    def get_channel_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract channel ID from a YouTube channel URL.
        
        Args:
            url (str): YouTube channel URL
            
        Returns:
            Optional[str]: Channel ID or None if not extractable
        """
        # Handle different URL formats
        if 'youtube.com/channel/' in url:
            # Format: https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw
            parts = url.split('youtube.com/channel/')
            if len(parts) > 1:
                return parts[1].split('/')[0].split('?')[0]
        elif 'youtube.com/c/' in url:
            # Format: https://www.youtube.com/c/ChannelName
            # Need to make an API call to resolve custom URL
            custom_name = url.split('youtube.com/c/')[1].split('/')[0].split('?')[0]
            try:
                response = self.youtube.search().list(
                    part='snippet',
                    q=custom_name,
                    type='channel',
                    maxResults=1
                ).execute()
                
                items = response.get('items', [])
                if items:
                    return items[0]['snippet']['channelId']
            except HttpError as e:
                print(f"An HTTP error occurred: {e}")
                return None
        elif 'youtube.com/user/' in url:
            # Format: https://www.youtube.com/user/UserName
            username = url.split('youtube.com/user/')[1].split('/')[0].split('?')[0]
            return self.get_channel_id_from_username(username)
        
        return None
