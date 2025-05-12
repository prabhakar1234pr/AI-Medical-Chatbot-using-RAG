# CareEscapes-AI-ChatBot

A medical chatbot built with Azure OpenAI and LangChain that provides helpful medical information. This repository contains the chatbot service that will be deployed as a container.

## Architecture

The CareEscapes application consists of three separate components:

1. **Frontend** - Static web application deployed to Azure Static Web Apps
2. **Backend** - API service deployed to Azure App Service
3. **Chatbot** - This repository, deployed as a container to Azure Container Instances

The components interact as follows:
- User interacts with the Frontend
- Frontend makes API calls to Backend
- Backend communicates with Chatbot container
- Results flow back to the user

## Features

- AI-powered medical chatbot
- Conversation memory with Redis
- Simple REST API for backend integration
- Automatic CI/CD deployment to Azure Container Instances

## Prerequisites

- Python 3.9+
- Azure OpenAI API access
- Redis instance (for conversation history)

## Local Setup

1. Clone the repository
   ```bash
   git clone https://github.com/prabhakar1234pr/CareEscapes-AI-ChatBot.git
   cd CareEscapes-AI-ChatBot
   ```

2. Create a virtual environment and install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials (see `.env.example` for reference)

4. Run the chatbot CLI for testing
   ```bash
   python -m Agent.chatbot
   ```

## Docker Usage

1. Build the Docker image
   ```bash
   docker build -t medical-chatbot .
   ```

2. Run the container with environment variables
   ```bash
   docker run -it -p 8000:8000 --env-file .env medical-chatbot
   ```

3. Access the API at http://localhost:8000

## API Endpoints

- `GET /`: Welcome message
- `POST /chat`: Chat with the bot
  ```json
  {
    "user_input": "What are symptoms of the flu?",
    "session_id": "user123"  // Optional, defaults to "default_user"
  }
  ```

## Deployment

The chatbot is automatically deployed to Azure Container Instances when changes are pushed to the main branch via GitHub Actions.

### Required GitHub Secrets

The following secrets need to be set in your GitHub repository:

- `ACR_LOGIN_SERVER`: Azure Container Registry server URL
- `ACR_USERNAME`: Azure Container Registry username
- `ACR_PASSWORD`: Azure Container Registry password
- `AZURE_CREDENTIALS`: Azure service principal credentials JSON
- `ACI_RESOURCE_GROUP`: Azure resource group for Container Instance
- `ACI_REGION`: Azure region for Container Instance
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `AZURE_OPENAI_API_VERSION`: Azure OpenAI API version
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT`: Azure OpenAI deployment name
- `REDIS_URL`: Redis connection URL

### Accessing the Deployed API

The Chatbot API will be available at:
```
http://careescapes-chatbot.[AZURE_REGION].azurecontainer.io:8000
``` 