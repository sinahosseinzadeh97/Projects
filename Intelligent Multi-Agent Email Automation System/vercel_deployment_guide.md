# Frontend Deployment Instructions for Vercel

## Prerequisites
- A Vercel account (sign up at https://vercel.com if you don't have one)
- Node.js and npm installed on your local machine

## Step 1: Update API URL Configuration
Before deploying to Vercel, you need to create an environment variable file to connect to your Heroku backend:

1. Create a file named `.env` in the frontend directory with the following content:
```
REACT_APP_API_URL=https://your-heroku-app-name.herokuapp.com
```
Replace `your-heroku-app-name` with the actual name of your Heroku backend app.

## Step 2: Deploy to Vercel Using the Vercel CLI

1. Install the Vercel CLI:
```bash
npm install -g vercel
```

2. Navigate to the frontend directory:
```bash
cd email_automation_demo/frontend
```

3. Login to Vercel:
```bash
vercel login
```

4. Deploy the project:
```bash
vercel
```

5. Follow the prompts in the CLI:
   - Set up and deploy? Yes
   - Which scope? (Select your account)
   - Link to existing project? No
   - What's your project's name? email-automation-frontend
   - In which directory is your code located? ./
   - Want to override the settings? No

## Step 3: Deploy to Vercel Using the Vercel Dashboard

Alternatively, you can deploy directly from the Vercel dashboard:

1. Go to https://vercel.com/new
2. Import your project from a Git repository or upload the frontend directory
3. Configure the project:
   - Framework Preset: Create React App
   - Build Command: npm run build
   - Output Directory: build
   - Environment Variables: Add REACT_APP_API_URL with your Heroku backend URL

4. Click "Deploy"

## Step 4: Configure Environment Variables

After deployment, you can add or update environment variables:

1. Go to your project in the Vercel dashboard
2. Navigate to Settings > Environment Variables
3. Add the variable:
   - Name: REACT_APP_API_URL
   - Value: https://your-heroku-app-name.herokuapp.com
4. Click "Save"
5. Redeploy your application for the changes to take effect

## Step 5: Verify Deployment

1. Once deployed, Vercel will provide you with a URL (typically https://email-automation-frontend.vercel.app)
2. Visit the URL to ensure your frontend is working correctly
3. Try logging in with the demo credentials (username: admin, password: adminpassword)
4. Verify that the frontend can communicate with your Heroku backend

## Troubleshooting

If you encounter CORS issues:
1. Make sure your Heroku backend has the correct CORS configuration
2. Check that the REACT_APP_API_URL environment variable is set correctly
3. Verify that your backend is running and accessible

If you see build errors:
1. Check the build logs in the Vercel dashboard
2. Ensure all dependencies are correctly listed in package.json
3. Verify that the vercel.json configuration is correct
