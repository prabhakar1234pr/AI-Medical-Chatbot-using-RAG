import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain


# Environment Setup 

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
FAISS_DB_PATH = os.getenv("FAISS_DB_PATH", "db/faiss_index")

if not GROQ_API_KEY:
    raise EnvironmentError("❌ Missing GROQ_API_KEY in environment variables.")


# LLM Initialization 

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama3-8b-8192",
    temperature=0.2,
    max_retries=3,
    timeout=30.0
)

# Retriever Setup 

def get_redis_memory(session_id: str) -> ConversationBufferMemory:
    chat_history = RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL
    )
    return ConversationBufferMemory(
        chat_memory=chat_history,
        return_messages=True
    )


# Prompt Template 

RAG_PROMPT = """
You are a helpful and precise medical assistant. Use the provided context to answer the user’s question.
If you don’t know the answer, simply say "I don’t know" — do not fabricate information.

Context:
{context}

User Question:
{question}

Answer:
"""

prompt = ChatPromptTemplate.from_template(RAG_PROMPT)


# Build Conversational RAG Chain

def get_conversational_chain(session_id: str = "careescapes-session") -> ConversationalRetrievalChain:
    memory = get_redis_memory(session_id)
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=False
    )

# CLI for Testing 

if __name__ == "__main__":
    print("Launching CareEscapes AI Chatbot (RAG + Redis Memory)")
    print("Type 'exit' to quit.\n")

    chain = get_conversational_chain()

    while True:
        query = input("You: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("👋 Exiting chatbot. Stay healthy!")
            break

        try:
            response = chain.invoke({"question": query})
            print(f" Bot: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")