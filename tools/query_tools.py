from neo4j import GraphDatabase
from crewai.tools import BaseTool


class QueryTool(BaseTool):

    name: str = 'Query tool'
    description: str = 'Get a cypher query and return answers'

    def _run(self,cypher_query:str)->list:
        uri = "bolt://localhost:7687"
        auth = ("neo4j", "lsq13733004201")
        dbname = "liu"

        try:
            with GraphDatabase.driver(uri, auth=auth) as driver:
                driver.verify_connectivity()  # 验证连接
                with driver.session(database=dbname) as session:
                    records = session.run(cypher_query)  # 执行查询
                    records_list = [dict(record) for record in records]

                    if not records_list:
                        raise ValueError("查询未返回任何结果，请检查Cypher语句或数据库内容")

                    return records_list

        except Exception as e:
            return [f"查询失败：{str(e)}"]

# 测试代码
if __name__ == "__main__":
    # 实例化
    query = QueryTool()
    # cypher_query =  """
    #                 MATCH p=(r:Road)-[*]->(child)
    #                 WHERE r.`gml:id`= 'tran_585935ae-aab9-4c7f-9fa2-2b90ceeb0b0f'
    #                 AND child.codeSpace IS NOT NULL
    #                 WITH child, replace(split(child.codeSpace, 'codelists/')[1],'.xml', '') AS class_name, child._text AS class_num
    #                 MATCH q=(n:name)<-[*]-(d:Dictionary)
    #                 WHERE n.`_text`=class_name
    #                 MATCH r=(d)-[*]->(num:name)
    #                 WHERE num.`_text`=class_num
    #                 MATCH (num)-[*2]-(des:description)
    #                 RETURN class_name,class_num,des.`_text`
    #                 """
    # 调用
    cypher_query = "MATCH p=(b:Building) WHERE b.`gml:id` = 'bldg_050fa2a5-b390-44ce-88d5-ae4f83a5a055' RETURN b"
    result = query._run(cypher_query)
    print(result)