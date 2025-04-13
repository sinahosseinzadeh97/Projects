#!/usr/bin/env python
"""
Setup script to configure API keys for testing the YouTube Q&A system.
This script prompts for YouTube and OpenAI API keys and sets them as environment variables.
"""

import os
import sys
import argparse
from getpass import getpass

def save_api_keys_to_env(youtube_key, openai_key):
    """Save API keys to environment variables."""
    os.environ['YOUTUBE_API_KEY'] = youtube_key
    os.environ['OPENAI_API_KEY'] = openai_key
    print("API keys set as environment variables for the current session.")

def save_api_keys_to_file(youtube_key, openai_key, file_path='.env'):
    """Save API keys to a .env file."""
    with open(file_path, 'w') as f:
        f.write(f"YOUTUBE_API_KEY={youtube_key}\n")
        f.write(f"OPENAI_API_KEY={openai_key}\n")
    print(f"API keys saved to {file_path}")
    print("You can load these keys using:")
    print("  - For bash/zsh: source .env")
    print("  - For Python: from dotenv import load_dotenv; load_dotenv()")

def main():
    """Main function to prompt for and save API keys."""
    parser = argparse.ArgumentParser(description='Setup API keys for YouTube Q&A system.')
    parser.add_argument('--file', '-f', action='store_true', help='Save API keys to .env file')
    args = parser.parse_args()
    
    print("Setup API keys for YouTube Q&A system")
    print("====================================")
    
    # Check if keys are already set
    youtube_key = os.environ.get('YOUTUBE_API_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY')
    
    if youtube_key:
        print(f"YouTube API key already set: {youtube_key[:4]}...{youtube_key[-4:]}")
        change = input("Change this key? (y/n): ").lower()
        if change == 'y':
            youtube_key = getpass("Enter YouTube API key: ")
    else:
        print("YouTube API key not found in environment variables.")
        youtube_key = getpass("Enter YouTube API key: ")
    
    if openai_key:
        print(f"OpenAI API key already set: {openai_key[:4]}...{openai_key[-4:]}")
        change = input("Change this key? (y/n): ").lower()
        if change == 'y':
            openai_key = getpass("Enter OpenAI API key: ")
    else:
        print("OpenAI API key not found in environment variables.")
        openai_key = getpass("Enter OpenAI API key: ")
    
    # Save keys to environment variables
    save_api_keys_to_env(youtube_key, openai_key)
    
    # Optionally save to file
    if args.file:
        save_api_keys_to_file(youtube_key, openai_key)
    
    print("\nAPI keys configured successfully!")
    print("You can now run: python test_youtube_video.py")

if __name__ == "__main__":
    main() 