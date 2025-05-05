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
You are an AI assistant for a dental tourism platform called CareEscapes.

Your job is to understand what the user is trying to do (intent) and extract important details (entities) from their input.

## TASK:

Given the user message below, classify the **intent** from the list below and extract any relevant **entities**. If something is not present, leave it empty or null.

**Possible Intents**:
- book_appointment
- cancel_appointment
- reschedule_appointment
- provide_name
- search_clinics
- update_profile
- faq_query
- navigation_command
- confirm_action
- deny_action
- unknown

**Entities to Extract (if present)**:
- first_name
- last_name
- full_name
- email
- phone_number
- location_city
- location_country
- procedure_name
- preferred_date
- preferred_time
- budget
- clinic_name
- doctor_name
- page_to_navigate

## EXAMPLES:

User: "I want to book an appointment for implants in Mexico under $1000"

Output:
{{
  "intent": "book_appointment",
  "entities": {{
    "procedure_name": "implants",
    "location_country": "Mexico",
    "budget": "$1000"
  }}
}}

User: "Hi, my name is Prabhakar Elavala"

Output:
{{
  "intent": "provide_name",
  "entities": {{
    "first_name": "Prabhakar",
    "last_name": "Elavala",
    "full_name": "Prabhakar Elavala"
  }}
}}

User: "Take me to the profile page"

Output:
{{
  "intent": "navigation_command",
  "entities": {{
    "page_to_navigate": "profile"
  }}
}}

## USER INPUT:
{user_input}

## RESPONSE (in JSON):
"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=CUSTOM_PROMPT_TEMPLATE
)

# Load FAISS vectorstore
DB_FAISS_PATH = 'db/faiss_index'
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# Explicitly specify the index name
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

# Run it
if __name__ == "__main__":
    user_query = input("Enter your question: ")
    response = rag_chain.invoke(user_query)
    print(f"\nAnswer: {response}")



