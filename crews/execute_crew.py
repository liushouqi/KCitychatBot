from crewai import Crew, Agent, Task, Process
from textwrap import dedent
from crewai.project import CrewBase, agent, task, crew
from tools.query_tools import QueryTool
import logging, re
logging.getLogger("opentelemetry.trace").setLevel(logging.ERROR)


@CrewBase
class ExecuteCrew:

    def __init__(self, cypher_query: str, url: str, user: str, password: str, dBname: str):
        self.cypher_query = cypher_query
        self.url = url
        self.user = user
        self.password = password
        self.dBname = dBname

    @agent
    def execute_agent(self) -> Agent:
        return Agent(
            role='Cypher Query Executor',
            goal='Execute cypher queries and return structured results',
            backstory="""As a Neo4j specialist, you excel at executing complex Cypher queries
                         and transforming results into structured formats""",
            verbose=True,
            llm=None
        )

    @task
    def execute_task(self) -> Task:
        return Task(
            description=dedent(f"The generated Cypher query is: {self.cypher_query}. Please execute this query against the Neo4j database using the available tool."),
            agent=self.execute_agent(),
            tools=[QueryTool
                   (cypher_query=self.cypher_query,
                    url=self.url,
                    user=self.user,
                    dbName=self.dBname,
                    password=self.password)
                    ],
            expected_output="Answers in Json format",
        )

    @crew
    def execute_crew(self) -> Crew:
        return Crew(
            agents=[self.execute_agent()],
            tasks=[self.execute_task()],
            process=Process.sequential,
            verbose=True
        )

    def process_string(self, input_str):
        """将Execute_Crew查询的Json格式转化为字符串，具体表现为：去除[]{}，单双引号前添加转义字符"""
        data = re.sub(r'[\[\]{}]', '', input_str)
        output_data = re.sub(r"[\"']", r'\"', data)
        return output_data
    
    def run(self):
        # 初始化crew并执行任务
        execute_crew = self.execute_crew()
        # result的类型为crewai.crews.crew_output.CrewOutput
        result_json = execute_crew.kickoff()
        result = self.process_string(result_json.raw)
        return  result


# 测试代码
if __name__ == '__main__':
    url = "bolt://localhost:7687"
    user = "neo4j"
    password = "lsq13733004201"
    database = "liu"
    query = "MATCH p=(b:Building)-[*]->(h) WHERE b.`gml:id` = 'bldg_050fa2a5-b390-44ce-88d5-ae4f83a5a056' AND ANY(r IN RELATIONSHIPS(p) WHERE TYPE(r) = 'measuredHeight' OR TYPE(r) = 'LocalityName') RETURN b.`gml:id`,h.`_text`"
    crew3 = ExecuteCrew(cypher_query=query,url=url,user=user,password=password,dBname=database)
    output_3 = crew3.run()
    print(output_3)
