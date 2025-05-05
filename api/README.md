# CareEscapes API Extension

This extension adds PostgreSQL database integration and booking functionality to the CareEscapes medical chatbot.

## Components

1. **FastAPI Backend**: REST API for clinic search and appointment booking
2. **PostgreSQL Database**: Stores users, clinics, services, and bookings
3. **LangChain Integration**: Connects the existing RAG chatbot to database operations

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start PostgreSQL Database

Make sure Docker is installed on your system, then run:

```bash
cd Docker
docker-compose up -d
```

This will start a PostgreSQL database with the schema already configured.

### 3. Run the API Server

```bash
python -m api.db_server
```

The server will run on http://localhost:8092 with Swagger documentation available at http://localhost:8092/docs

### 4. Integrate with LangChain Agent

Use the `connector.py` module in your LangChain agent to connect to the API. See `agent_integration.py` for an example.

## API Endpoints

### Clinics

- `GET /clinics/search` - Search for clinics with filters for location, procedure name, and price

### Bookings

- `POST /bookings/` - Create a new booking
- `GET /bookings/{user_id}` - Get all bookings for a user
- `DELETE /bookings/{booking_id}` - Cancel a booking

## Architecture

```
┌────────────┐       ┌───────────┐       ┌───────────┐
│  LangChain │       │  FastAPI  │       │ PostgreSQL│
│   Agent    │◄─────►│  Backend  │◄─────►│ Database  │
└────────────┘       └───────────┘       └───────────┘
     │                                         ▲
     │                                         │
     ▼                                         │
┌────────────┐                           ┌─────┴─────┐
│ RAG System │                           │  Docker   │
└────────────┘                           └───────────┘
```

## Example Usage

For examples of how to use this API with your LangChain agent, see `agent_integration.py`. 