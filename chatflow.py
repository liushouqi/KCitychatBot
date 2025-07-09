from textwrap import dedent
from dotenv import load_dotenv
import os
from openai import OpenAI
from crews.input2cypher_crew import Input2CypherCrew
from crews.execute_crew import ExecuteCrew
from crews.generate_crew import GenerateCrew
from typing import List, Dict, Tuple
from config import DBConfig

# 读取环境变量
load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

class ChatFlow:
    def __init__(self):
        self.retry_count = 0  # Retry counter for failed queries
        self.chat_history: List[Dict[str, str]] = [{"role": "assistant", "content": "Hello! Please connect to the database, then you can upload files or ask questions."}]  # Stores chat history, including initial message

    def process_inputs(self, input_text: str):
        """ Processes user input, including greeting detection and query execution. """
        self.chat_history.append({"role": "user", "content": input_text})  # Record user input

        if self.is_greeting(input_text):
            output = self.answer_greeting(input_text)
        else:
            output = self.chatflow_run(input_text)
        self.chat_history.append({"role": "assistant", "content": output})  # Record bot output
        return output

    def is_greeting(self, input_text: str) -> bool:
        greetings = ["你好", "早上好", "中午好", "下午好", "晚上好", "hello", "hi", "Hello", "Hi"]
        return any(greeting in input_text.lower() for greeting in greetings) # Convert input to lowercase for case-insensitive check

    def answer_greeting(self, input_text: str):
        """ Handles greetings and returns a direct response. """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful CityGML chatbot."},
                {"role": "user", "content": input_text},
            ],
            stream=False
        )
        return response.choices[0].message.content

    def chatflow_run(self, input_text: str):
        """ Executes the full query process with retry support. """
        crew1 = Input2CypherCrew(input_text)
        query = crew1.run()

        # Ensure the established Neo4j driver is used within ExecuteCrew
        crew2 = ExecuteCrew(
             cypher_query=query,
             url=DBConfig.url,
             user=DBConfig.user,
             password=DBConfig.password,
             dBname=DBConfig.dbName
            )
        query_answer = crew2.run()

        if query_answer.startswith("查询失败"):
            self.retry_count += 1
            if self.retry_count < 3:
                print(f"Chatbot: Query failed, retrying... (Attempt {self.retry_count})")
                return self.chatflow_run(input_text) # Recursive retry
            else:
                self.retry_count = 0
                return "Multiple attempts to query failed. Please adjust your question or try again later."

        # If query is successful, generate natural language result
        self.retry_count = 0
        crew3 = GenerateCrew(f"The input question was: {input_text}\nYou will receive a JSON formatted output: \n{query_answer}. Please optimize the output into human-readable English, focusing on key points, reducing redundancy, and keeping the content around 60 words.")
        output = crew3.run()
        return output

if __name__ == "__main__":
    chat_flow = ChatFlow()  # 机器人实例，保持对话上下文
    print("欢迎使用CityGML聊天机器人! 输入'q'退出")
    while True:
        user_input = input(dedent("Chatbot: "))
        if user_input.lower() == 'q':
            print("Chatbot: 感谢使用！再见！")
            break
        chat_flow.process_inputs(user_input)
