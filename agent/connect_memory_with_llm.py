# ✅ Updated connect_memory_with_llm.py with Redis Memory + RAG Integration

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import os
from dotenv import load_dotenv
import json
import sys
from datetime import datetime, timedelta
import uuid
import re

# Add the parent directory to sys.path to import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.connector import (
    search_clinics, create_booking, get_user_bookings, cancel_booking,
    create_user, find_user_by_name, get_user, update_user
)

# Load environment variables
load_dotenv()

# Load API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

# Initialize LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama3-8b-8192",
    temperature=0.2,
    max_retries=3,
    timeout=30.0,
)

# ---------- PROMPTS ----------

FAQ_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer user's question.
If you don't know the answer, just say that you don't know — don't try to make up an answer.
Don't provide anything outside the given context.

Context: {context}
Question: {question}

Start the answer directly. No small talk please.
"""

faq_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=FAQ_PROMPT_TEMPLATE
)

INTENT_PROMPT_TEMPLATE = """
You are a dental tourism chatbot for CareEscapes. Your job is to detect the user's intent and extract relevant entities.

User input: {question}

Possible intents are:
- "faq_query"
- "book_appointment"
- "search_clinics"
- "view_bookings"
- "cancel_booking"
- "provide_name"
- "navigation_command"

Respond with JSON:
{
  "intent": "...",
  "entities": {
    "first_name": "...",
    "last_name": "...",
    "procedure_name": "...",
    "location_city": "...",
    "max_price": "..."
  }
}
Only fill in what's provided.
"""

intent_prompt = PromptTemplate(
    input_variables=["question"],
    template=INTENT_PROMPT_TEMPLATE
)

# ---------- Vectorstore + Retriever ----------

DB_FAISS_PATH = 'db/faiss_index'
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True, index_name="index")
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# ---------- Redis Memory Setup ----------

chat_history = RedisChatMessageHistory(session_id="demo-session", url="redis://localhost:6379")
memory = ConversationBufferMemory(chat_memory=chat_history, return_messages=True)

# ---------- Conversational RAG Chain ----------

rag_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=False
)

# ---------- Intent Detection Chain ----------

intent_chain = (
    {"question": RunnablePassthrough()}
    | intent_prompt
    | llm
    | StrOutputParser()
)

# You can now use rag_chain.invoke({"question": "your input"}) in CLI or FastAPI
if __name__ == "__main__":
    print("🧠 CareEscapes Memory-Enhanced Chatbot (RAG + Redis)")
    print("Type 'exit' to quit.")
    while True:
        query = input("\nUser: ")
        if query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        try:
            result = rag_chain.invoke({"question": query})
            print("\nBot:", result)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
