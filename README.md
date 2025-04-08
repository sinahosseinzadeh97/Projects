# Advanced Product Data Enrichment Tool

![Data Enrichment](https://img.shields.io/badge/Data-Enrichment-4361ee) ![AI Powered](https://img.shields.io/badge/AI-Powered-7209b7) ![NLP](https://img.shields.io/badge/NLP-Enabled-3a0ca3)

A powerful data processing tool that enhances product research workflows with AI-powered enrichment capabilities. This tool integrates multiple AI services (OpenAI, Hugging Face, Google) to extract meaningful insights from product data.

![Demo Animation](https://github.com/sinahosseinzadeh97/Projects/raw/main/DATAENRICHMENTTOOL/demo.gif)

## 🚀 Features

- **NLP-Powered Keyword Extraction**: Extract meaningful keywords from product descriptions using advanced NLP techniques
- **Advanced Data Filtering**: Filter records based on sophisticated classification rules and AI-generated metadata
- **Reverse Lookup Tool**: Trace products to upstream data sources using identifiers (ASIN, SKU, UPC)
- **Enriched CSV Exports**: Generate search-friendly metadata for analysis
- **Structured Data Processing**: Support for CSV, JSON, and XML formats
- **Intuitive UI**: Browse, search, upload, and export through a Streamlit dashboard

## 🧪 Try It Now!

Want to see this tool in action? Follow these simple steps:

1. Clone this repository:
   ```bash
   git clone https://github.com/sinahosseinzadeh97/Projects.git
   cd Projects/DATAENRICHMENTTOOL
   ```

2. Run the launch script:
   ```bash
   chmod +x launch.sh
   ./launch.sh
   ```

3. Explore the interface and see the power of AI-driven data enrichment!

## 🔧 Installation & Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys in the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_key_here
   HUGGINGFACE_API_KEY=your_huggingface_key_here
   GOOGLE_API_KEY=your_google_key_here
   ```

4. Ensure NLTK data is available:
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

## 📊 Usage Guide

1. **Data Upload**: Upload CSV or JSON files containing product data
2. **Browse & Search**: Explore your product data through the interactive UI
3. **Basic Enrichment**: Extract keywords and analyze product descriptions
4. **AI Enrichment**: Apply advanced AI models to your data
5. **Reverse Lookup**: Trace products to upstream data sources
6. **Export**: Download enriched data and metadata

## 🧠 AI Capabilities

The tool integrates with three major AI service providers:

- **OpenAI**: Advanced keyword extraction, product classification, description generation
- **Hugging Face**: Sentiment analysis, named entity recognition, language detection
- **Google API**: Image analysis, entity extraction, product information search

## 📁 Project Structure

```
.
├── app.py                  # Main Streamlit application
├── config.py               # Configuration and settings
├── data_processor.py       # Core data processing logic
├── data_filter.py          # Data filtering utilities
├── reverse_lookup.py       # Reverse lookup functionality
├── openai_processor.py     # OpenAI API integration
├── huggingface_processor.py # Hugging Face API integration
├── google_processor.py     # Google API integration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API keys)
├── data/                   # Data storage directory
├── src/                    # Source code modules
└── index.html              # Landing page
```

## 🔑 API Integration

To use the AI features, you'll need to obtain API keys from:

1. [OpenAI](https://platform.openai.com/)
2. [Hugging Face](https://huggingface.co/settings/tokens)
3. [Google Cloud](https://console.cloud.google.com/)

Add these keys to your `.env` file or configure them through the application settings.

## 💻 Hire Me!

Looking for a skilled developer to build intelligent data solutions for your business? I'm available for:

- **Full-stack development** with expertise in React, Python, and Node.js
- **AI application development** with integration to leading AI services
- **Data processing pipelines** that transform raw data into actionable insights
- **Custom software solutions** tailored to your specific business needs

📧 **Contact:** [sinahosseinzadeh97@gmail.com](mailto:sinahosseinzadeh97@gmail.com)
🔗 **LinkedIn:** [sinahosseinzadeh](https://www.linkedin.com/in/sinahosseinzadeh/)
🌐 **Portfolio:** [sinahosseinzadeh.com](https://sinahosseinzadeh.com)

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.
