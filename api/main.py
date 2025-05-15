import os
import sys
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid

# Add the project root to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our chatbot
from Agent.chatbot import get_bot_response

# Initialize FastAPI app
app = FastAPI(
    title="Medical Chatbot API",
    description="API for the medical chatbot with tool-based functionality",
    version="1.0.0"
)

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store conversation history for different sessions
conversation_histories = {}

# Request models
class ChatRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None

class ToolSelectionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    session_id: Optional[str] = None

# Response models
class ChatResponse(BaseModel):
    response: str
    session_id: str

class ToolResponse(BaseModel):
    result: Dict[str, Any]
    session_id: str
    
# Helper function to get or create a session
def get_session_id(session_id: Optional[str] = None) -> str:
    if not session_id:
        return str(uuid.uuid4())
    return session_id

# Helper function to get conversation history
def get_conversation_history(session_id: str) -> List:
    if session_id not in conversation_histories:
        conversation_histories[session_id] = [
            {"role": "system", "content": "You are a helpful medical assistant that can answer questions and help with clinic bookings."}
        ]
    return conversation_histories[session_id]

@app.get("/")
def read_root():
    return {"message": "Medical Chatbot API is running"}

@app.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    try:
        # Get or create session
        session_id = get_session_id(request.session_id)
        
        # Get conversation history for this session
        conversation_history = get_conversation_history(session_id)
        
        # Process the user input
        reply, updated_history = get_bot_response(request.user_input, conversation_history)
        
        # Update the conversation history
        conversation_histories[session_id] = updated_history
        
        return ChatResponse(response=reply, session_id=session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/tools")
def list_available_tools():
    """Return a list of available tools that the chatbot can use."""
    try:
        from Agent.tools import tools
        return {
            "tools": list(tools.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tools: {str(e)}")

@app.post("/tool/{tool_name}")
def execute_tool_directly(tool_name: str, request: Dict[str, Any]):
    """Directly execute a specific tool (for development/testing)."""
    try:
        from Agent.tools import tools
        
        if tool_name not in tools:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        result = tools[tool_name].execute(request)
        return {"result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool: {str(e)}")

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a conversation session."""
    if session_id in conversation_histories:
        del conversation_histories[session_id]
        return {"message": f"Session {session_id} deleted"}
    
    raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 