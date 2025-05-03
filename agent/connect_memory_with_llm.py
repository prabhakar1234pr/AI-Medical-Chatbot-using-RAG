from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

load_dotenv()

# Load API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

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

# Load FAISS vectorstore
DB_FAISS_PATH = 'db/faiss_index'
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(DB_FAISS_PATH, embedding_model,allow_dangerous_deserialization=True)  

# Setup retriever
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Define RAG chain using Runnable
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm 
    | StrOutputParser()
)

# Run it
user_query = input("Enter your question: ")
response = rag_chain.invoke(user_query)

print(f"\nAnswer: {response}")



