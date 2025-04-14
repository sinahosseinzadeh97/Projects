# User Interface Design

This document outlines the design for the user interface of the YouTube Q&A system, including the web interface built with Streamlit.

## Overview

The user interface will provide a simple, intuitive way for users to:
1. Configure the system with a YouTube channel
2. Process videos and transcripts
3. Ask questions about the video content
4. View answers with references to source videos

## UI Components

### 1. Header Section

- System title and logo
- Navigation menu (Dashboard, Ask, Settings)
- System status indicator

### 2. Dashboard Page

```
┌─────────────────────────────────────────────────────────┐
│ YouTube Q&A System                          [Status: ✓] │
├─────────────────────────────────────────────────────────┤
│ [Dashboard] [Ask] [Settings]                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  System Statistics                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ 42          │ │ 5,230       │ │ 2.3s        │       │
│  │ Videos      │ │ Segments    │ │ Avg Response│       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
│                                                         │
│  Recent Videos                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Video Title 1                      [01/01/2023] │   │
│  │ Video Title 2                      [01/02/2023] │   │
│  │ Video Title 3                      [01/03/2023] │   │
│  │ ...                                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Recent Questions                                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ What is the recommended valuation multiple?     │   │
│  │ How to calculate customer acquisition cost?     │   │
│  │ ...                                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3. Ask Page

```
┌─────────────────────────────────────────────────────────┐
│ YouTube Q&A System                          [Status: ✓] │
├─────────────────────────────────────────────────────────┤
│ [Dashboard] [Ask] [Settings]                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Ask a Question                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ What is the recommended valuation multiple?     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Ask]                                                  │
│                                                         │
│  Answer                                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Based on the referenced content, the            │   │
│  │ recommended valuation multiple is around        │   │
│  │ 4-6x EBITDA.                                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  References                                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. "Business Valuation Explained" (02:15)       │   │
│  │    "The recommended valuation multiple is       │   │
│  │     typically 4-6x EBITDA for most businesses." │   │
│  │    [Watch Video]                                │   │
│  │                                                 │   │
│  │ 2. "Selling Your Business" (15:30)              │   │
│  │    "For service businesses, expect multiples    │   │
│  │     between 4-6 times EBITDA depending on..."   │   │
│  │    [Watch Video]                                │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4. Settings Page

```
┌─────────────────────────────────────────────────────────┐
│ YouTube Q&A System                          [Status: ✓] │
├─────────────────────────────────────────────────────────┤
│ [Dashboard] [Ask] [Settings]                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Channel Configuration                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │ YouTube Channel ID or URL:                      │   │
│  │ ┌─────────────────────────────────────────┐     │   │
│  │ │ UCWa_TFiwfgLPaHEHSGFwHtw               │     │   │
│  │ └─────────────────────────────────────────┘     │   │
│  │                                                 │   │
│  │ Max Videos to Process: [50]                     │   │
│  │                                                 │   │
│  │ [Process Channel]                               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Model Configuration                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Embedding Model:                                │   │
│  │ ( ) all-MiniLM-L6-v2                            │   │
│  │ (•) all-mpnet-base-v2                           │   │
│  │ ( ) multi-qa-mpnet-base-dot-v1                  │   │
│  │                                                 │   │
│  │ OpenAI Model:                                   │   │
│  │ (•) gpt-3.5-turbo                               │   │
│  │ ( ) gpt-4                                       │   │
│  │                                                 │   │
│  │ [Save Configuration]                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  API Keys                                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ YouTube API Key: ••••••••••••••••••••••••       │   │
│  │ [Update]                                        │   │
│  │                                                 │   │
│  │ OpenAI API Key: ••••••••••••••••••••••••        │   │
│  │ [Update]                                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## User Flows

### 1. Initial Setup Flow

1. User navigates to Settings page
2. User enters YouTube API key
3. User enters OpenAI API key
4. User enters YouTube channel ID or URL
5. User clicks "Process Channel"
6. System shows progress indicator while processing videos
7. System redirects to Dashboard when complete

### 2. Question Answering Flow

1. User navigates to Ask page
2. User enters question in text field
3. User clicks "Ask" button
4. System shows loading indicator
5. System displays answer with references
6. User can click on reference links to watch source videos at specific timestamps

### 3. System Management Flow

1. User navigates to Settings page
2. User can update configuration settings
3. User can trigger reprocessing of videos
4. User can update API keys

## Responsive Design

The UI will be responsive and adapt to different screen sizes:

### Desktop View
- Full layout as shown in the wireframes
- Side-by-side display of answer and references

### Tablet View
- Slightly compressed layout
- Stacked display of answer and references on smaller screens

### Mobile View
- Single column layout
- Collapsible sections for better navigation
- Simplified reference display

## Visual Design Elements

### Color Scheme
- Primary: #1E88E5 (Blue)
- Secondary: #FFC107 (Amber)
- Background: #F5F5F5 (Light Gray)
- Text: #212121 (Dark Gray)
- Accent: #FF5722 (Deep Orange)

### Typography
- Headings: Roboto, 24px/20px/16px (H1/H2/H3)
- Body: Roboto, 14px
- Monospace: Roboto Mono, 14px (for code or technical content)

### Components
- Cards with subtle shadows for content sections
- Rounded buttons with hover effects
- Progress indicators for long-running operations
- Toast notifications for system messages

## Accessibility Considerations

- High contrast text for readability
- Keyboard navigation support
- Screen reader compatible elements
- Proper ARIA labels for interactive elements
- Text alternatives for all non-text content

## Implementation with Streamlit

The UI will be implemented using Streamlit, which provides a simple way to create interactive web applications in Python.

### Key Streamlit Components

```python
# Page navigation
st.sidebar.title("YouTube Q&A System")
page = st.sidebar.radio("Navigation", ["Dashboard", "Ask", "Settings"])

# Dashboard components
if page == "Dashboard":
    st.title("Dashboard")
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Videos", "42")
    with col2:
        st.metric("Segments", "5,230")
    with col3:
        st.metric("Avg Response", "2.3s")
    
    # Recent videos
    st.subheader("Recent Videos")
    for video in recent_videos:
        st.write(f"{video['title']} [{video['published_at']}]")

# Ask page components
elif page == "Ask":
    st.title("Ask a Question")
    
    question = st.text_input("Enter your question:")
    if st.button("Ask"):
        with st.spinner("Generating answer..."):
            answer = generate_answer(question)
        
        st.subheader("Answer")
        st.write(answer["answer"])
        
        st.subheader("References")
        for ref in answer["references"]:
            st.write(f"**{ref['video_title']}** ({format_time(ref['start_time'])})")
            st.write(f"> {ref['text']}")
            st.markdown(f"[Watch Video](https://www.youtube.com/watch?v={ref['video_id']}&t={int(ref['start_time'])})")
```

## Future UI Enhancements

1. **Dark Mode**: Toggle between light and dark themes
2. **User Accounts**: Login and personalized history
3. **Saved Questions**: Ability to bookmark questions and answers
4. **Export Functionality**: Export answers as PDF or markdown
5. **Video Preview**: Embedded video player for references
6. **Voice Input**: Speech-to-text for question input
7. **Visualization**: Charts and graphs for analytics
