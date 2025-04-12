"""
Enhanced Streamlit UI with API integrations for the data processing tool.

This module provides a web-based user interface with advanced AI features
powered by OpenAI, Hugging Face, and Google APIs.
"""

import os
import sys
import json
import pandas as pd
import streamlit as st
from io import StringIO
import tempfile
from PIL import Image

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data.data_processor import load_data, enrich_product_data, export_to_csv, generate_metadata
from src.data.data_filter import apply_filters
from src.models.reverse_lookup import ReverseLookupTool
from src.config import config
from src.models.openai_processor import OpenAIProcessor
from src.models.huggingface_processor import HuggingFaceProcessor
from src.models.google_processor import GoogleAPIProcessor

# Set page configuration
st.set_page_config(
    page_title="Enhanced Product Data Enrichment Tool",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'products' not in st.session_state:
    st.session_state.products = []
if 'enriched_products' not in st.session_state:
    st.session_state.enriched_products = []
if 'filtered_products' not in st.session_state:
    st.session_state.filtered_products = []
if 'metadata' not in st.session_state:
    st.session_state.metadata = []
if 'lookup_tool' not in st.session_state:
    st.session_state.lookup_tool = None
if 'api_processors' not in st.session_state:
    st.session_state.api_processors = {
        'openai': None,
        'huggingface': None,
        'google': None
    }
if 'api_status' not in st.session_state:
    st.session_state.api_status = {
        'openai': False,
        'huggingface': False,
        'google': False
    }

def initialize_lookup_tool():
    """Initialize the reverse lookup tool with thread-safe connections."""
    if st.session_state.lookup_tool is None:
        try:
            st.session_state.lookup_tool = ReverseLookupTool()
            st.session_state.lookup_tool.initialize_database()
            return True
        except Exception as e:
            st.error(f"Error initializing reverse lookup tool: {e}")
            return False
    return True

def initialize_api_processors():
    """Initialize API processors if API keys are available."""
    # Check for OpenAI API key
    if config.get('openai', 'api_key') and not st.session_state.api_processors['openai']:
        try:
            st.session_state.api_processors['openai'] = OpenAIProcessor()
            st.session_state.api_status['openai'] = True
        except Exception as e:
            st.error(f"Error initializing OpenAI processor: {e}")
            st.session_state.api_status['openai'] = False
    
    # Check for Hugging Face API key
    if config.get('huggingface', 'api_key') and not st.session_state.api_processors['huggingface']:
        try:
            st.session_state.api_processors['huggingface'] = HuggingFaceProcessor()
            st.session_state.api_status['huggingface'] = True
        except Exception as e:
            st.error(f"Error initializing Hugging Face processor: {e}")
            st.session_state.api_status['huggingface'] = False
    
    # Check for Google API key
    if config.get('google', 'api_key') and not st.session_state.api_processors['google']:
        try:
            st.session_state.api_processors['google'] = GoogleAPIProcessor()
            st.session_state.api_status['google'] = True
        except Exception as e:
            st.error(f"Error initializing Google API processor: {e}")
            st.session_state.api_status['google'] = False

def main():
    """
    Main function for the Streamlit UI.
    """
    # Initialize tools and processors
    initialize_lookup_tool()
    initialize_api_processors()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = [
        "Home", 
        "Data Upload", 
        "Browse & Search", 
        "Basic Enrichment", 
        "AI Enrichment",
        "Reverse Lookup", 
        "Export"
    ]
    page = st.sidebar.radio("Go to", pages)
    
    # API Status indicators in sidebar
    st.sidebar.title("API Status")
    
    col1, col2, col3 = st.sidebar.columns(3)
    
    with col1:
        if st.session_state.api_status['openai']:
            st.success("OpenAI: ✅")
        else:
            st.error("OpenAI: ❌")
    
    with col2:
        if st.session_state.api_status['huggingface']:
            st.success("HF: ✅")
        else:
            st.error("HF: ❌")
    
    with col3:
        if st.session_state.api_status['google']:
            st.success("Google: ✅")
        else:
            st.error("Google: ❌")
    
    # Display selected page
    if page == "Home":
        display_home_page()
    elif page == "Data Upload":
        display_upload_page()
    elif page == "Browse & Search":
        display_browse_page()
    elif page == "Basic Enrichment":
        display_basic_enrichment_page()
    elif page == "AI Enrichment":
        display_ai_enrichment_page()
    elif page == "Reverse Lookup":
        display_lookup_page()
    elif page == "Export":
        display_export_page()

def display_home_page():
    """
    Display the home page.
    """
    st.title("Enhanced Product Data Enrichment Tool")
    
    st.markdown("""
    Welcome to the Enhanced Product Data Enrichment Tool! This application helps you process and enrich 
    structured product data for research workflows using advanced AI capabilities.
    
    ### Features
    
    - **Data Upload**: Upload CSV or JSON files containing product data
    - **Browse & Search**: Browse and search through your product data
    - **Basic Enrichment**: Enrich your data with NLP-powered keyword extraction
    - **AI Enrichment**: Use advanced AI models from OpenAI, Hugging Face, and Google
    - **Reverse Lookup**: Look up products by their identifiers and trace to upstream data
    - **Export**: Export enriched data and metadata to CSV files
    
    ### Getting Started
    
    1. Navigate to the **Data Upload** page to upload your product data
    2. Use the **Browse & Search** page to explore your data
    3. Go to the **Basic Enrichment** page to extract keywords and enrich your data
    4. Use the **AI Enrichment** page to apply advanced AI models to your data
    5. Use the **Reverse Lookup** page to trace products to their upstream data
    6. Export your enriched data from the **Export** page
    """)
    
    # Display current data stats
    st.subheader("Current Data Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Raw Products", len(st.session_state.products))
    
    with col2:
        st.metric("Enriched Products", len(st.session_state.enriched_products))
    
    with col3:
        st.metric("Filtered Products", len(st.session_state.filtered_products))
    
    with col4:
        # Count products with AI enrichment
        ai_enriched_count = sum(
            1 for p in st.session_state.enriched_products 
            if any(k.startswith(('ai_', 'hf_', 'google_')) for k in p.keys())
        )
        st.metric("AI-Enriched Products", ai_enriched_count)
    
    # Display API status
    st.subheader("AI Services Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.api_status['openai']:
            st.success("OpenAI API: Connected")
            st.markdown("**Capabilities:**")
            st.markdown("- Advanced keyword extraction")
            st.markdown("- Product classification")
            st.markdown("- Description generation")
            st.markdown("- Sentiment analysis")
        else:
            st.error("OpenAI API: Not connected")
            st.markdown("Configure OpenAI API key to enable advanced NLP features.")
    
    with col2:
        if st.session_state.api_status['huggingface']:
            st.success("Hugging Face API: Connected")
            st.markdown("**Capabilities:**")
            st.markdown("- Sentiment analysis")
            st.markdown("- Entity extraction")
            st.markdown("- Language detection")
            st.markdown("- Multi-language support")
        else:
            st.error("Hugging Face API: Not connected")
            st.markdown("Configure Hugging Face API key to enable specialized NLP models.")
    
    with col3:
        if st.session_state.api_status['google']:
            st.success("Google API: Connected")
            st.markdown("**Capabilities:**")
            st.markdown("- Image analysis")
            st.markdown("- Entity extraction")
            st.markdown("- Sentiment analysis")
            st.markdown("- Product information search")
        else:
            st.error("Google API: Not connected")
            st.markdown("Configure Google API key to enable image analysis and search features.")

def display_upload_page():
    """
    Display the data upload page.
    """
    st.title("Data Upload")
    
    st.markdown("""
    Upload your product data files (CSV or JSON) or generate sample data for testing.
    """)
    
    # File upload section
    st.subheader("Upload Files")
    
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "json"])
    
    if uploaded_file is not None:
        try:
            # Determine file type from extension
            file_type = uploaded_file.name.split(".")[-1].lower()
            
            # Load data based on file type
            if file_type == "csv":
                df = pd.read_csv(uploaded_file)
                st.session_state.products = df.to_dict('records')
            elif file_type == "json":
                content = uploaded_file.getvalue().decode("utf-8")
                data = json.loads(content)
                if isinstance(data, list):
                    st.session_state.products = data
                else:
                    st.session_state.products = [data]
            
            st.success(f"Successfully loaded {len(st.session_state.products)} products from {uploaded_file.name}")
            
            # Display preview
            st.subheader("Data Preview")
            if st.session_state.products:
                df_preview = pd.DataFrame(st.session_state.products).head(5)
                st.dataframe(df_preview)
            
            # Import to database if reverse lookup tool is initialized
            if st.session_state.lookup_tool:
                if st.button("Import to Database"):
                    try:
                        # Save to temporary CSV file
                        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
                            temp_path = temp_file.name
                            pd.DataFrame(st.session_state.products).to_csv(temp_path, index=False)
                        
                        # Import to database
                        product_count, source_count = st.session_state.lookup_tool.import_from_csv(temp_path)
                        
                        # Clean up temporary file
                        os.unlink(temp_path)
                        
                        st.success(f"Imported {product_count} products and {source_count} source records to database")
                    except Exception as e:
                        st.error(f"Error importing to database: {e}")
        
        except Exception as e:
            st.error(f"Error loading file: {e}")
    
    # Generate sample data section
    st.subheader("Generate Sample Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_products = st.number_input("Number of products", min_value=1, max_value=1000, value=10)
    
    with col2:
        categories = st.multiselect(
            "Product categories",
            ["Electronics", "Home Appliances", "Clothing", "Books", "Toys"],
            ["Electronics", "Home Appliances"]
        )
    
    if st.button("Generate Sample Data"):
        try:
            # Generate sample data
            sample_products = []
            
            for i in range(num_products):
                category = categories[i % len(categories)]
                
                if category == "Electronics":
                    product = {
                        "id": f"PROD-E{i+1:03d}",
                        "asin": f"B0{i+1:06d}",
                        "sku": f"SKU-E{i+1:05d}",
                        "upc": f"1234567{i+1:05d}",
                        "title": f"Premium Wireless Headphones Model X{i+1}",
                        "description": "High-quality wireless headphones with noise cancellation technology. Features Bluetooth 5.0, 30-hour battery life, and comfortable over-ear design. Perfect for music lovers and professionals who need clear sound.",
                        "features": "Noise cancellation, Bluetooth 5.0, 30-hour battery life, Comfortable design, Fast charging",
                        "category": "Electronics",
                        "price": 99.99 + (i * 10)
                    }
                elif category == "Home Appliances":
                    product = {
                        "id": f"PROD-H{i+1:03d}",
                        "asin": f"B1{i+1:06d}",
                        "sku": f"SKU-H{i+1:05d}",
                        "upc": f"7654321{i+1:05d}",
                        "title": f"Smart Coffee Maker Pro {i+1}",
                        "description": "Programmable smart coffee maker with Wi-Fi connectivity. Control brewing from your smartphone, set schedules, and enjoy perfect coffee every time. Features 12-cup capacity and built-in grinder.",
                        "features": "Wi-Fi connectivity, Smartphone control, 12-cup capacity, Built-in grinder, Programmable timer",
                        "category": "Home Appliances",
                        "price": 149.99 + (i * 5)
                    }
                elif category == "Clothing":
                    product = {
                        "id": f"PROD-C{i+1:03d}",
                        "asin": f"B2{i+1:06d}",
                        "sku": f"SKU-C{i+1:05d}",
                        "upc": f"9876543{i+1:05d}",
                        "title": f"Premium Cotton T-Shirt {i+1}",
                        "description": "Soft and comfortable 100% organic cotton t-shirt. Available in multiple colors and sizes. Perfect for everyday wear with durable construction and stylish design.",
                        "features": "100% organic cotton, Multiple colors, Sizes S-XXL, Machine washable, Durable construction",
                        "category": "Clothing",
                        "price": 24.99 + (i * 2)
                    }
                elif category == "Books":
                    product = {
                        "id": f"PROD-B{i+1:03d}",
                        "asin": f"B3{i+1:06d}",
                        "sku": f"SKU-B{i+1:05d}",
                        "upc": f"5678901{i+1:05d}",
                        "title": f"The Art of Data Science: Volume {i+1}",
                        "description": "Comprehensive guide to modern data science techniques and applications. Covers machine learning, statistical analysis, and data visualization with practical examples and case studies.",
                        "features": "500 pages, Hardcover, Includes code examples, Written by experts, Published 2025",
                        "category": "Books",
                        "price": 39.99 + (i * 3)
                    }
                else:  # Toys
                    product = {
                        "id": f"PROD-T{i+1:03d}",
                        "asin": f"B4{i+1:06d}",
                        "sku": f"SKU-T{i+1:05d}",
                        "upc": f"1357924{i+1:05d}",
                        "title": f"Educational Building Blocks Set {i+1}",
                        "description": "Creative building blocks set for children ages 3-10. Develops cognitive skills and creativity through play. Includes various shapes and colors for endless building possibilities.",
                        "features": "100 pieces, Multiple colors, Various shapes, Educational, Safe for children 3+",
                        "category": "Toys",
                        "price": 29.99 + (i * 4)
                    }
                
                sample_products.append(product)
            
            st.session_state.products = sample_products
            
            st.success(f"Generated {len(sample_products)} sample products")
            
            # Display preview
            st.subheader("Data Preview")
            df_preview = pd.DataFrame(sample_products).head(5)
            st.dataframe(df_preview)
            
        except Exception as e:
            st.error(f"Error generating sample data: {e}")

if __name__ == "__main__":
    main()