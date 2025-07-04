from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from openai import OpenAI
from crews.input2cypher_crew import Input2CypherCrew
from crews.execute_crew import ExecuteCrew
from crews.generate_crew import GenerateCrew
from typing import List, Dict

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

class ChatFlow:
    def __init__(self):
        self.retry_count = 0  # 失败重试计数器
        self.chat_history: List[Dict[str, str]] = [{"role": "assistant", "content": "Hello! Please connect with database, then you can upload files or ask questions for me!"}]  # 存储对话历史，包含初始消息

    def process_inputs(self, input_text: str):
        """ 处理用户输入，包括识别问候语和执行查询 """
        self.chat_history.append({"role": "user", "content": input_text})  # 记录用户输入

        if self.is_greeting(input_text):
            output = self.answer_greeting(input_text)
        else:
            output = self.chatflow_run(input_text)
        self.chat_history.append({"role": "assistant", "content": output})  # 记录机器人输出
        return output

    def is_greeting(self, input_text: str) -> bool:
        greetings = ["你好", "早上好", "中午好", "下午好", "晚上好", "hello", "hi"]
        return any(greeting in input_text for greeting in greetings)

    def answer_greeting(self, input_text: str):
        """ 处理问候语并直接返回 """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful CityGML chatbot"},
                {"role": "user", "content": input_text},
            ],
            stream=False
        )
        return response.choices[0].message.content

    def chatflow_run(self, input_text: str):
        """ 执行完整的查询流程，并支持重试 """
        crew1 = Input2CypherCrew(input_text)
        query = crew1.run()

        crew2 = ExecuteCrew(f"生成的Cypher查询如下：{query}，请借助工具向Neo4j数据库执行查询")
        query_answer = crew2.run()

        if query_answer.startswith("查询失败"):
            self.retry_count += 1
            if self.retry_count < 3:
                print(f"Chatbot: 查询失败，正在重新尝试...(第 {self.retry_count} 次)")
                return self.chatflow_run(input_text)
            else:
                self.retry_count = 0
                return "经过多次尝试，查询仍然失败，请调整您的问题或稍后再试。"

        # 查询成功，生成自然语言结果
        self.retry_count = 0
        crew3 = GenerateCrew(f"输入问题为：{input_text}"
                                  f"你将接受到一个Json格式的输出结果：\n{query_answer}，请根据用户输入和系统输出，优化输出为符合人类语言习惯的英文输出，注意突出重点减少重复，控制输出内容在60个单词左右。")
        output = crew3.run()
        return output

app = FastAPI()

app.mount("/frontend", StaticFiles(directory="frontend"), name="fronted")

templates = Jinja2Templates(directory=".")

chat_flow = ChatFlow()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "chat_history": chat_flow.chat_history})

@app.post("/chat")
async def chat(user_input: str = Form(...)):
    output = chat_flow.process_inputs(user_input)
    return {"response": output}