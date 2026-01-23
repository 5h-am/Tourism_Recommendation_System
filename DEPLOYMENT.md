# Deployment Guide

## Deploy to Render.com (Recommended - Free)

### Step 1: Prepare Your Code
1. Ensure all files are created (requirements.txt, Procfile, render.yaml)
2. Test locally: `python app.py`
3. Commit all changes to Git

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 3: Deploy on Render
1. Go to https://render.com and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select your repository
5. Render will auto-detect Python and use render.yaml settings
6. Add environment variable:
   - Key: FLASK_SECRET_KEY
   - Value: (generate a random string)
7. Click "Create Web Service"

### Step 4: Wait for Deployment
- First deployment takes 3-5 minutes
- Render will install dependencies and start the app
- You'll get a URL like: https://tourism-recommender.onrender.com

### Step 5: Test
- Visit your deployed URL
- Test all features: search, recommendations, itinerary

## Troubleshooting

### Build Fails
- Check logs in Render dashboard
- Verify requirements.txt has correct versions
- Ensure Python version matches runtime.txt

### App Crashes
- Check if data/tripadvisor_data.csv is in repository
- Verify all imports are in requirements.txt
- Check Render logs for error messages

### Slow First Load
- Free tier apps sleep after 15 min inactivity
- First request wakes it up (30-60 seconds)
- Upgrade to paid tier for always-on

## Alternative: Deploy to Railway.app

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`
5. Open: `railway open`

## Alternative: Deploy to PythonAnywhere

1. Go to https://www.pythonanywhere.com
2. Create free account
3. Upload files or clone from GitHub
4. Set up virtual environment
5. Configure WSGI file
6. Reload web app

## Important Notes
- Ensure data/tripadvisor_data.csv is committed to Git (needed for deployment)
- Never commit .env file (it's in .gitignore)
- Generate a strong SECRET_KEY for production
- Free tier on Render sleeps after 15 min - first load will be slow
- Set environment variables in Render dashboard, not in code
