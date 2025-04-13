# User Guide

## Introduction

Welcome to the YouTube Q&A System! This guide will help you get started with using the system to ask questions about content from educational YouTube channels.

## Getting Started

### Installation

Before using the system, make sure you have installed it following the instructions in the README.md file.

### Setting Up API Keys

The system requires two API keys to function:

1. **YouTube API Key**: Used to retrieve videos and transcripts from YouTube
2. **OpenAI API Key**: Used to generate answers to your questions

You can set these keys in two ways:

1. **Environment Variables**:
   ```
   export YOUTUBE_API_KEY="your_youtube_api_key"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

2. **Settings Page**: Enter your API keys in the Settings page of the web interface

### Starting the System

Run the system using the provided run script:
```
python run.py
```

This will start both the backend server and the web interface. Once started, open your browser and navigate to:
```
http://localhost:8501
```

## Using the Web Interface

The web interface consists of three main pages:

1. **Dashboard**: Overview of system status and recently processed videos
2. **Ask**: Ask questions about video content
3. **Settings**: Configure the system and process YouTube channels

### Dashboard

The Dashboard provides an overview of:
- System status (number of videos and segments processed)
- Recently processed videos
- Current embedding model in use

### Processing YouTube Channels

Before you can ask questions, you need to process videos from a YouTube channel:

1. Navigate to the **Settings** page
2. Enter a YouTube Channel ID or URL in the "YouTube Channel ID or URL" field
   - Example Channel ID: `UCBJycsmduvYEL83R_U4JriQ`
   - Example Channel URL: `https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ`
3. Set the maximum number of videos to process using the slider
4. Click "Process Channel"
5. Wait for the processing to complete (this may take several minutes)

The system will:
1. Retrieve videos from the channel
2. Extract transcripts from each video
3. Segment the transcripts
4. Generate embeddings for each segment
5. Store the embeddings in a vector index for searching

### Asking Questions

Once you have processed videos from a channel:

1. Navigate to the **Ask** page
2. Enter your question in the text input field
3. Adjust the number of references using the slider (more references may provide more context)
4. Select the OpenAI model to use
5. Click "Ask"

The system will:
1. Convert your question to an embedding
2. Find the most relevant transcript segments
3. Generate an answer based on those segments
4. Display the answer with references to the source videos

### Example Questions

Here are some example questions you might ask (assuming you've processed videos from a business education channel):

- "What is the recommended valuation multiple for a business?"
- "How do I calculate EBITDA?"
- "What are the key factors in determining a business's value?"
- "What is the difference between strategic and financial buyers?"

### Viewing References

Each answer includes references to the source videos. For each reference, you'll see:

- The video title
- The timestamp where the information appears
- A snippet of the transcript
- A link to watch the video at that specific timestamp

Click on the link to watch the video at the exact moment where the information appears.

## Advanced Features

### Adjusting Search Parameters

You can adjust how many transcript segments are used to generate answers:

1. On the **Ask** page, use the "Number of references" slider
2. A higher number may provide more comprehensive answers but might include less relevant information
3. A lower number focuses on the most relevant segments but might miss some context

### Choosing Different Models

You can select different OpenAI models for answer generation:

1. On the **Ask** page, use the "OpenAI Model" dropdown
2. GPT-3.5-Turbo is faster and less expensive
3. GPT-4 may provide more accurate and nuanced answers but is more expensive

## Troubleshooting

### No Videos Found

If the system can't find videos for a channel:

1. Verify that the Channel ID or URL is correct
2. Check that your YouTube API key is valid and has the necessary permissions
3. Make sure the channel has public videos available

### No Transcript Available

Some videos may not have transcripts available. The system will skip these videos during processing.

### Answer Quality Issues

If you're not satisfied with the quality of answers:

1. Try increasing the number of references
2. Try using a more advanced model (e.g., GPT-4 instead of GPT-3.5-Turbo)
3. Process more videos from the channel to expand the knowledge base
4. Rephrase your question to be more specific

### API Key Issues

If you encounter API key errors:

1. Verify that your API keys are correct
2. Check that you have sufficient quota/credits for both YouTube and OpenAI APIs
3. For YouTube API, ensure you have enabled the YouTube Data API v3 in your Google Cloud Console
4. For OpenAI API, check your usage limits and billing status

## Tips for Best Results

1. **Be Specific**: Ask clear, specific questions rather than vague ones
2. **Process Multiple Channels**: For broader topics, process videos from multiple relevant channels
3. **Start with Recent Videos**: Process the most recent videos first, as they may contain more up-to-date information
4. **Use Channel Expertise**: Focus on channels that specialize in the topic you're interested in
5. **Check References**: Always review the source references to verify the information

## Privacy and Data Usage

The system processes and stores:
- Video metadata (title, description, etc.)
- Video transcripts
- Embeddings of transcript segments

It does not:
- Store user questions permanently
- Share data with third parties
- Use your data for training AI models

All processing happens locally on your machine or on your own servers if you've deployed the system elsewhere.
