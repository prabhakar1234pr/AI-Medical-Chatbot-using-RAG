import os
import sys
from dotenv import load_dotenv
from typing import Dict, Any, List, Tuple
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate



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




