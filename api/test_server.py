from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    print("GET / endpoint called")
    return {"status": "online", "message": "Test server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080) 