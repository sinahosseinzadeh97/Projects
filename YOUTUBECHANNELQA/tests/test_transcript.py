"""
Simple script to test if we can get the transcript for a YouTube video.
"""

from youtube_transcript_api import YouTubeTranscriptApi
import sys

def get_video_id(url_or_id):
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

def get_transcript(video_id_or_url):
    """Get transcript for a YouTube video."""
    video_id = get_video_id(video_id_or_url)
    
    try:
        print(f"Getting transcript for video ID: {video_id}")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error getting transcript: {str(e)}")
        return None

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=-nvJIfQnidw"
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
    
    transcript = get_transcript(video_url)
    
    if transcript:
        print(f"Successfully retrieved transcript with {len(transcript)} segments")
        print("\nFirst 3 segments:")
        for i, segment in enumerate(transcript[:3]):
            print(f"{i+1}. [{segment['start']:.2f}s] {segment['text']}")
    else:
        print("Failed to retrieve transcript") 