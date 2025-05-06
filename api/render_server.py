"""
Simplified server file for Render deployment
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers (assuming these exist in your project)
try:
    from .routers import clinics, bookings, users
    ROUTERS_AVAILABLE = True
except ImportError:
    ROUTERS_AVAILABLE = False
    print("Warning: Router modules not found. Only basic endpoints will be available.")

# Check for database connection
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
if not DB_CONNECTION_STRING:
    print("WARNING: No DB_CONNECTION_STRING environment variable found.")
    print("Database functionality will not work correctly.")
else:
    # Mask the password in logs
    masked_conn = DB_CONNECTION_STRING.replace(
        DB_CONNECTION_STRING.split(":", 2)[2].split("@")[0], 
        "****"
    ) if "@" in DB_CONNECTION_STRING else DB_CONNECTION_STRING
    print(f"Database connection string configured: {masked_conn}")

# Create FastAPI app
app = FastAPI(
    title="CareEscapes API",
    description="API for healthcare booking platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers if available
if ROUTERS_AVAILABLE:
    app.include_router(clinics.router)
    app.include_router(bookings.router)
    app.include_router(users.router)

@app.get("/")
async def root():
    # Check database connection status
    db_status = "Configured" if DB_CONNECTION_STRING else "Not configured"
    
    return {
        "message": "Welcome to the CareEscapes API",
        "database_status": db_status,
        "environment": "Render" if os.getenv("RENDER") else "Development",
        "routers_loaded": ROUTERS_AVAILABLE
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    port = int(os.getenv("PORT", 8092))
    uvicorn.run("render_server:app", host="0.0.0.0", port=port, reload=False) 