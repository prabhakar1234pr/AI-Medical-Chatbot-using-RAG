import os
import json
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv(dotenv_path="api-key.env")


# Set Groq API Key from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
 

# Initialize LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama3-8b-8192",
    temperature=0.2
)

# Intent Detection Prompt
INTENT_PROMPT_TEMPLATE = """
You are an AI assistant for a dental care chatbot.

Your tasks:
1. Identify the user's **specific intent** from the following options:
   ["faq", "search_clinics", "search_services", "search_booking", "book_appointment", "price_comparision"]

2. Extract relevant **entities** from the user input:
   - location_city
   - procedure_name
   - max_price
   - clinic_id
   - service_id
   - user_id
   - appointment_date

RULES:
- RESPOND ONLY in valid JSON.
- DO NOT include any explanation or extra text.
- If a field does not apply, use an empty string "".
- DO NOT include comments or formatting outside the JSON structure.

User input: {question}

Return your response in EXACTLY this format:
{{
  "intent": "faq | search_clinics | search_services | search_booking | book_appointment | price_comparision",
  "entities": {{
    "location_city": "",
    "procedure_name": "",
    "max_price": "",
    "clinic_id": "",
    "service_id": "",
    "user_id": "",
    "appointment_date": ""
  }}
}}
"""



intent_prompt = PromptTemplate(
    input_variables=["question"],
    template=INTENT_PROMPT_TEMPLATE
)

intent_chain = (
    {"question": RunnablePassthrough()}
    | intent_prompt
    | llm
    | StrOutputParser()
)



def handle_user_input(user_input):
    raw_response = intent_chain.invoke(user_input).strip()

    # Debug print to see what the LLM is actually returning
    print("DEBUG: LLM raw response:", raw_response)

    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError:
        return "Sorry, I couldn't understand your request. Please try again with more details."

    intent = result.get("intent")
    entities = result.get("entities", {})
    print("Intent:", intent)
    print("Entities:", entities)

    return intent



# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print("Bot:", handle_user_input(user_input))
