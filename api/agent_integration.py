"""
Example of how to integrate the CareEscapes DB API with your LangChain agent.
This demonstrates how to add the database tools to your existing LangChain setup.
"""

from langchain.agents import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import json

# Import our connector functions
from connector import search_clinics, create_booking, get_user_bookings, cancel_booking

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Define tools for database actions
db_tools = [
    Tool(
        name="SearchClinics",
        func=lambda query: json.dumps(search_clinics(**query)),
        description="Search for dental clinics by location, procedure name, or max price. Input should be a JSON with the keys 'location_city', 'procedure_name', and/or 'max_price'."
    ),
    Tool(
        name="CreateBooking",
        func=lambda query: json.dumps(create_booking(**query)),
        description="Create a booking for a dental procedure. Input should be a JSON with the keys 'user_id', 'clinic_id', 'service_id', 'doctor_id' (optional), and 'appointment_startdate' (in ISO format)."
    ),
    Tool(
        name="GetUserBookings",
        func=lambda user_id: json.dumps(get_user_bookings(user_id)),
        description="Get all bookings for a user. Input should be the user_id as a string."
    ),
    Tool(
        name="CancelBooking",
        func=lambda booking_id: json.dumps(cancel_booking(booking_id)),
        description="Cancel a booking. Input should be the booking_id as a string."
    )
]

# Define your LLM (using Groq)
llm = ChatGroq(
    temperature=0,
    model_name="llama3-70b-8192",
    groq_api_key=GROQ_API_KEY
)

# Create the agent prompt template
prompt = PromptTemplate.from_template(
    """You are an AI assistant for CareEscapes, a dental tourism platform. 
    You can answer medical questions using your knowledge base, but you can also help users
    search for clinics, book appointments, check their bookings, and cancel appointments.
    
    When helping with bookings, first search for clinics that match the user's needs,
    then help them book an appointment with their chosen clinic.
    
    {tools}
    
    When using the tools, make sure to parse the JSON results properly and present them
    in a user-friendly way.
    
    Human: {input}
    Agent: {agent_scratchpad}
    """
)

# Create the agent
agent = create_react_agent(llm, db_tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=db_tools, verbose=True)

# Example usage
if __name__ == "__main__":
    # Run this file directly to test the agent
    print("CareEscapes Agent Example")
    print("Ask about dental procedures, or try to search for clinics and book appointments.")
    print("Type 'exit' to quit.")
    print()
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        result = agent_executor.invoke({"input": user_input})
        print(f"Agent: {result['output']}") 