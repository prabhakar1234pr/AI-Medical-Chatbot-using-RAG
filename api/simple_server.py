from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
import traceback
from pydantic import BaseModel

# Add agent directory to the path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print("Starting server... Importing RAG chain")
try:
    from agent.connect_memory_with_llm import rag_chain
    print("RAG chain imported successfully")
except Exception as e:
    print(f"Error importing RAG chain: {e}")
    print(traceback.format_exc())
    rag_chain = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "API is working!"}

@app.post("/echo")
async def echo(request: dict):
    return {"message": f"You said: {request.get('message', '')}"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        print(f"Received chat request: {request.message}")
        
        if rag_chain is None:
            return {"message": "RAG chain not available. Using echo mode instead.", "type": "error"}
        
        # Use the rag_chain to get the response
        response = rag_chain.invoke(request.message)
        print(f"Generated response: {response[:100]}...")  # Print first 100 chars
        
        return {"message": response}
    except Exception as e:
        print(f"Error processing request: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8091) 