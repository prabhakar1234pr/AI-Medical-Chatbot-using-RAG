# CareEscapes Healthcare Platform

A comprehensive healthcare platform that helps users find clinics, book appointments, and access medical knowledge through an AI-powered chatbot using RAG (Retrieval-Augmented Generation).

## Project Structure

- `/agent` - Contains the AI agent implementation for the medical knowledge chatbot
- `/api` - FastAPI backend that provides database access and chatbot integration
- `/db` - FAISS vector database storing document embeddings for medical knowledge
- `/data` - Contains the medical encyclopedia data
- `/frontend` - React frontend for the platform interface

## Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- Neon PostgreSQL database
- Groq API key

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Environment Setup

Create a `.env` file in the root directory with your Neon database connection and Groq API key:

```
# CareEscapes Environment Variables

# Neon PostgreSQL Database
DB_CONNECTION_STRING=postgresql://username:password@hostname:port/careescapes?sslmode=require

# Add your GROQ API key here
GROQ_API_KEY=your_groq_api_key
```

### 3. Backend Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### 1. Start the FastAPI Backend

```bash
# Option 1: Using the Python script
python run_api.py

# Option 2: Direct command
cd api
python main.py
```

The API server will run at http://localhost:8092

### 2. Start the React Frontend

```bash
cd frontend
npm start
```

The frontend will run at http://localhost:3000

## Database Information

The application uses a Neon PostgreSQL database with the following tables:
- users: Stores user account information
- clinics: Information about healthcare providers
- services: Medical services offered by clinics
- doctors: Doctor profiles linked to clinics and services
- bookings: Appointment bookings made by users
- reviews: User reviews of clinics and services
- payments: Payment records for bookings
- wishlists: User-saved favorite clinics/services

## API Endpoints

- `GET /` - Check if the API is running
- `POST /chat` - Send a message to the medical knowledge chatbot
- `GET /clinics` - Get list of available clinics
- `GET /clinics/{clinic_id}` - Get details of a specific clinic
- `GET /clinics/{clinic_id}/services` - Get services offered by a clinic
- `POST /bookings` - Create a new booking
- Additional endpoints for user management, doctor information, etc.

## Features

- Medical knowledge chatbot using RAG with FAISS and LangChain
- Clinic search and filtering
- Appointment booking and management
- User profiles and reviews
- Intent detection for routing user queries 