FROM python:3.9-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY Agent/ ./Agent/
COPY api/ ./api/

# Make sure we have the __init__.py file for the Agent package
RUN mkdir -p Agent
RUN touch Agent/__init__.py

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app

# Run the FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 