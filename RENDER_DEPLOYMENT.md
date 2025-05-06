# Render Deployment Guide for CareEscapes API

This guide provides step-by-step instructions to deploy the CareEscapes API to Render.

## Prerequisites

1. A [Render account](https://render.com)
2. Your project code in a GitHub repository
3. A Neon database (already set up)

## Deployment Steps

### 1. Log in to Render Dashboard

Go to [Render dashboard](https://dashboard.render.com/) and log in to your account.

### 2. Create a New Web Service

1. Click on "New +" button in the top right corner
2. Select "Web Service" from the dropdown menu

### 3. Connect Your Repository

1. Connect your GitHub (or GitLab) account if you haven't already
2. Select the repository containing your CareEscapes API code

### 4. Configure the Web Service

Fill in the following details:
- **Name**: `careescapes-api` (or any name you prefer)
- **Environment**: `Python 3`
- **Region**: Choose the closest to your users
- **Branch**: `main` (or your default branch)
- **Build Command**: `pip install -r api/requirements.txt`
- **Start Command**: `cd api && python -m uvicorn db_server:app --host 0.0.0.0 --port $PORT`
- **Plan**: Start with the free plan

### 5. Add Environment Variables

Add these environment variables:

1. `DB_CONNECTION_STRING` - Your Neon database connection string
   ```
   postgresql://neondb_owner:your_password@hostname:port/neondb?sslmode=require
   ```

2. `GROQ_API_KEY` - Your GROQ API key

### 6. Deploy the Service

Click "Create Web Service" to start the deployment process.

## Verifying the Deployment

Once the deployment is complete:

1. Click on the URL provided by Render (e.g., `https://careescapes-api.onrender.com`)
2. You should see a response: `{"message":"Welcome to the CareEscapes API","database_status":"Configured"}`

## Troubleshooting

If you encounter any issues:

1. Check the logs in the Render dashboard
2. Verify your environment variables are set correctly
3. Ensure your Neon database is accessible from Render

## Updating Your Deployment

Any push to your main branch will automatically trigger a new deployment, as the `autoDeploy` setting is enabled in `render.yaml`. 