#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Verify NLTK data
echo "Setting up NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create directory for database if it doesn't exist
mkdir -p data

# Open HTML file in browser
echo "Opening HTML interface in browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open index.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open index.html
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    start index.html
else
    echo "Couldn't automatically open index.html. Please open it manually."
fi

# Run Streamlit app
echo "Starting Streamlit application..."
streamlit run app.py 