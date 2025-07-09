from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from openai import OpenAI
from chatflow import ChatFlow
from pydantic import BaseModel
from load.db_connector import connect_test
from config import DBConfig

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Define the request body model for database connection details
class ConnectionDetails(BaseModel):
    url: str
    user: str
    dbName: str
    password: str

app = FastAPI() # Pass the lifespan context manager to FastAPI

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

templates = Jinja2Templates(directory=".")

chat_flow = ChatFlow()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "chat_history": chat_flow.chat_history})

@app.post("/chat")
async def chat(user_input: str = Form(...)):
    # Directly call chat_flow's process_inputs method
    output = chat_flow.process_inputs(user_input)
    return {"response": output}

@app.post("/connect_database", response_class=JSONResponse)
async def connect_database_api(details: ConnectionDetails):
    """
    Handles database connection requests from the frontend, calling connect_test.
    """
    try:
        connect_test(details.url, details.user, details.password)
        # store database information in the backend
        DBConfig.url = details.url
        DBConfig.user = details.user
        DBConfig.password = details.password
        DBConfig.dbName = details.dbName

        return JSONResponse(content={'success': True, 'message': 'Connection successful'})
    except Exception as e:
        # Return detailed failure message
        return JSONResponse(content={'success': False, 'message': f'Connection failed: {str(e)}'}, status_code=500)
