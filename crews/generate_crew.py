from crewai import LLM
from dotenv import load_dotenv
from crewai.project import CrewBase,agent,task,crew
from crewai import Agent,Task,Crew,Process
from textwrap import dedent
import json
import os
import logging
logging.getLogger("opentelemetry.trace").setLevel(logging.ERROR)


# 读取环境变量
load_dotenv()
deepseek_llm = LLM(
    model="deepseek/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=1.3
)

@CrewBase
class GenerateCrew:

    def __init__(self,answer:str):
        self.answer=answer

    @agent
    def generate_agent(self) -> Agent:
        return Agent(
            role="Expert in natural language processing",
            goal="Transform structured data into natural language responses that are consistent with human reading habits",
            backstory="""You will receive a cypher query answer in json format, 
                         please generate the output based on the answer and question""",
            llm=deepseek_llm,
            verbose=True
        )

    @task
    def generate_task(self) -> Task:
        return Task(
            description=dedent(f"{self.answer}"),
            agent=self.generate_agent(),
            expected_output="Natural and fluent responses, using full sentence structure and avoiding direct copying of JSON keys",
        )

    @crew
    def generate_crew(self) -> Crew:
        return Crew(
            agents=[self.generate_agent()],
            tasks=[self.generate_task()],
            process=Process.sequential,
            verbose=True
        )

    def run(self):
        generate_crew = self.generate_crew()
        result = generate_crew.kickoff()
        return result.raw

# 测试代码
if __name__ == "__main__":
    with open("answer.json", "r") as f:
        output_3 = json.load(f)
        print(output_3)
        crew_4 = GenerateCrew(output_3)
        output_4 = crew_4.run()