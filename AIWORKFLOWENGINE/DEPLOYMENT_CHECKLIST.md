# Deployment Checklist

Use this checklist to ensure a successful deployment of the AI Research System.

## Pre-Deployment

- [ ] Verify all required Python packages are in `pyproject.toml`
- [ ] Ensure the `.streamlit/config.toml` file is correctly configured
- [ ] Test the application locally to confirm it works as expected
- [ ] Check that `.env.example` includes all required environment variables
- [ ] Prepare your API keys (OpenAI, Twilio if needed)

## Deployment Files Checklist

Confirm that you have the following files prepared for deployment:

### Common Files
- [ ] `.env` file with your API keys (create from `.env.example`)
- [ ] `.streamlit/config.toml` with server configuration

### Docker Deployment
- [ ] `Dockerfile`
- [ ] `docker-compose.yml`
- [ ] Run Docker tests locally if possible

### Nginx + Systemd Deployment
- [ ] `nginx.conf` updated with your domain name
- [ ] `ai-research.service` updated with correct paths and username
- [ ] SSL certificates or Let's Encrypt setup ready

## Server Deployment Steps

### 1. Server Preparation
- [ ] Update server OS and install security updates
- [ ] Install required tools (Python, Docker, or Nginx depending on method)
- [ ] Configure firewall to allow port 80/443 (and 5000 if direct access needed)

### 2. Application Installation
- [ ] Transfer application files to server
- [ ] Run setup script (`./setup.sh`)
- [ ] Configure environment variables

### 3. Start Services
- [ ] Start application service (Docker or systemd)
- [ ] Configure and start Nginx if using
- [ ] Set up SSL certificates

### 4. Testing
- [ ] Verify application is accessible through expected URL/port
- [ ] Test basic functionality (search for an entity)
- [ ] Check logs for any unexpected errors

### 5. Post-Deployment
- [ ] Set up monitoring (optional)
- [ ] Configure backups for important data
- [ ] Document deployment configuration
- [ ] Set up automated updates/maintenance schedule

## Common Problems and Solutions

### Application Not Starting
- Check application logs
- Verify API keys are correct
- Ensure all dependencies are installed
- Check port availability

### Nginx Configuration Issues
- Test Nginx configuration with `nginx -t`
- Check Nginx logs for specific errors
- Verify that the upstream service (Streamlit) is running

### Docker Issues
- Check Docker logs: `docker-compose logs`
- Ensure Docker and Docker Compose are up to date
- Verify network configurations (ports exposed correctly)

### SSL Certificate Issues
- Check certificate expiration dates
- Verify certificate paths in Nginx configuration
- Use Let's Encrypt certbot for automatic certificate management

## Helpful Commands

### Docker
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Systemd
```bash
# Start service
sudo systemctl start ai-research

# Check status
sudo systemctl status ai-research

# View logs
sudo journalctl -u ai-research -f

# Restart service
sudo systemctl restart ai-research
```

### Nginx
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check logs
sudo tail -f /var/log/nginx/error.log
```