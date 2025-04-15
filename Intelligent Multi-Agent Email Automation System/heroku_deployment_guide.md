# Heroku Deployment Guide for Email Automation System

This guide provides detailed instructions for deploying the Intelligent Multi-Agent Email Automation System to Heroku.

## Prerequisites

Before beginning the deployment, ensure you have the following:

- A Heroku account (sign up at https://signup.heroku.com/ if you don't have one)
- Heroku CLI installed on your computer (https://devcenter.heroku.com/articles/heroku-cli)
- Git installed on your computer
- The email automation system code (extracted from the provided zip file)

## Backend Deployment

### Step 1: Prepare the Backend for Deployment

1. Navigate to the backend directory:
   ```bash
   cd email_automation_system/backend
   ```

2. Create a `Procfile` (this tells Heroku how to run your application):
   ```bash
   echo "web: gunicorn -k uvicorn.workers.UvicornWorker main:app" > Procfile
   ```

3. Add `gunicorn` to requirements.txt:
   ```bash
   echo "gunicorn==20.1.0" >> requirements.txt
   ```

4. Update the database and cache configuration in `config.py` to use environment variables:
   ```python
   # Add this to config.py
   import os

   # Override default config with environment variables
   if "MONGODB_URI" in os.environ:
       config["database"]["mongodb_url"] = os.environ["MONGODB_URI"]
   
   if "REDIS_URL" in os.environ:
       config["cache"]["redis_host"] = os.environ["REDIS_URL"]
   ```

### Step 2: Deploy the Backend to Heroku

1. Log in to Heroku CLI:
   ```bash
   heroku login
   ```

2. Create a new Heroku app:
   ```bash
   heroku create email-automation-backend
   ```
   Note: If this name is taken, Heroku will suggest an alternative name.

3. Add MongoDB and Redis add-ons:
   ```bash
   heroku addons:create mongolab:sandbox
   heroku addons:create heroku-redis:hobby-dev
   ```

4. Initialize a Git repository and deploy:
   ```bash
   git init
   git add .
   git commit -m "Initial backend deployment"
   git push heroku master
   ```

5. Ensure at least one instance is running:
   ```bash
   heroku ps:scale web=1
   ```

6. Open the app to verify it's running:
   ```bash
   heroku open
   ```
   
   You should see the API welcome message. The API documentation will be available at `/docs`.

## Frontend Deployment

### Step 1: Prepare the Frontend for Deployment

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Create a `.env.production` file with your backend URL:
   ```bash
   echo "REACT_APP_API_URL=https://your-backend-app-name.herokuapp.com" > .env.production
   ```
   Replace `your-backend-app-name` with the actual name of your backend Heroku app.

3. Install dependencies and build the frontend:
   ```bash
   npm install
   npm run build
   ```

4. Create a simple Express server to serve the static files (create a file named `server.js`):
   ```javascript
   const express = require('express');
   const path = require('path');
   const app = express();
   const PORT = process.env.PORT || 3000;

   // Serve static files
   app.use(express.static(path.join(__dirname, 'build')));

   // Handle React routing, return all requests to React app
   app.get('*', function(req, res) {
     res.sendFile(path.join(__dirname, 'build', 'index.html'));
   });

   app.listen(PORT, () => {
     console.log(`Server is running on port ${PORT}`);
   });
   ```

5. Create a `package.json` file for the server:
   ```bash
   npm init -y
   npm install express --save
   ```

6. Update the `package.json` to include the start script:
   ```json
   "scripts": {
     "start": "node server.js"
   }
   ```

7. Create a `Procfile`:
   ```bash
   echo "web: npm start" > Procfile
   ```

### Step 2: Deploy the Frontend to Heroku

1. Create a new Heroku app for the frontend:
   ```bash
   heroku create email-automation-frontend
   ```

2. Initialize a Git repository and deploy:
   ```bash
   git init
   git add .
   git commit -m "Initial frontend deployment"
   git push heroku master
   ```

3. Ensure at least one instance is running:
   ```bash
   heroku ps:scale web=1
   ```

4. Open the app to verify it's running:
   ```bash
   heroku open
   ```

## Connecting the Applications

1. Set CORS settings on the backend to allow requests from the frontend:
   ```bash
   heroku config:set CORS_ORIGINS=https://your-frontend-app-name.herokuapp.com --app your-backend-app-name
   ```
   Replace `your-frontend-app-name` and `your-backend-app-name` with your actual Heroku app names.

2. Restart the backend app:
   ```bash
   heroku restart --app your-backend-app-name
   ```

## Testing the Deployment

1. Visit your frontend URL (https://your-frontend-app-name.herokuapp.com)
2. Log in with the default credentials (admin/adminpassword)
3. Configure your email providers and integration services
4. Start using the system!

## Troubleshooting

If you encounter issues with your deployment, you can check the logs:

```bash
# For backend logs
heroku logs --tail --app your-backend-app-name

# For frontend logs
heroku logs --tail --app your-frontend-app-name
```

Common issues:
- Database connection errors: Check that the MongoDB add-on is properly provisioned
- Redis connection errors: Check that the Redis add-on is properly provisioned
- CORS errors: Ensure the CORS settings are correctly configured
- Build failures: Check for any syntax errors or missing dependencies

## Scaling Your Application

As your usage grows, you may need to scale your application:

```bash
# Scale web dynos
heroku ps:scale web=2 --app your-app-name

# Upgrade database plan
heroku addons:upgrade mongolab:standard --app your-backend-app-name

# Upgrade Redis plan
heroku addons:upgrade heroku-redis:premium-0 --app your-backend-app-name
```

## Monitoring

Heroku provides basic monitoring through the dashboard. For more advanced monitoring:

1. Add the New Relic add-on:
   ```bash
   heroku addons:create newrelic:wayne --app your-app-name
   ```

2. Configure New Relic according to their documentation

## Backup and Recovery

To ensure your data is backed up:

1. Enable automated backups for MongoDB:
   ```bash
   heroku addons:create mongolab:backup-auto --app your-backend-app-name
   ```

2. You can also manually create backups:
   ```bash
   heroku addons:create mongolab:backup --app your-backend-app-name
   ```

## Security Considerations

1. Set up environment variables for sensitive information:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key --app your-backend-app-name
   ```

2. Enable Heroku's automatic TLS:
   ```bash
   heroku features:enable http-session-affinity --app your-app-name
   ```

3. Consider adding authentication add-ons like Auth0:
   ```bash
   heroku addons:create auth0 --app your-frontend-app-name
   ```
