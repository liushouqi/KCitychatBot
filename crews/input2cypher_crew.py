from crewai import LLM
from crewai import Crew, Agent, Task, Process
from crewai.project import CrewBase, agent, task, crew
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from textwrap import dedent
from dotenv import load_dotenv
import os
from prompts import extract_example, cypher_example

# 读取环境变量
load_dotenv()
# deepseek-reasoner模型，收费更高但输出结果更好
deepseek_llm = LLM(
    model="deepseek/deepseek-reasoner",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=1.5
)

# 外部知识，参与Embedding模型
csv_source = CSVKnowledgeSource(
    file_paths=["labels_properties.csv", "regions.csv"]
)


@CrewBase
class Input2CypherCrew:

    def __init__(self, user_input:str):
        self.input = user_input

    @agent
    def extract_agent(self)->Agent:
        return Agent(
            role='Expert in semantics',
            goal='Extract intents, entities and attributes based on user input',
            backstory='''Some entities and their attributes will be provided as external knowledge.
            After learning some extract examples, you need to extract information from user input ''',
            llm=deepseek_llm,
            verbose=True
        )

    @agent
    def query_agent(self)->Agent:
        return Agent(
            role='Cypher expert',
            goal='Automatically generate cypher queries',
            backstory=''' Some cypher query examples will help you to generate right queries. 
               After that, try to generate new and credible cypher query based on input''',
            llm=deepseek_llm,
            verbose=True
        )

    @task
    def extract_task(self)->Task:
        return Task(
            description=dedent(extract_example+self.input),
            agent=self.extract_agent(),
            expected_output="Users' intents, node labels and attributes"
        )


    def query_task(self,extracted_inf)->Task:
        return Task(
            description=dedent(f"{cypher_example}\n{extracted_inf[-1]}"),
            agent=self.query_agent(),
            expected_output=" Only cypher query"
        )

    @crew
    def input2cypher_crew(self)->Crew:
        extract_task = self.extract_task()
        return Crew(
            agents=[self.extract_agent(),self.query_agent()],
            tasks=[extract_task, self.query_task([extract_task])],
            process=Process.sequential,
            knowledge_sources=[csv_source],
            verbose=True
        )

    def run(self):
       input2cypher_crew = self.input2cypher_crew()
       result = input2cypher_crew.kickoff()

       return  result.raw


# 测试代码
if __name__ == "__main__":
    print("欢迎来到CityGML对话机器人，输入你的问题！")
    user_inputs = input(dedent("Chatbot:"))
    crew1 = Input2CypherCrew(user_inputs)
    output_1 = crew1.run()
