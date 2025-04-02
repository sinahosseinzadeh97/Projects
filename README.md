# AI Research System

A modular AI research system that extracts structured information about entities from the internet using LLM agents.

## System Overview

This system uses specialized AI agents to gather information about people, companies, and other entities. It processes this information through a pipeline of agents:

1. **Fact Extractor Agent**: Extracts basic factual information
2. **Media Fetcher Agent**: Finds images and other media
3. **Content Aggregator Agent**: Collects and organizes content
4. **Summarizer Agent**: Produces concise summaries

## Requirements

- Python 3.11 or higher
- OpenAI API key
- Twilio credentials (optional, for SMS notifications)

## Quick Setup

1. Clone this repository
2. Run the setup script:
   ```bash
   ./setup.sh
   ```
3. Edit the `.env` file to add your API keys
4. Run the application:
   ```bash
   source venv/bin/activate
   streamlit run app.py
   ```

## Deployment Options

### Option 1: Docker Deployment

Using Docker is the simplest way to deploy the system, as it packages all dependencies together.

#### Prerequisites
- Docker and Docker Compose installed on your server

#### Steps

1. Copy the project files to your server
2. Create a `.env` file with your API keys (use `.env.example` as a template)
3. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```
4. Your application will be available at `http://your-server-ip:5000`

#### Updating the application
```bash
git pull  # Pull latest changes
docker-compose down
docker-compose up -d --build
```

### Option 2: Nginx + Systemd Deployment

This approach is good for production environments where you want more control.

#### Prerequisites
- Ubuntu/Debian server
- Python 3.11
- Nginx
- Systemd

#### Steps

1. Copy the project files to your server (e.g., `/opt/ai-research-system/`)
2. Run the setup script:
   ```bash
   cd /opt/ai-research-system/
   ./setup.sh
   ```
3. Edit the `.env` file to add your API keys

4. Configure systemd service:
   ```bash
   # Edit the service file to set the correct paths and username
   nano ai-research.service
   
   # Copy the service file to systemd
   sudo cp ai-research.service /etc/systemd/system/
   
   # Start and enable the service
   sudo systemctl daemon-reload
   sudo systemctl enable ai-research
   sudo systemctl start ai-research
   ```

5. Configure Nginx:
   ```bash
   # Edit nginx.conf to set your domain name
   nano nginx.conf
   
   # Test the Nginx configuration
   sudo cp nginx.conf /etc/nginx/sites-available/ai-research
   sudo ln -s /etc/nginx/sites-available/ai-research /etc/nginx/sites-enabled/
   sudo nginx -t
   
   # If the test is successful, restart Nginx
   sudo systemctl restart nginx
   ```

6. Set up SSL with Let's Encrypt:
   ```bash
   sudo apt update
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

### Option 3: Simple Python Server (Development/Testing)

For simpler setups or development environments:

1. Setup the environment:
   ```bash
   ./setup.sh
   ```

2. Create a simple screen or tmux session to keep the server running:
   ```bash
   # Using screen
   screen -S ai-research
   source venv/bin/activate
   streamlit run app.py
   # Press Ctrl+A followed by D to detach
   
   # Or using tmux
   tmux new -s ai-research
   source venv/bin/activate
   streamlit run app.py
   # Press Ctrl+B followed by D to detach
   ```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| OPENAI_API_KEY | Your OpenAI API key | Yes |
| TWILIO_ACCOUNT_SID | Twilio Account SID | No |
| TWILIO_AUTH_TOKEN | Twilio Auth Token | No |
| TWILIO_PHONE_NUMBER | Twilio Phone Number | No |

## Maintenance and Monitoring

### Logs
- Docker: `docker-compose logs -f`
- Systemd: `sudo journalctl -u ai-research -f`
- Nginx: `/var/log/nginx/ai-research-error.log` and `/var/log/nginx/ai-research-access.log`

### Backup
Regularly backup your `.env` file and the cache directory if you want to preserve cached responses.

## Troubleshooting

### Common Issues

1. **Application not starting**
   - Check logs for errors
   - Verify API keys are correctly set in `.env`
   - Ensure the correct Python version is being used

2. **Nginx 502 Bad Gateway**
   - Verify the Streamlit server is running
   - Check Nginx configuration
   - Check firewall settings

3. **API Rate Limiting**
   - If you hit OpenAI API rate limits, consider implementing a rate limiter or upgrading your OpenAI plan

## Security Considerations

1. Never commit API keys to version control
2. Use HTTPS for production deployments
3. Consider adding authentication if the application is exposed to the internet
4. Regularly update dependencies to patch security vulnerabilities

## Support

For questions or issues, please refer to the project's documentation or reach out to the project maintainers.