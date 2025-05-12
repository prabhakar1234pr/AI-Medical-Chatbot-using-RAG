from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from Agent.chatbot import get_bot_response

load_dotenv()  # Load environment variables from .env

server = os.getenv("AZURE_SQL_SERVER")
database = os.getenv("AZURE_SQL_DATABASE")
username = os.getenv("AZURE_SQL_USERNAME")
password = os.getenv("AZURE_SQL_PASSWORD")
driver = os.getenv("AZURE_SQL_DRIVER", "ODBC+Driver+17+for+SQL+Server").replace(" ", "+")

connection_string = f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}?driver={driver}"

app = FastAPI()

try:
    engine = create_engine(connection_string)
except Exception as e:
    print(f"Warning: Database connection failed - {str(e)}")
    engine = None

@app.get("/")
def root():
    return {"message": "Welcome to the Medical Chatbot API"}

@app.get("/bookings")
def read_bookings():
    if not engine:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM bookings"))
        bookings = [dict(row._mapping) for row in result]
        return {"bookings": bookings}

class ChatRequest(BaseModel):
    user_input: str
    session_id: str = "default_user"

@app.post("/chat")
def chat_with_bot(request: ChatRequest):
    try:
        reply = get_bot_response(request.user_input, request.session_id)
        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))