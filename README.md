# Medical Chatbot Demo

A medical chatbot with a React frontend and FastAPI backend that can use 6 different tools to assist users:

1. **FAQ Tool**: Answers general medical questions
2. **Clinic Search Tool**: Finds clinics by location or specialty
3. **Service Search Tool**: Provides information about medical services 
4. **Booking Search Tool**: Looks up existing appointments
5. **Booking Creation Tool**: Schedules new appointments
6. **Price Comparison Tool**: Compares costs of medical services

## Setup for Local Demo

### 1. Set up Azure OpenAI credentials

Create a `.env` file in the root directory with your Azure OpenAI credentials:

```
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_ENDPOINT=https://your-azure-openai-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

### 2. Run the demo (easiest way)

Just run the batch file:

```
.\start_demo.bat
```

### OR Manual startup:

#### 2.1 Activate the virtual environment

```
.\chatbot_env\Scripts\activate
```

#### 2.2 Start the backend server

```
cd api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will run on http://localhost:8000

#### 2.3 Start the frontend

In a separate terminal:

```
cd medical-chatbot-frontend
npm start
```

The frontend will be available at http://localhost:3000

## Using the Chatbot

You can trigger different tools with queries like:

- "What are common symptoms of the flu?" (FAQ)
- "Find dermatologists near Boston" (Clinic Search)
- "What services do you offer for prenatal care?" (Service Search)
- "Check my appointment for next Tuesday" (Booking Search)
- "I need to schedule a dental cleaning" (Booking Creation)
- "Compare prices for a basic checkup between different clinics" (Price Comparison)

## API Endpoints

- `GET /`: Health check
- `POST /chat`: Main chatbot endpoint
- `GET /tools`: Lists all available tools
- `POST /tool/{tool_name}`: Execute a specific tool directly
- `DELETE /sessions/{session_id}`: Delete a conversation session
- `GET /health`: Health check endpoint 