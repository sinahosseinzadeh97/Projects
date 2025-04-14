# Reddit Automation Tool

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Developer:** SinaMohammadHosseinZadeh

## Overview

A sophisticated Python-based Reddit automation tool designed to intelligently monitor and interact with targeted subreddits in the health, wellness, and alternative medicine niches. The system uses advanced natural language processing to identify relevant posts, analyze their content, and generate authentic, human-like responses based on customizable templates and A/B testing strategies.

This tool enables businesses and content creators to effectively engage with their target audience on Reddit while maintaining authenticity and providing genuine value to the community.

### Key Features

- **Intelligent Post Analysis:** Analyzes posts for relevance using keyword matching and semantic relevance scoring
- **Human-like Response Generation:** Creates authentic, conversational responses based on post content and context
- **Multi-subreddit Monitoring:** Simultaneously tracks posts from multiple health and wellness subreddits
- **Advanced A/B Testing:** Compare different response templates and strategies to optimize engagement
- **Comprehensive Analytics Dashboard:** Web interface for monitoring performance with interactive charts and metrics
- **Automated Scheduling:** Time-based posting schedules with randomization to appear more natural
- **Rate Limiting & Safety Measures:** Implements safeguards to ensure responsible platform usage
- **Containerized Deployment:** Easy deployment with Docker and Docker Compose
- **Test Mode:** Fully functional test/demo mode that runs without requiring Reddit API credentials

## Target Niches

The tool is specifically optimized for three key niches:

1. **Health** - General health topics, medical information, and health-related advice
2. **Wellness** - Holistic wellness, mindfulness, mental health, and self-improvement
3. **Alternative Medicine** - Natural remedies, herbal supplements, and non-traditional health approaches

## Technical Architecture

The system follows a modular architecture with clean separation of concerns:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Subreddit      │────▶│  Post           │────▶│  Response       │
│  Monitor        │     │  Analyzer       │     │  Generator      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                              │
         │                                              │
         ▼                                              ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Reddit Bot     │◀───▶│  Scheduler      │     │  Logger         │
│  Coordinator    │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                              ▲
         │                                              │
         ▼                                              │
┌─────────────────────────────────────────────────────────────────┐
│                        Web Dashboard                             │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

- **main.py**: Entry point that initializes and coordinates all components
- **reddit_bot.py**: Core bot class that orchestrates the overall workflow
- **subreddit_monitor.py**: Monitors target subreddits for new posts matching criteria
- **post_analyzer.py**: Analyzes posts for relevance and topic matching with scoring
- **response_generator.py**: Generates human-like responses with A/B testing variants
- **dashboard.py**: Flask-based web interface for monitoring and analytics
- **scheduler.py**: Manages timing of bot actions for natural behavior
- **logger.py**: Comprehensive activity tracking and statistics generation
- **test_mode.py**: Simulation environment for testing without API credentials

## Installation

### Prerequisites

- Python 3.9 or higher
- Reddit API credentials (for production use)
- Optional: Docker and Docker Compose (for containerized deployment)
- Optional: PostgreSQL (for database storage)

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SinaMohammadHosseinZadeh/reddit-automation-tool.git
   cd reddit-automation-tool
   ```

2. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and add your Reddit API credentials:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USERNAME=your_reddit_username
   REDDIT_PASSWORD=your_reddit_password
   REDDIT_USER_AGENT=reddit_bot_v1.0.0
   ```

4. **Generate a secret key for Flask:**
   ```bash
   python generate_secret.py
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

6. **Docker deployment (optional):**
   ```bash
   docker-compose up --build
   ```

## Dashboard & Analytics

The web dashboard is accessible at `http://localhost:5000` and provides:

- **Real-time Performance Metrics:** Success rates, response counts, and relevance scores
- **Interactive Charts:** Visualize daily activity and subreddit performance
- **A/B Testing Results:** Compare effectiveness of different response templates
- **Recent Activity Logs:** View recent responses and their statuses
- **Health Monitoring:** System status and error reporting

