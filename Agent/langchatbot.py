import os
import sys
from dotenv import load_dotenv
from typing import Dict, Any, List, Tuple
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field
from langchain.chains import LLMChain

# Add the current directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import tools
from Agent.tools import tools

# Load environment variables
load_dotenv()

class ToolResponse(BaseModel):
    """Schema for the tool response"""
    tool: str = Field(description="The selected tool to use")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool")
    response: str = Field(description="The response to the user")

    model_config = {
        "arbitrary_types_allowed": True
    }

# Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-8b-8192",
    temperature=0.7,
    max_tokens=1024
)

# Create the prompt template
template = """You are a medical chatbot assistant. Analyze the user's query and determine which tool to use.
Available tools:
- faq: For general questions about medical topics
- clinic_search: For finding clinics by location or specialty
- service_search: For information about medical services
- booking_search: For looking up existing appointments
- booking_creation: For scheduling new appointments
- price_comparison: For comparing costs of services

User query: {input}

First determine the tool and parameters, then execute the tool and provide a user-friendly response.
Respond with a JSON object in this EXACT format:
{{
    "tool": "tool_name",
    "parameters": {{"param1": "value1"}},
    "response": "Your response as a simple string, not a nested object"
}}

Example response:
{{
    "tool": "faq",
    "parameters": {{"query": "general health"}},
    "response": "Here's some general health information..."
}}"""

prompt = ChatPromptTemplate.from_template(template)

# Create output parser
output_parser = PydanticOutputParser(pydantic_object=ToolResponse)

# Create the chain
chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True
)

def chat_with_bot(user_input: str, conversation_history=None) -> Tuple[str, List[Dict[str, str]], str]:
    """Main chatbot function that handles tool routing using LangChain."""
    if conversation_history is None:
        conversation_history = [
            {"role": "system", "content": "You are a helpful medical assistant that can answer questions and help with clinic bookings."}
        ]
    
    # Add user input to conversation history
    conversation_history.append({"role": "user", "content": user_input})
    
    print(f"\n--- INTENT DETECTION FOR: '{user_input}' ---")
    
    # Execute the chain
    result = chain.run(input=user_input)
    print(f"LLM DECISION:\n{result}\n")
    
    try:
        # Parse the result
        tool_response = output_parser.parse(result)
        selected_tool = tool_response.tool
        params = tool_response.parameters
        print(f"TOOL SELECTED: {selected_tool}")
        print(f"PARAMETERS: {params}")
        print(f"--- END INTENT DETECTION ---\n")
        
        # Execute the tool if it exists
        if selected_tool in tools:
            tool_result = tools[selected_tool].execute(params)
            reply = f"Based on the {selected_tool} tool results: {tool_result}"
        else:
            reply = tool_response.response
            
    except Exception as e:
        # Fallback to FAQ if parsing fails
        print(f"ERROR PARSING LLM RESPONSE: {str(e)}")
        print(f"FALLBACK TO: faq")
        print(f"--- END INTENT DETECTION ---\n")
        selected_tool = "faq"
        params = {"query": user_input}
        reply = "I apologize, but I couldn't process your request properly."
    
    # Add bot response to conversation history
    conversation_history.append({"role": "assistant", "content": reply})
    
    return reply, conversation_history, selected_tool

def get_bot_response(user_input: str, conversation_history=None) -> Tuple[str, List[Dict[str, str]], str]:
    """Function for API calls to get a response from the chatbot."""
    return chat_with_bot(user_input, conversation_history)

# Run CLI chat
if __name__ == "__main__":
    print("🩺 Medical Chatbot (type 'exit' to quit)")
    
    # Initialize conversation history
    conversation_history = [
        {"role": "system", "content": "You are a helpful medical assistant that can answer questions and help with clinic bookings."}
    ]
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            print("👋 Bye! Take care.")
            break
        
        reply, conversation_history, tool_name = chat_with_bot(user_input, conversation_history)
        print(f"Bot: {reply}\n")


