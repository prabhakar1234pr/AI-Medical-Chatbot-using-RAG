from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database URL - Allow environment variable override
DB_CONNECTION_STRING = os.getenv(
    "DB_CONNECTION_STRING", 
    "postgresql://pgadmin:admin@localhost:5432/careescapes"
)

# Print connection info (remove in production)
# Mask password in log output for security
connection_string_safe = DB_CONNECTION_STRING.replace(
    DB_CONNECTION_STRING.split(":", 2)[2].split("@")[0], 
    "****"
) if "@" in DB_CONNECTION_STRING else DB_CONNECTION_STRING
print(f"Connecting to database: {connection_string_safe}")

# Create SQLAlchemy engine
engine = create_engine(DB_CONNECTION_STRING)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
metadata = MetaData()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 