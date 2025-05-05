from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import traceback
from pydantic import BaseModel
from dotenv import load_dotenv

# Get the absolute path to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Project root: {PROJECT_ROOT}")

# Add project root to Python path
sys.path.append(PROJECT_ROOT)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class ChatRequest(BaseModel):
    message: str

# Initialize components for RAG
try:
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import PromptTemplate
    from langchain_groq import ChatGroq
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    # Get Groq API key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        print("GROQ_API_KEY not found in environment variables")
        rag_chain = None
    else:
        print("GROQ_API_KEY found in environment variables")
        
        # Initialize LLM
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="llama3-8b-8192",
            temperature=0.2,
            max_retries=3,
            timeout=30.0,
        )
        
        # Set up prompt template
        prompt_template = """
        Use the pieces of information provided in the context to answer user's question.
        If you don't know the answer, just say that you don't know — don't try to make up an answer.
        Don't provide anything outside the given context.

        Context: {context}
        Question: {question}

        Start the answer directly. No small talk please.
        """
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=prompt_template
        )
        
        # Set up embedding model and vector store
        DB_FAISS_PATH = os.path.join(PROJECT_ROOT, 'db', 'faiss_index')
        print(f"Loading FAISS index from: {DB_FAISS_PATH}")
        
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        db = FAISS.load_local(
            folder_path=DB_FAISS_PATH, 
            embeddings=embedding_model, 
            allow_dangerous_deserialization=True,
            index_name="index"
        )
        
        # Set up retriever
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        
        # Define RAG chain
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

@app.get("/")
def root():
    return {"message": "Medical Knowledge Chatbot API is running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        print(f"Received chat request: {request.message}")
        
        if rag_chain is None:
            return {"message": "RAG chain not available. Using echo mode instead.", "type": "error"}
        
        # Process the request using the RAG chain
        response = rag_chain.invoke(request.message)
        print(f"Generated response: {response[:100]}...")
        
        return {"message": response}
    except Exception as e:
        print(f"Error processing request: {e}")
        print(traceback.format_exc())
        return {"message": f"Error: {str(e)}", "type": "error"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8091) 