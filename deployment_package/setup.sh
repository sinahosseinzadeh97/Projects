#!/bin/bash
# AI Research System Setup Script

# Exit on error
set -e

echo "=== AI Research System Setup Script ==="
echo "This script will set up the AI Research System."
echo

# Check if Python 3.11 is installed
if ! command -v python3.11 &> /dev/null; then
    echo "Python 3.11 is not installed. Please install it before continuing."
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install openai pydantic python-dotenv streamlit twilio

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env to add your API keys."
fi

# Create .streamlit directory and config if it doesn't exist
if [ ! -d .streamlit ]; then
    echo "Creating .streamlit directory and config..."
    mkdir -p .streamlit
    cat > .streamlit/config.toml << EOF
[server]
headless = true
address = "0.0.0.0"
port = 5000
EOF
fi

echo
echo "Setup complete! Next steps:"
echo "1. Edit .env to add your API keys"
echo "2. Run the application with 'streamlit run app.py'"
echo
echo "For system installation, refer to README.md for Docker, Nginx, and systemd instructions."