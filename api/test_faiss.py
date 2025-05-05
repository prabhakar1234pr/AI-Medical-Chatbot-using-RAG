import os
import sys
import traceback

# Get the absolute path to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Project root: {PROJECT_ROOT}")

# Add project root to Python path
sys.path.append(PROJECT_ROOT)

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    
    # Use absolute path for FAISS index
    DB_FAISS_PATH = os.path.join(PROJECT_ROOT, 'db', 'faiss_index')
    print(f"FAISS index path: {DB_FAISS_PATH}")
    
    # Check if directory exists
    print(f"Directory exists: {os.path.isdir(DB_FAISS_PATH)}")
    
    # List files in the directory
    print("Files in directory:")
    for file in os.listdir(DB_FAISS_PATH):
        print(f"- {file}")
    
    # Check if the index files exist
    faiss_file = os.path.join(DB_FAISS_PATH, 'index.faiss')
    pkl_file = os.path.join(DB_FAISS_PATH, 'index.pkl')
    print(f"FAISS file exists: {os.path.exists(faiss_file)}")
    print(f"PKL file exists: {os.path.exists(pkl_file)}")
    
    # Initialize embedding model
    print("Initializing embedding model...")
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Load FAISS vectorstore
    print("Loading FAISS index...")
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True, index_name="index")
    
    # Test a simple query
    print("Testing query...")
    docs = db.similarity_search("test query", k=1)
    print(f"Retrieved document: {docs[0].page_content[:100]}...")
    
    print("FAISS test completed successfully!")
except Exception as e:
    print(f"Error: {e}")
    print(traceback.format_exc()) 