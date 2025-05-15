@echo off
echo Starting Medical Chatbot Demo...

echo Activating virtual environment...
call .\chatbot_env\Scripts\activate

echo Starting backend server...
start cmd /k "cd api; uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting frontend...
start cmd /k "cd medical-chatbot-frontend; npm start"

echo Both servers are starting. Frontend will be available at http://localhost:3000 
echo Backend will be available at http://localhost:8000
echo.
echo IMPORTANT: Make sure you've created a .env file with your Azure OpenAI credentials
echo See .env.example for the required format
echo. 