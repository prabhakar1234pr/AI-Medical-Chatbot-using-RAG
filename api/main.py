# main.py - connecting to chatbot
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os

# Add the parent directory to path to allow importing chatbot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the chatbot function
try:
    from Agent.chatbot import get_bot_response
    CHATBOT_AVAILABLE = True
except ImportError:
    print("Warning: Could not import chatbot module. Using fallback responses.")
    CHATBOT_AVAILABLE = False

class SimpleHTTPHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def do_OPTIONS(self):
        self._set_headers()
        
    def do_GET(self):
        self._set_headers()
        if self.path == '/' or self.path == '/health':
            response = {"status": "healthy", "message": "Medical Chatbot API is running"}
        elif self.path == '/tools' and CHATBOT_AVAILABLE:
            response = {"tools": ["faq", "clinic_search", "service_search", "booking_search", "booking_creation", "price_comparison"]}
        else:
            response = {"status": "error", "message": "Endpoint not found"}
        
        self.wfile.write(json.dumps(response).encode())
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(post_data.decode('utf-8'))
        except:
            self._set_headers(400)
            self.wfile.write(json.dumps({"status": "error", "message": "Invalid JSON"}).encode())
            return
        
        self._set_headers()
        
        if self.path == '/chat':
            if CHATBOT_AVAILABLE:
                try:
                    # Get the last user message
                    if "messages" in request_data and len(request_data["messages"]) > 0:
                        last_message = request_data["messages"][-1]
                        if last_message["role"] == "user":
                            user_input = last_message["content"]
                            
                            # Convert previous messages to the format expected by chatbot
                            history = [{"role": msg["role"], "content": msg["content"]} 
                                      for msg in request_data["messages"][:-1]]
                            
                            # Call the chatbot
                            bot_response, updated_history, tool_used = get_bot_response(user_input, history)
                            
                            response = {
                                "response": bot_response,
                                "status": "success",
                                "session_id": "demo-123",
                                "tool_used": tool_used
                            }
                            
                        else:
                            response = {"status": "error", "message": "Last message must be from user"}
                    else:
                        response = {"status": "error", "message": "No messages provided"}
                except Exception as e:
                    print(f"Error calling chatbot: {str(e)}")
                    response = {
                        "response": "I encountered an issue with my AI brain. As a medical assistant, I'd be happy to help once I'm feeling better!",
                        "status": "success",
                        "session_id": "demo-123",
                        "tool_used": "error"
                    }
            else:
                # Fallback response if chatbot is not available
                response = {
                    "response": "I am a medical chatbot. How can I help you today?",
                    "status": "success",
                    "session_id": "demo-123",
                    "tool_used": "none"
                }
        else:
            response = {"status": "error", "message": "Endpoint not found"}
        
        self.wfile.write(json.dumps(response).encode())

def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPHandler)
    print(f'Server running at http://localhost:{port}/')
    print(f'Chatbot integration: {"AVAILABLE" if CHATBOT_AVAILABLE else "NOT AVAILABLE"}')
    httpd.serve_forever()

# This allows the script to be run directly
if __name__ == '__main__':
    run()
