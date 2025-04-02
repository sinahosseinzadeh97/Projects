"""
Streamlit web application for the AI research system.
"""
import streamlit as st
import json
import time
from datetime import datetime

from core.agent_orchestrator import AgentOrchestrator
from utils.caching import cache_manager
from utils.validation import is_valid_person_name, is_valid_company_name
from config import DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL

# Page configuration
st.set_page_config(
    page_title="AI Research System",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for improved styling
st.markdown("""
<style>
    .main-title {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #1E88E5 !important;
        margin-bottom: 1rem !important;
        text-align: center;
    }
    .subtitle {
        font-size: 1.2rem !important;
        font-weight: 400 !important;
        color: #424242 !important;
        margin-bottom: 2rem !important;
        text-align: center;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        padding: 12px 15px;
        font-size: 16px;
        border: 2px solid #E0E0E0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTextInput > div > div > input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: white;
        border-radius: 10px;
        padding: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        gap: 1px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E3F2FD;
        color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for the orchestrator
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = AgentOrchestrator(
        llm_provider=DEFAULT_LLM_PROVIDER,
        llm_model=DEFAULT_LLM_MODEL
    )

if "results" not in st.session_state:
    st.session_state.results = None

if "loading" not in st.session_state:
    st.session_state.loading = False

if "entity_type" not in st.session_state:
    st.session_state.entity_type = "person"

# Custom CSS for sidebar
st.markdown("""
<style>
    .sidebar-title {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #1E88E5 !important;
        margin-bottom: 1rem !important;
    }
    .sidebar-section {
        background-color: #F5F5F5;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .sidebar-header {
        font-weight: 600;
        color: #424242;
        margin-bottom: 10px;
        border-bottom: 2px solid #1E88E5;
        padding-bottom: 5px;
    }
    .sidebar-text {
        font-size: 0.9rem;
        color: #616161;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<p class="sidebar-title">AI Research System</p>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text">A modular AI research system that extracts structured information about entities from the internet.</div>', unsafe_allow_html=True)
    
    # Entity type selection
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">Entity Type</div>', unsafe_allow_html=True)
    entity_type = st.radio("Select Type", ["Person", "Company"], index=0, label_visibility="collapsed")
    st.session_state.entity_type = entity_type.lower()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Cache management
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">Cache Management</div>', unsafe_allow_html=True)
    if st.button("Clear Cache"):
        cache_manager.clear()
        st.success("Cache cleared!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # About section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">About</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-text">
    This system uses AI agents to extract information about entities:
    <ul>
      <li><strong>Fact Extractor</strong>: Gets basic facts</li>
      <li><strong>Media Fetcher</strong>: Finds related media</li>
      <li><strong>Content Aggregator</strong>: Collects reviews and articles</li>
      <li><strong>Summarizer</strong>: Creates concise summaries</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-title">🔍 AI Entity Research</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Enter a name to discover comprehensive information about a person or company</p>', unsafe_allow_html=True)

# Input form
with st.form("research_form"):
    query = st.text_input("Enter a name to research:", placeholder="e.g., Brad Pitt or Apple Inc.")
    
    # Custom CSS for a beautiful button
    st.markdown("""
    <style>
        div.stButton > button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            border: none;
            padding: 12px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
            box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        }
        div.stButton > button:hover {
            background-color: #45a049;
            box-shadow: 0 12px 20px 0 rgba(0,0,0,0.24);
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        submit_button = st.form_submit_button("🔍 Research")
    with col2:
        if st.session_state.loading:
            st.info("Researching... This may take a minute.")

# Process the query when submitted
if submit_button and query:
    # Validate input
    if st.session_state.entity_type == "person" and not is_valid_person_name(query):
        st.error("Please enter a valid person name.")
    elif st.session_state.entity_type == "company" and not is_valid_company_name(query):
        st.error("Please enter a valid company name.")
    else:
        try:
            st.session_state.loading = True
            st.rerun()
        except:
            pass

# If we're in loading state, perform the research
if st.session_state.loading and query:
    try:
        # Process the query
        with st.spinner(f"Researching '{query}'..."):
            results = st.session_state.orchestrator.process_query(query)
            st.session_state.results = results
        
        # Reset loading state
        st.session_state.loading = False
        st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state.loading = False

# Display results if available
if st.session_state.results:
    results = st.session_state.results
    entity_type = results.get("entity_type", "entity")
    data = results.get("data", {})
    
    # Main entity information
    st.header(data.get("name", "Results"))
    
    # Show processing info
    st.write(f"Processing time: {results.get('processing_time_seconds', 0):.2f} seconds")
    st.write(f"Query timestamp: {results.get('query_timestamp', datetime.now().isoformat())}")
    
    # Create tabs for different information categories
    tabs = st.tabs(["Summary", "Facts", "Media", "Content", "Raw Data"])
    
    # Summary tab
    with tabs[0]:
        st.subheader("Summary")
        
        # Display summary if available
        if "summary" in data:
            summary_data = data["summary"]
            if isinstance(summary_data, dict) and "value" in summary_data:
                st.write(summary_data["value"])
                
                # Show confidence and sources
                if "confidence" in summary_data:
                    st.progress(float(summary_data["confidence"]), text=f"Confidence: {summary_data['confidence']:.2f}")
                
                if "sources" in summary_data and summary_data["sources"]:
                    st.write("Sources:")
                    for source in summary_data["sources"]:
                        if isinstance(source, dict):
                            if "url" in source and source["url"]:
                                st.write(f"- [{source.get('name', 'Source')}]({source['url']})")
                            else:
                                st.write(f"- {source.get('name', 'Source')}")
        else:
            st.write("No summary available.")
    
    # Facts tab
    with tabs[1]:
        st.subheader("Facts")
        
        # Create columns for facts
        col1, col2 = st.columns(2)
        
        fact_keys = []
        
        # Person-specific facts
        if entity_type == "person":
            fact_keys = [
                ("date_of_birth", "Date of Birth"),
                ("place_of_birth", "Place of Birth"),
                ("profession", "Profession"),
                ("biography", "Biography"),
                ("achievements", "Achievements"),
                ("related_works", "Related Works")
            ]
        # Company-specific facts
        elif entity_type == "company":
            fact_keys = [
                ("founded", "Founded"),
                ("headquarters", "Headquarters"),
                ("industry", "Industry"),
                ("products_services", "Products/Services"),
                ("key_people", "Key People"),
                ("description", "Description")
            ]
        
        # Display facts in columns
        for i, (key, label) in enumerate(fact_keys):
            col = col1 if i % 2 == 0 else col2
            
            with col:
                if key in data:
                    fact_data = data[key]
                    st.write(f"**{label}:**")
                    
                    if isinstance(fact_data, dict):
                        # Display fact value
                        value = fact_data.get("value")
                        if isinstance(value, list):
                            for item in value:
                                st.write(f"- {item}")
                        else:
                            st.write(value)
                        
                        # Show confidence
                        if "confidence" in fact_data:
                            confidence = float(fact_data["confidence"])
                            st.progress(confidence, text=f"Confidence: {confidence:.2f}")
        
        # Additional info section for any other facts
        if "additional_info" in data and data["additional_info"]:
            st.subheader("Additional Information")
            for key, value in data["additional_info"].items():
                if isinstance(value, dict) and "value" in value:
                    st.write(f"**{key.replace('_', ' ').title()}:** {value['value']}")
    
    # Media tab
    with tabs[2]:
        st.subheader("Related Media")
        
        if "related_images" in data:
            st.write("**Images:**")
            image_data = data["related_images"]
            
            if isinstance(image_data, dict) and "value" in image_data:
                images = image_data["value"]
                if isinstance(images, list):
                    # Display image descriptions
                    for image in images:
                        if isinstance(image, dict) and "description" in image:
                            st.write(f"- {image['description']}")
                            if "likely_source" in image:
                                st.write(f"  Source: {image['likely_source']}")
                            st.write("")
            else:
                st.write("No image information available.")
        else:
            st.write("No media information available.")
    
    # Content tab
    with tabs[3]:
        st.subheader("Related Content")
        
        # Look for reviews or opinions
        if "opinions_reviews" in data:
            st.write("**Opinions & Reviews:**")
            content_data = data["opinions_reviews"]
            
            if isinstance(content_data, dict) and "value" in content_data:
                content_items = content_data["value"]
                if isinstance(content_items, list):
                    for item in content_items:
                        if isinstance(item, dict):
                            with st.expander(item.get("content_type", "Content") + ": " + item.get("summary", "")[:50] + "..."):
                                st.write(item.get("summary", ""))
                                st.write(f"Source: {item.get('source', 'Unknown')}")
                                
                                # Display sentiment if available
                                sentiment = item.get("sentiment", "").lower()
                                if sentiment == "positive":
                                    st.success(f"Sentiment: {sentiment}")
                                elif sentiment == "negative":
                                    st.error(f"Sentiment: {sentiment}")
                                else:
                                    st.info(f"Sentiment: {sentiment}")
            else:
                st.write("No content information available.")
        else:
            st.write("No content information available.")
    
    # Raw Data tab
    with tabs[4]:
        st.subheader("Raw JSON Data")
        st.json(results)

# Footer
st.markdown("---")
st.caption("AI Research System | Powered by LLM Agents")
