from fastapi import FastAPI, Request, Form, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from openai import OpenAI
from chatflow import ChatFlow
from pydantic import BaseModel
from load.db_connector import initialize_driver, close_driver, test_neo4j_connection
from config import DBConfig
from typing import List, Dict
import load.gml_processor as gml_processor
import asyncio
from contextlib import asynccontextmanager


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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行的代码 (这里不需要)
    print("Application startup.")
    yield
    # 应用关闭时执行的代码
    print("Application shutdown.")
    close_driver()

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json({"type": "progress", "message": message})

manager = ConnectionManager()

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
        test_neo4j_connection(details.url, details.user, details.password)
        initialize_driver(details.url, details.user, details.password)
        # store database information in the backend
        DBConfig.url = details.url
        DBConfig.user = details.user
        DBConfig.password = details.password
        DBConfig.dbName = details.dbName
        return JSONResponse(content={'success': True, 'message': 'Connection successful'})
    except Exception as e:
        # Return detailed failure message
        return JSONResponse(content={'success': False, 'message': f'Connection failed: {str(e)}'}, status_code=500)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # 保持连接打开，可以用于双向通信，但这里主要用于后端向前端推送
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.post("/upload/{client_id}")
async def upload_gml_files(client_id: str, files: List[UploadFile] = File(...)):
    if not DBConfig.dbName:
        await manager.send_personal_message("The database is not connected. Please connect to the database first before uploading files.", client_id)
        return JSONResponse(status_code=400, content={"message": "Database not connected"})

    # 在后台任务中处理文件，以免阻塞HTTP响应
    # FastAPI会自动处理这个，直接await即可
    for file in files:
        await manager.send_personal_message(f"Start processing the file: {file.filename}", client_id)
        content = await file.read()
        # 将 manager 和 client_id 传递给处理函数，以便它可以发送回馈消息
        asyncio.create_task(
            gml_processor.process_uploaded_gml_file(
                original_filename=file.filename,
                file_content=content,
                dbname=DBConfig.dbName,
                manager=manager,
                client_id=client_id
            )
        )
    return JSONResponse(content={"message": f"The file upload request has been received and is being processed... Please check the progress in the chat box."})