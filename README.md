# CareEscapes-AI-ChatBot

A medical chatbot built with Azure OpenAI and LangChain that provides helpful medical information. This repository contains the chatbot service with multiple specialized tools.

## Architecture

The CareEscapes application consists of three separate components:

1. **Frontend** - React web application in medical-chatbot-frontend
2. **Backend API** - FastAPI service that handles requests from the frontend
3. **Chatbot Engine** - AI-powered chatbot with specialized tools

The components interact as follows:
- User interacts with the Frontend
- Frontend makes API calls to Backend
- Backend communicates with the Chatbot engine
- Results flow back to the user

## Features

- AI-powered medical chatbot
- Tool-based architecture for specialized capabilities:
  - FAQ Queries
  - Search for Clinics
  - Search for Services
  - Search for Bookings
  - Create Bookings
  - Price Comparison
- Conversation memory across sessions
- Simple REST API for frontend integration

## Prerequisites

- Python 3.9+
- Azure OpenAI API access
- Node.js and npm (for frontend)

## Setup and Running

### Backend Setup

1. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials (see `.env.example` for reference)

4. Run the FastAPI backend
   ```bash
   cd api
   python run.py
   ```
   
   The API will be available at http://localhost:8000

5. API Documentation: View Swagger docs at http://localhost:8000/docs

### Frontend Setup

1. Navigate to the frontend directory
   ```bash
   cd medical-chatbot-frontend
   ```

2. Install dependencies
   ```bash
   npm install
   ```

3. Run the development server
   ```bash
   npm start
   ```
   
   The frontend will be available at http://localhost:3000

## API Endpoints

- `GET /`: Welcome message
- `POST /chat`: Chat with the bot
  ```json
  {
    "user_input": "What are symptoms of the flu?",
    "session_id": "optional-session-id"
  }
  ```
- `GET /tools`: List available tools
- `POST /tool/{tool_name}`: Directly execute a specific tool (for testing)
- `DELETE /sessions/{session_id}`: Delete a conversation session
- `GET /health`: Health check endpoint

## Docker Deployment

1. Build the Docker image
   ```bash
   docker build -t medical-chatbot .
   ```

2. Run the container with environment variables
   ```bash
   docker run -it -p 8000:8000 --env-file .env medical-chatbot
   ```

## Customizing the Tools

Each tool is implemented as a separate Python class in the `Agent/tools/` directory. To customize a tool:

1. Edit the corresponding tool file (e.g., `Agent/tools/faq_tool.py`)
2. Implement the `execute` method with your desired logic
3. Return a dictionary with the results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Deployment

The chatbot is automatically deployed to Azure Container Instances when changes are pushed to the main branch via GitHub Actions.

### Required GitHub Secrets

The following secrets need to be set in your GitHub repository:

- `ACR_LOGIN_SERVER`: Azure Container Registry server URL (format: `registryname.azurecr.io`)
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

> **Note:** Make sure all secrets are properly configured before pushing changes, especially the ACR_LOGIN_SERVER which must be in the format `registryname.azurecr.io`.

### Accessing the Deployed API

The Chatbot API will be available at:
```
http://careescapes-chatbot.[AZURE_REGION].azurecontainer.io:8000
``` 