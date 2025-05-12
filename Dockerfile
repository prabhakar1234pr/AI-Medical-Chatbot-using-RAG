FROM python:3.9-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy chatbot code
COPY Agent/ ./Agent/

# Create a simple API wrapper for the chatbot
RUN echo 'from fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel\nfrom Agent.chatbot import get_bot_response\n\napp = FastAPI()\n\n@app.get("/")\ndef root():\n    return {"message": "Medical Chatbot API"}\n\nclass ChatRequest(BaseModel):\n    user_input: str\n    session_id: str = "default_user"\n\n@app.post("/chat")\ndef chat_with_bot(request: ChatRequest):\n    try:\n        reply = get_bot_response(request.user_input, request.session_id)\n        return {"response": reply}\n    except Exception as e:\n        raise HTTPException(status_code=500, detail=str(e))' > chatbot_api.py

# Default command runs the minimal API for the chatbot
CMD ["uvicorn", "chatbot_api:app", "--host", "0.0.0.0", "--port", "8000"] 