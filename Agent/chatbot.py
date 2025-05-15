import os
import sys
from dotenv import load_dotenv
from openai import AzureOpenAI
from typing import Dict, Any, List, Tuple

# Add the current directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import tools
from Agent.tools import tools

# Load environment variables
load_dotenv()

# Azure OpenAI setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def detect_intent(user_input: str) -> Tuple[str, Dict[str, Any]]:
    """Use LLM to determine which tool to use and extract parameters."""
    # Construct a prompt to detect intent and extract parameters
    system_prompt = """You are a medical chatbot assistant. Analyze the user's query and determine which tool to use.
    Available tools:
    - faq: For general questions about medical topics
    - clinic_search: For finding clinics by location or specialty
    - service_search: For information about medical services
    - booking_search: For looking up existing appointments
    - booking_creation: For scheduling new appointments
    - price_comparison: For comparing costs of services
    
    Extract relevant parameters for the tool.
    Respond with a JSON object containing 'tool' and 'parameters'.
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Determine intent for: {user_input}"}
    ]
    
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages,
        response_format={"type": "json_object"}
    )
    
    try:
        result = eval(response.choices[0].message.content)
        return result.get("tool", "faq"), result.get("parameters", {})
    except:
        # Fallback to FAQ if parsing fails
        return "faq", {"query": user_input}

def chat_with_bot(user_input: str, conversation_history=None) -> Tuple[str, List[Dict[str, str]]]:
    """Main chatbot function that handles tool routing."""
    if conversation_history is None:
        conversation_history = [
            {"role": "system", "content": "You are a helpful medical assistant that can answer questions and help with clinic bookings."}
        ]
    
    # Add user input to conversation history
    conversation_history.append({"role": "user", "content": user_input})
    
    # Detect which tool to use
    tool_name, tool_params = detect_intent(user_input)
    
    # Execute the appropriate tool
    if tool_name in tools:
        tool_result = tools[tool_name].execute(tool_params)
        
        # Format tool result for the LLM
        tool_result_str = f"Tool '{tool_name}' executed with result: {tool_result}"
        
        # Ask LLM to generate a user-friendly response based on the tool result
        messages = conversation_history + [{"role": "system", "content": tool_result_str}]
        
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages
        )
        
        reply = response.choices[0].message.content
    else:
        # Fallback to general conversation if no tool matches
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=conversation_history
        )
        
        reply = response.choices[0].message.content
    
    # Add bot response to conversation history
    conversation_history.append({"role": "assistant", "content": reply})
    
    return reply, conversation_history

def get_bot_response(user_input: str, conversation_history=None) -> Tuple[str, List[Dict[str, str]]]:
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
        
        reply, conversation_history = chat_with_bot(user_input, conversation_history)
        print(f"Bot: {reply}\n")


