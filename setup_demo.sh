#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Data Enrichment Tool Demo Environment...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install requirements
echo -e "${GREEN}Installing requirements...${NC}"
pip install -r requirements.txt

# Verify NLTK data
echo -e "${GREEN}Setting up NLTK data...${NC}"
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create sample .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${GREEN}Creating sample .env file...${NC}"
    cat > .env << EOL
# Add your API keys here for full functionality
# The app will work in demo mode without these keys
OPENAI_API_KEY=
HUGGINGFACE_API_KEY=
GOOGLE_API_KEY=
DATABASE_PATH=data/product_database.db
EOL
fi

# Create directory for database if it doesn't exist
mkdir -p data

# Copy sample data to data directory
echo -e "${GREEN}Setting up sample data...${NC}"
cp sample_data.csv data/

# Print success message
echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}Setup complete! Run the following to start:${NC}"
echo -e "${GREEN}./launch.sh${NC}"
echo -e "${YELLOW}==============================================${NC}"
echo -e "The application will work in demo mode without API keys."
echo -e "For full functionality, edit the .env file to add your API keys." 