![Dashboard Screenshot](https://example.com/dashboard_screenshot.png)

## Configuration Options

Configure the bot's behavior through environment variables or the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `REDDIT_CLIENT_ID` | Reddit API Client ID | (Required) |
| `REDDIT_CLIENT_SECRET` | Reddit API Client Secret | (Required) |
| `REDDIT_USERNAME` | Reddit username | (Required) |
| `REDDIT_PASSWORD` | Reddit password | (Required) |
| `SUBREDDITS` | Comma-separated list of subreddits | health,wellness,alternativemedicine,nutrition,supplements,holistic,naturalremedies |
| `MAX_DAILY_RESPONSES` | Maximum responses per day | 20 |
| `MAX_SUBREDDIT_RESPONSES` | Maximum per subreddit per day | 5 |
| `SCAN_INTERVAL_MINUTES` | Minutes between subreddit scans | 15 |
| `RESPONSE_DELAY_MINUTES` | Random delay before posting | 2 |
| `MIN_POST_SCORE` | Minimum score for post consideration | 1 |
| `ENABLE_DASHBOARD` | Enable web dashboard | True |
| `DASHBOARD_PORT` | Port for web dashboard | 5000 |

## Response Templates System

The bot uses a sophisticated template system for generating authentic responses:

```
Template Directory Structure:
templates/
├── health_responses.json
├── wellness_responses.json
└── alternative_medicine_responses.json
```

Each template includes both A and B variants for testing different approaches:

```json
{
  "template_id": "health_1",
  "variants": {
    "A": "Hi, I noticed your post about {title}. Taking care of your health is so important. {body} Hope this helps!",
    "B": "Hey there, Your health concerns about {title} really resonated with me. {body} Wishing you wellness on your journey!"
  },
  "keywords": ["health", "medical", "doctor"],
  "relevance_boost": 1.2
}
```

Templates support dynamic variables and can be customized for different tones and approaches.

## Test Mode

The system includes a fully functional test mode that simulates Reddit posts and responses:

```bash
# Run the application in test mode (no Reddit API credentials needed)
python main.py
```

Test mode will:
1. Generate sample posts across different subreddits
2. Analyze posts for relevance and keyword matching
3. Generate appropriate responses using templates
4. Log activities and generate analytics data
5. Populate the dashboard with sample performance data

This provides a complete demonstration of the tool's capabilities without requiring Reddit API access.

## Production Deployment Guide

For deploying to another server, follow these steps:

### Prerequisites

Make sure your server has:
- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Git
- Python 3.9+ (only if running without Docker)
- 2GB RAM minimum (4GB recommended)
- 10GB free disk space
- Port 5000 accessible (or configure a different port)

1. **Transfer the files to your server**:
   ```bash
   # Option 1: Clone directly on the server
   git clone https://github.com/SinaMohammadHosseinZadeh/reddit-automation-tool.git
   cd reddit-automation-tool

   # Option 2: Use SCP to transfer files from local machine
   scp -r /path/to/local/reddit-automation-tool user@your-server:/path/on/server
   ```

2. **Configure environment variables**:
   ```bash
   # Create and edit the .env file
   cp .env.example .env
   nano .env
   ```
   
   Update the following in your `.env` file:
   - Set your Reddit API credentials
   - Change database passwords to strong, unique values
   - Set `FLASK_ENV=production` and `DEBUG=False`
   - Configure subreddits and response limits

3. **Run the deployment script**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

   The script will:
   - Verify all prerequisites are installed
   - Check for required environment variables
   - Build and start Docker containers
   - Initialize the database
   - Verify the application is running

4. **Security Recommendations**:
   - Use a reverse proxy like Nginx in front of the application
   - Enable HTTPS with a valid SSL certificate
   - Set up proper firewalls allowing only necessary ports
   - Change default database passwords
   - Run regular security updates

5. **Verify Deployment**:
   - Dashboard should be available at http://your-server-ip:5000
   - Check logs with `docker-compose logs -f`
   - Test API health endpoint at http://your-server-ip:5000/api/health

6. **Manual Deployment Without Script**:
   If you prefer to deploy manually:
   ```bash
   # Make sure the .env file is properly configured
   docker-compose up --build -d
   
   # Check logs to ensure everything started correctly
   docker-compose logs -f
   ```

## Security Considerations

- Reddit API credentials are stored securely in environment variables
- The Flask session secret is generated using cryptographically secure methods
- All sensitive information is excluded from version control
- The system implements rate limiting to comply with Reddit's API terms of service
- Logging excludes sensitive user information

## Troubleshooting

Common issues and solutions:

### API and Authentication Issues
- **"invalid_grant" error**: Ensure your Reddit credentials are correct and have necessary permissions
- **API connection failures**: Check your network settings and ensure your server can connect to Reddit's API
- **Authentication errors**: Verify that your Reddit account has the necessary permissions and is not rate-limited

### Dashboard and Frontend Issues
- **Missing data in dashboard**: Run application in test mode to generate sample data
- **CORS errors in browser console**: Check that the API endpoints match what the frontend is calling
- **Dashboard not loading**: Verify that port 5000 is open and accessible

### Container and Deployment Issues
- **Docker container fails to start**: Check logs with `docker-compose logs` to diagnose specific errors
- **Database connection failures**: Ensure PostgreSQL is running and credentials are correct
- **Permission issues**: Verify file permissions on log directories and config files
- **Rate limiting issues**: Adjust the timing settings in your configuration

### Server Deployment Specific Issues
- **Port conflicts**: If port 5000 is already in use, change the port mapping in docker-compose.yml
- **Memory issues**: If the application crashes, increase available memory or reduce worker count
- **Database persistence**: Ensure your volume mount points are properly configured for data persistence
- **Firewall blockages**: Configure your server firewall to allow necessary traffic

## Developer

Developed by **SinaMohammadHosseinZadeh**

For questions, support, or custom development inquiries, please contact:
- GitHub: [SinaMohammadHosseinZadeh](https://github.com/SinaMohammadHosseinZadeh)
- Email: your.email@example.com

## License

This project is licensed under the MIT License - see the LICENSE file for details.