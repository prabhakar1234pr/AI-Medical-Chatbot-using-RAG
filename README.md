# Medical Knowledge Chatbot

A chatbot application that uses RAG (Retrieval-Augmented Generation) to answer medical questions based on the GALE Encyclopedia of Medicine.

## Project Structure

- `/agent` - Contains the AI agent implementation for the chatbot
- `/api` - FastAPI backend that connects the frontend to the AI agent
- `/db` - FAISS vector database storing document embeddings
- `/data` - Contains the medical encyclopedia PDF
- `/frontend` - React frontend for the chatbot interface

## Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- Groq API key (stored in .env file)

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Environment Setup

Create a `.env` file in the root directory with your Groq API key:

```
GROQ_API_KEY=your-api-key-here
```

### 3. Backend Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### 1. Start the FastAPI Backend

```bash
cd api
uvicorn main:app --reload
```

The API server will run at http://localhost:8000

### 2. Start the React Frontend

```bash
cd frontend
npm start
```

The frontend will run at http://localhost:3000

## Usage

1. Open your browser and navigate to http://localhost:3000
2. Type your medical question in the chat input
3. The system will retrieve relevant information from the medical encyclopedia and provide an answer

## API Endpoints

- `GET /` - Check if the API is running
- `POST /chat` - Send a message to the chatbot
  - Request body: `{ "message": "your question here" }`
  - Response: `{ "response": "chatbot answer" }` 