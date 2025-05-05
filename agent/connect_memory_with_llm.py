from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
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

# ------------------ PROMPTS ------------------

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
- "faq_query": General medical or dental questions
- "book_appointment": User wants to book an appointment
- "search_clinics": User wants to find clinics (by location, procedure, price)
- "view_bookings": User wants to see their bookings
- "cancel_booking": User wants to cancel a booking
- "provide_name": User is providing personal information (name, email, etc.)
- "navigation_command": User wants to navigate to another page

Respond with JSON in the format:
{{
  "intent": "...",
  "entities": {{
    "user_id": "...",
    "first_name": "...",
    "last_name": "...",
    "email_id": "...",
    "mobile": "...",
    "procedure_name": "...",
    "location_city": "...",
    "max_price": "...",
    "booking_id": "...",
    "clinic_id": "...",
    "service_id": "...",
    "doctor_id": "...",
    "appointment_date": "...",
    "page_to_navigate": "..."
  }}
}}
Only fill in what's provided. Leave others as null or empty string.
"""

intent_prompt = PromptTemplate(
    input_variables=["question"],
    template=INTENT_PROMPT_TEMPLATE
)

# ------------------ VECTORSTORE + RETRIEVER ------------------

DB_FAISS_PATH = 'db/faiss_index'
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True, index_name="index")
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# ------------------ CHAINS ------------------

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | faq_prompt
    | llm 
    | StrOutputParser()
)

intent_chain = (
    {"question": RunnablePassthrough()}
    | intent_prompt
    | llm
    | StrOutputParser()
)

# ------------------ API FUNCTIONS ------------------

def handle_search_clinics(entities):
    """
    Search for clinics using the API connector.
    """
    try:
        # Extract parameters from entities
        location_city = entities.get('location_city')
        procedure_name = entities.get('procedure_name')
        max_price = entities.get('max_price')
        
        # If max_price is a string, convert to float
        if max_price and isinstance(max_price, str) and max_price.replace('.', '', 1).isdigit():
            max_price = float(max_price)
        
        # Call the API
        search_results = search_clinics(
            location_city=location_city,
            procedure_name=procedure_name,
            max_price=max_price
        )
        
        # Check if there's an error
        if isinstance(search_results, dict) and 'error' in search_results:
            return f"❌ Error searching clinics: {search_results['error']}"
        
        # Format the results for display
        if not search_results:
            return "Sorry, no clinics found matching your search criteria."
        
        result_text = "📋 Here are the clinics I found:\n\n"
        for idx, clinic_data in enumerate(search_results, 1):
            clinic = clinic_data['clinic']
            service = clinic_data['service']
            result_text += f"{idx}. {clinic['clinic_name']} ({clinic['location_city']}, {clinic['location_country']})\n"
            result_text += f"   Service: {service['service_name']}\n"
            result_text += f"   Price Range: {service['pricestart']}-{service['priceend']} {service['currency']}\n"
            result_text += f"   Clinic ID: {clinic['clinic_id']} | Service ID: {service['service_id']}\n\n"
        
        result_text += "If you'd like to book an appointment, please provide the clinic ID and service ID."
        
        return result_text
    except Exception as e:
        return f"❌ An error occurred while searching for clinics: {str(e)}"

def handle_booking_creation(entities):
    """
    Create a booking using the API connector.
    """
    try:
        # Extract required parameters
        user_id = entities.get('user_id')
        clinic_id = entities.get('clinic_id')
        service_id = entities.get('service_id')
        doctor_id = entities.get('doctor_id')
        
        # Handle appointment date
        appointment_date = entities.get('appointment_date')
        # If appointment_date is not provided, set it to tomorrow at 10am
        if not appointment_date:
            tomorrow = datetime.now() + timedelta(days=1)
            appointment_date = tomorrow.replace(hour=10, minute=0, second=0).isoformat()
        
        # Validate required fields
        if not user_id or not clinic_id or not service_id:
            missing = []
            if not user_id: missing.append("user ID")
            if not clinic_id: missing.append("clinic ID")
            if not service_id: missing.append("service ID")
            return f"❌ Cannot create booking: Missing {', '.join(missing)}."
        
        # Create the booking
        booking_result = create_booking(
            user_id=user_id,
            clinic_id=clinic_id,
            service_id=service_id,
            doctor_id=doctor_id,
            appointment_startdate=appointment_date
        )
        
        # Check if there's an error
        if isinstance(booking_result, dict) and 'error' in booking_result:
            return f"❌ Error creating booking: {booking_result['error']}"
        
        # Format the success response
        result_text = "✅ Booking created successfully!\n\n"
        result_text += f"Booking ID: {booking_result['booking_id']}\n"
        result_text += f"Appointment: {booking_result['appointment_start']}\n"
        result_text += f"Status: {booking_result['booking_status']}\n"
        result_text += "\nThe clinic will confirm your booking soon. You can view your bookings or cancel if needed."
        
        return result_text
    except Exception as e:
        return f"❌ An error occurred while creating booking: {str(e)}"

def handle_view_bookings(entities):
    """
    Get a user's bookings using the API connector.
    """
    try:
        # Extract the user ID
        user_id = entities.get('user_id')
        
        # Validate required fields
        if not user_id:
            return "❌ Cannot view bookings: User ID is required."
        
        # Get the bookings
        bookings = get_user_bookings(user_id)
        
        # Check if there's an error
        if isinstance(bookings, dict) and 'error' in bookings:
            return f"❌ Error retrieving bookings: {bookings['error']}"
        
        # Format the results
        if not bookings:
            return "You don't have any bookings at the moment."
        
        result_text = "📋 Your bookings:\n\n"
        for idx, booking in enumerate(bookings, 1):
            result_text += f"{idx}. Booking ID: {booking['booking_id']}\n"
            result_text += f"   Date: {booking['appointment_start']}\n"
            result_text += f"   Status: {booking['booking_status']}\n"
            result_text += f"   Clinic ID: {booking['clinic_id']}\n"
            result_text += f"   Service ID: {booking['service_id']}\n\n"
        
        return result_text
    except Exception as e:
        return f"❌ An error occurred while retrieving bookings: {str(e)}"

def handle_cancel_booking(entities):
    """
    Cancel a booking using the API connector.
    """
    try:
        # Extract the booking ID
        booking_id = entities.get('booking_id')
        
        # Validate required fields
        if not booking_id:
            return "❌ Cannot cancel booking: Booking ID is required."
        
        # Cancel the booking
        result = cancel_booking(booking_id)
        
        # Check if there's an error
        if isinstance(result, dict) and 'error' in result:
            return f"❌ Error cancelling booking: {result['error']}"
        
        return "✅ Your booking has been successfully cancelled."
    except Exception as e:
        return f"❌ An error occurred while cancelling booking: {str(e)}"

def handle_user_info(entities):
    """
    Process user information, create or update user in database.
    """
    try:
        # Extract user information
        first_name = entities.get('first_name')
        last_name = entities.get('last_name', '')  # Default to empty string
        email_id = entities.get('email_id')
        mobile = entities.get('mobile')
        user_id = entities.get('user_id')
        
        print(f"Processing user info: {first_name} {last_name}")
        
        # Default email if not provided
        if not email_id and first_name:
            # Create a simple default email using name
            name_part = f"{first_name}{last_name}".lower().replace(' ', '')
            email_id = f"{name_part}@example.com"
            print(f"Generated default email: {email_id}")
        
        # If we have a user ID, try to update the user
        if user_id:
            update_data = {}
            if first_name: update_data['first_name'] = first_name
            if last_name: update_data['last_name'] = last_name
            if mobile: update_data['mobile'] = mobile
            
            if update_data:
                result = update_user(user_id, update_data)
                if isinstance(result, dict) and 'error' in result:
                    return f"❌ Could not update your information: {result['error']}"
                return f"✅ Your profile has been updated, {first_name or 'User'}!"
        
        # If we have a first name, try to find or create a user
        if first_name:
            # Try to find the user by name
            if last_name:
                print(f"Searching for user by name: {first_name} {last_name}")
                existing_users = find_user_by_name(first_name, last_name)
                
                # Check for valid response
                if not isinstance(existing_users, dict) and existing_users:
                    # User exists
                    user = existing_users[0]
                    return f"✅ Welcome back, {user['first_name']}! Your user ID is {user['user_id']}."
            
            # No existing user, create new one
            if email_id:
                print(f"Creating new user: {first_name} {last_name} with email {email_id}")
                result = create_user(first_name, last_name or "", email_id, mobile)
                if isinstance(result, dict) and 'error' in result:
                    return f"❌ Could not save your information: {result['error']}"
                
                return f"✅ Nice to meet you, {first_name}! I've saved your information. Your user ID is {result['user_id']}."
            else:
                return f"👋 Hello {first_name}! I'll need an email address to create your profile. For now, I'll just remember your name."
        
        # Not enough info
        return "I need at least your first name to help you further. Could you please introduce yourself?"
        
    except Exception as e:
        print(f"Error in handle_user_info: {str(e)}")
        return f"❌ An error occurred while processing your information: {str(e)}"

def navigate_user(entities):
    """
    Handle navigation commands (mock function - would be handled by frontend)
    """
    return f"🚀 Redirecting you to the {entities.get('page_to_navigate')} page..."

# ------------------ MAIN ROUTER ------------------

def extract_names_from_text(text):
    """Extract first and last name from a text greeting."""
    # Common patterns for name introductions
    patterns = [
        r"(?:I am|I'm|my name is|this is|hi I'm|hello I'm|hey I'm|it's|call me)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)",
        r"(?:I am|I'm|my name is|this is|hi I'm|hello I'm|hey I'm|it's|call me)\s+([A-Z][a-z]+)",
        r"(?:hi|hello|hey)\s+(?:guys|all|there)?,?\s+(?:I am|I'm|this is|it's)?\s*([A-Z][a-z]+)\s+([A-Z][a-z]+)",
        r"(?:hi|hello|hey)(?:\s+(?:guys|all|there)?)?,?\s+([A-Z][a-z]+)(?:\s+here)?",
        r"(?:name(?:'s|s|)\s+(?:is|:))\s+([A-Z][a-z]+)(?:\s+([A-Z][a-z]+))?",
        r"([A-Z][a-z]+)\s+([A-Z][a-z]+)(?:\s+here|speaking|is my name)"
    ]
    
    text = text.strip()
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 2 and groups[0] and groups[1]:
                return {"first_name": groups[0].capitalize(), "last_name": groups[1].capitalize()}
            elif len(groups) == 1 and groups[0]:
                # Look for last name after the first name
                first_name = groups[0].capitalize()
                remaining_text = text[text.lower().find(first_name.lower()) + len(first_name):].strip()
                words = remaining_text.split()
                if words and words[0][0].isupper():
                    return {"first_name": first_name, "last_name": words[0].capitalize()}
                return {"first_name": first_name, "last_name": ""}
    
    # Fallback: Just look for two capitalized words in sequence
    words = text.split()
    if len(words) >= 2:
        # Check for two capitalized words in sequence
        for i in range(len(words) - 1):
            if words[i][0].isupper() and words[i+1][0].isupper():
                return {"first_name": words[i].capitalize(), "last_name": words[i+1].capitalize()}
    
    return {}

def run_agent(user_query):
    # First, try direct pattern matching for common intents
    extracted_names = extract_names_from_text(user_query)
    print(f"Extracted names: {extracted_names}")
    
    # Pattern-based intent detection
    intent = "unknown"
    entities = {}
    
    # Simple pattern matching for common intents
    user_query_lower = user_query.lower()
    
    # Detect intent based on patterns first
    if any(phrase in user_query_lower for phrase in ["my name is", "i am", "i'm", "call me", "this is"]):
        intent = "provide_name"
        entities = extracted_names
    elif any(phrase in user_query_lower for phrase in ["find clinic", "search clinic", "dental clinic", "dentist", "find dentist"]):
        intent = "search_clinics"
        # Extract location/procedure if mentioned
        if "in" in user_query_lower:
            location_parts = user_query_lower.split("in")
            if len(location_parts) > 1:
                location = location_parts[1].strip().split()[0].capitalize()
                entities["location_city"] = location
    elif any(phrase in user_query_lower for phrase in ["book", "appointment", "schedule"]):
        intent = "book_appointment"
    elif any(phrase in user_query_lower for phrase in ["my booking", "my appointment", "check booking"]):
        intent = "view_bookings"
    elif any(phrase in user_query_lower for phrase in ["cancel booking", "cancel appointment"]):
        intent = "cancel_booking"
    else:
        # Try the LLM-based intent detection as a fallback
        try:
            intent_response = intent_chain.invoke(user_query)
            print(f"Raw intent response: {intent_response}")
            
            # Try to parse the JSON response
            try:
                intent_data = json.loads(intent_response)
                intent = intent_data.get("intent", "unknown")
                entities = intent_data.get("entities", {})
            except json.JSONDecodeError as json_err:
                print(f"JSON parsing error: {json_err}")
                # Fallback to name extraction if we can't parse the JSON
                if extracted_names:
                    intent = "provide_name"
                    entities = extracted_names
                else:
                    # If we can't detect any other intent, assume it's a medical question
                    intent = "faq_query"
        except Exception as e:
            print(f"Error in LLM intent detection: {str(e)}")
            # If LLM intent detection fails, fall back to RAG for medical questions
            if extracted_names:
                intent = "provide_name"
                entities = extracted_names
            else:
                intent = "faq_query"
    
    # Enhance entities with extracted names if appropriate
    if extracted_names and intent in ["provide_name", "book_appointment"] and not entities.get('first_name'):
        entities.update(extracted_names)
    
    print(f"Final intent: {intent}")
    print(f"Final entities: {entities}")
    
    # Route to appropriate handler
    if intent == "faq_query":
        return rag_chain.invoke(user_query)
    elif intent == "book_appointment":
        return handle_booking_creation(entities)
    elif intent == "search_clinics":
        return handle_search_clinics(entities)
    elif intent == "view_bookings":
        return handle_view_bookings(entities)
    elif intent == "cancel_booking":
        return handle_cancel_booking(entities)
    elif intent == "provide_name":
        if extracted_names:
            # Force extracted names into entities
            result = handle_user_info(extracted_names)
            return result
        return handle_user_info(entities)
    elif intent == "navigation_command":
        return navigate_user(entities)
    else:
        # Fallback to medical knowledge for unknown intents
        return rag_chain.invoke(user_query)

# ------------------ CLI Test Run ------------------

if __name__ == "__main__":
    print("CareEscapes Dental Tourism Chatbot")
    print("---------------------------------")
    print("You can ask about dental procedures, search for clinics, or manage your bookings.")
    print("Type 'exit' to quit.")
    print()
    
    # Mock user ID for testing
    test_user_id = str(uuid.uuid4())
    print(f"Using test user ID: {test_user_id}")
    
    while True:
        user_query = input("\n🧠 Ask something: ")
        if user_query.lower() == "exit":
            break
            
        result = run_agent(user_query)
        print(f"\n🧾 Response:\n{result}")



