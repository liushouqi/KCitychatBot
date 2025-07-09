from neo4j import GraphDatabase
from crewai.tools import BaseTool


class QueryTool(BaseTool):

    name: str = 'Query tool'
    description: str = 'Get a cypher query and return answers'
    url: str
    user: str
    dbName: str
    password: str
    cypher_query: str

    def _run(self, *args, **kwargs)->list:
        uri = self.url
        auth = (self.user, self.password)
        dNname = self.dbName
        cypher_query = self.cypher_query

        try:
            with GraphDatabase.driver(uri, auth=auth) as driver:
                driver.verify_connectivity()  # 验证连接
                with driver.session(database=dNname) as session:
                    records = session.run(cypher_query)  # 执行查询
                    records_list = [dict(record) for record in records]

                    if not records_list:
                        raise ValueError("查询未返回任何结果，请检查Cypher语句或数据库内容")

                    return records_list

        except Exception as e:
            return [f"查询失败：{str(e)}"]
        

# 测试代码
if __name__ == "__main__":
    query = "MATCH p=(b:Bridge) WHERE b.`gml:id` = 'brid_d25793e6-d162-4277-9c44-9db12e841d9a' RETURN b"
    my_query = QueryTool(url = "bolt://localhost:7687", user = "neo4j", password = "lsq13733004201", dbName="liu", cypher_query=query)
    result = my_query._run()
    print(result)