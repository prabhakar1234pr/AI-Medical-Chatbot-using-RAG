import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Azure OpenAI setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")
REDIS_URL = os.getenv("REDIS_URL")

def get_message_dicts(messages):
    """Convert LangChain messages to OpenAI-compatible format."""
    return [
        {"role": "system", "content": messages[0].content},
        *[
            {"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content}
            for m in messages[1:]
        ]
    ]

def chat_with_bot(user_input: str, chat_history: RedisChatMessageHistory) -> str:
    messages = [SystemMessage(content="You are a helpful medical assistant.")]
    messages += chat_history.messages
    messages.append(HumanMessage(content=user_input))

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=get_message_dicts(messages)
    )

    reply = response.choices[0].message.content

    # Update memory
    chat_history.add_user_message(user_input)
    chat_history.add_ai_message(reply)

    return reply

def get_bot_response(user_input: str, session_id: str = "api_user") -> str:
    """Function for API calls to get a response from the chatbot."""
    chat_history = RedisChatMessageHistory(session_id=session_id, url=REDIS_URL)
    return chat_with_bot(user_input, chat_history)

# Run CLI chat
if __name__ == "__main__":
    print("🩺 Medical Chatbot (type 'exit' to quit)")

    username = input("👤 What's your name? ").strip().lower().replace(" ", "_")
    chat_history = RedisChatMessageHistory(session_id=username, url=REDIS_URL)

    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            print("👋 Bye! Take care.")
            break
        reply = chat_with_bot(user_input, chat_history)
        print(f"Bot: {reply}\n")


