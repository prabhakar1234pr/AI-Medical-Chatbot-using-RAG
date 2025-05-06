from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add agent directory to the path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print("Starting server... Importing RAG chain")
# Import the RAG chain from the agent module
try:
    from agent.connect_memory_with_llm import rag_chain
    print("RAG chain imported successfully")
except Exception as e:
    print(f"Error importing RAG chain: {e}")
    print(traceback.format_exc())
    raise

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def read_root():
    print("GET / endpoint called")
    return {"status": "online", "message": "Medical Knowledge ChatBot API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        print(f"Received chat request: {request.message}")
        # Use the rag_chain to get the response
        response = rag_chain.invoke(request.message)
        print(f"Generated response: {response[:100]}...")  # Print first 100 chars
        return ChatResponse(response=response)
    except Exception as e:
        print(f"Error processing request: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090) 