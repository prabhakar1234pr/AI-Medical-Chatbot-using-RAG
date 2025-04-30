from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

# Load the Groq API key from environment variable
GROQ_API_KEY  = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

# Initialize the model
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama3-8b-8192",
    max_retries=3,  # Add retries
    timeout=30.0
)

# Define the chat prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful and funny AI assistant."),
    ("user", "{input}")
])

# Create the runnable chain
chain: Runnable = prompt | llm | StrOutputParser()

# Run the chatbot
while True:
    user_input = input("User: ")
    if user_input.lower() in ['exit', 'quit']:
        print("Goodbye! 👋")
        break
    response = chain.invoke({"input": user_input})
    print(f"Bot: {response}\n")