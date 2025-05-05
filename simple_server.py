from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
import traceback
from pydantic import BaseModel

# Get the absolute path to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)  # Add project root to Python path

print(f"Project root: {PROJECT_ROOT}")
print("Starting server... Importing RAG chain")

# Set the PYTHONPATH for subprocesses
os.environ["PYTHONPATH"] = PROJECT_ROOT

try:
    # Import the necessary modules
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import PromptTemplate
    from langchain_groq import ChatGroq
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Load API key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        print("GROQ_API_KEY environment variable not set")
        rag_chain = None
    else:
        # Initialize LLM with Groq
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="llama3-8b-8192",
            temperature=0.2,
            max_retries=3,
            timeout=30.0,
        )
        
        # Prompt template
        CUSTOM_PROMPT_TEMPLATE = """
        Use the pieces of information provided in the context to answer user's question.
        If you don't know the answer, just say that you don't know — don't try to make up an answer.
        Don't provide anything outside the given context.

        Context: {context}
        Question: {question}

        Start the answer directly. No small talk please.
        """
        
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=CUSTOM_PROMPT_TEMPLATE
        )
        
        # Use absolute path for FAISS index
        DB_FAISS_PATH = os.path.join(PROJECT_ROOT, 'db', 'faiss_index')
        print(f"Loading FAISS index from: {DB_FAISS_PATH}")
        
        # Check if the index files exist
        print(f"Index files exist: {os.path.exists(os.path.join(DB_FAISS_PATH, 'index.faiss'))}")
        
        # Initialize embedding model
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Load FAISS vectorstore
        db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True, index_name="index")
        
        # Setup retriever
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        
        # Define RAG chain using Runnable
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm 
            | StrOutputParser()
        )
        
        print("RAG chain initialized successfully")
except Exception as e:
    print(f"Error initializing RAG chain: {e}")
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