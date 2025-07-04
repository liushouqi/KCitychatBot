# 下面为大模型的提示词

extract_example = """
根据labels_properties.json中提供的实体及属性，并仿照下面的示例解析用户输入的语句，提取出用户意图，节点标签和属性。
示例如下：
示例1：
Input：What is the height and location of the building with gml:id = 'bldg_050fa2a5-b390-44ce-88d5-ae4f83a5a056'?
Output：
Extract intent: Query height and location of a specific building,labels: Building, properties: height - `measuredHeight`, location - `LocalityName`, `gml:id`:'bldg_050fa2a5-b390-44ce-88d5-ae4f83a5a056'.

示例2：
Input：What is the average building height in the Fengdao region?
Output：
Extract intent: Calculate average height of buildings in Fengdao region,labels: Building, properties: height - `measuredHeight`, `region`:Fengdao.

示例3：
Input：Please tell me all the information about the road named '首都高速5号池袋線'
Output：
Extract intent: Get all the information of a specific road, labels: Road, name, properties: `_text`.

输入问题为：
"""

cypher_example="""
根据提取的实体关系，自动生成Cypher查询语句，下面是4个示例，在我的示例中：Cypher语句是一整条完整的、不存在换行，请保留这种格式。
示例1：
Input：
Extract intent: Query height and location of a specific building, 
labels: Building, properties: height - `measuredHeight`, location - `LocalityName`, `gml:id`:'bldg_050fa2a5-b390-44ce-88d5-ae4f83a5a056'.
Output：
MATCH p=(b:Building)-[*]->(h) WHERE b.`gml:id` = 'bldg_050fa2a5-b390-44ce-88d5-ae4f83a5a056' AND ANY(r IN RELATIONSHIPS(p) WHERE TYPE(r) = 'measuredHeight' OR TYPE(r) = 'LocalityName') RETURN b.`gml:id`,h.`_text`

示例2：
Input：
Extract intent: Calculate average height of buildings in Fengdao region, 
labels: Building, properties: height - `measuredHeight`, `region`:Fengdao.
Output：
MATCH p=(b:Building)-[*]->(h) WHERE b.region=~ '.*丰岛区' AND ANY(r IN RELATIONSHIPS(p) WHERE TYPE(r) = 'measuredHeight') RETURN COUNT(b) AS building_count,AVG(toFloat(h.`_text`)) AS aver_height

示例3：
Input:
Extract intent: Get all the information of a specific road, labels: Road, name, properties: `_text`.
Output:
MATCH p=(w:Road)-[:name]->(h) WHERE h.`_text`= '首都高速5号池袋線' OPTIONAL MATCH (w)-[*]->(child1) WHERE child1.codeSpace IS NOT NULL WITH w, child1, replace(split(child1.codeSpace, 'codelists/')[1], '.xml', '') AS class_name, child1._text AS class_num OPTIONAL MATCH (n:name)<-[*]-(d:Dictionary)-[*]->(num:name) WHERE n.`_text` = class_name AND num.`_text` = class_num OPTIONAL MATCH (num)-[*2]-(des:description) WITH w, COLLECT(DISTINCT {class_name: class_name, class_num: class_num, description: des.`_text`}) AS details OPTIONAL MATCH (w)-[*1..3]->(child2) WHERE child2.codeSpace IS NULL AND child2._text IS NOT NULL WITH w, details, COLLECT(DISTINCT child2) AS child2_list RETURN w, details, child2_list LIMIT 1

"""
