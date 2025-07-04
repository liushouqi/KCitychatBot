create_query = """
//读取文件创建根节点
CALL apoc.load.xml($file_path) YIELD value
UNWIND apoc.map.removeKey(value, '_children') AS cityModel
CALL apoc.create.node([cityModel._type],{type:cityModel._type})
YIELD node  AS root
SET root += apoc.map.removeKey(cityModel,'_type')

WITH value,root
UNWIND value._children as one_child

//第二层节点
WITH one_child,root
UNWIND apoc.map.removeKey(one_child, '_children') AS oneth
CALL apoc.create.node([oneth._type],{type:oneth._type})
YIELD node  AS one
SET one += apoc.map.removeKey(oneth,'_type')
//添加关系
WITH root, one_child, one 
CALL apoc.create.relationship(root, one_child._type, {}, one) YIELD rel


//第三层节点
WITH one_child,one
UNWIND one_child._children AS two_child
UNWIND apoc.map.removeKey(two_child, '_children') AS twoth
CALL apoc.create.node([twoth._type],{type:twoth._type})
YIELD node  AS two
SET two += apoc.map.removeKey(twoth,'_type')
SET two.region = $region
//添加关系
WITH one, two_child, two 
CALL apoc.create.relationship(one, two_child._type, {}, two) YIELD rel


//第四层节点
WITH two_child,two
UNWIND two_child._children AS three_child
UNWIND apoc.map.removeKey(three_child, '_children') AS threeth
CALL apoc.create.node([threeth._type],{type:threeth._type})
YIELD node  AS three
SET three += apoc.map.removeKey(threeth,'_type')
//添加关系
WITH two, three_child, three 
CALL apoc.create.relationship(two, three_child._type, {}, three) YIELD rel


//第五层节点
WITH three_child,three
UNWIND three_child._children AS four_child
UNWIND apoc.map.removeKey(four_child, '_children') AS fouth
CALL apoc.create.node([fouth._type],{type:fouth._type})
YIELD node  AS four
SET four += apoc.map.removeKey(fouth,'_type')
//添加关系
WITH three, four_child, four 
CALL apoc.create.relationship(three, four_child._type, {}, four) YIELD rel


//第六层节点
WITH four_child,four
UNWIND four_child._children AS five_child
UNWIND apoc.map.removeKey(five_child, '_children') AS fifth
CALL apoc.create.node([fifth._type],{type:fifth._type})
YIELD node  AS five
SET five += apoc.map.removeKey(fifth,'_type')
//添加关系
WITH four, five_child, five 
CALL apoc.create.relationship(four, five_child._type, {}, five) YIELD rel


//第七层节点
WITH five_child,five
UNWIND five_child._children AS six_child
UNWIND apoc.map.removeKey(six_child, '_children') AS sixth
CALL apoc.create.node([sixth._type],{type:sixth._type})
YIELD node  AS six
SET six += apoc.map.removeKey(sixth,'_type')
//添加关系
WITH five, six_child, six
CALL apoc.create.relationship(five, six_child._type, {}, six) YIELD rel


//第八层节点
WITH six_child,six
UNWIND six_child._children AS seven_child
UNWIND apoc.map.removeKey(seven_child, '_children') AS seventh
CALL apoc.create.node([seventh._type],{type:seventh._type})
YIELD node  AS seven
SET seven += apoc.map.removeKey(seventh,'_type')
//添加关系
WITH six, seven_child, seven
CALL apoc.create.relationship(six, seven_child._type, {}, seven) YIELD rel


//第九层节点
WITH seven_child,seven
UNWIND seven_child._children AS eight_child
UNWIND apoc.map.removeKey(eight_child, '_children') AS eighth
CALL apoc.create.node([eighth._type],{type:eighth._type})
YIELD node  AS eight
SET eight += apoc.map.removeKey(eighth,'_type')
//添加关系
WITH seven, eight_child, eight
CALL apoc.create.relationship(seven, eight_child._type, {}, eight) YIELD rel


//第十层节点
WITH eight_child,eight
UNWIND eight_child._children AS nine_child
UNWIND apoc.map.removeKey(nine_child, '_children') AS nineth
CALL apoc.create.node([nineth._type],{type:nineth._type})
YIELD node  AS nine
SET nine += apoc.map.removeKey(nineth,'_type')
//添加关系
WITH eight, nine_child, nine
CALL apoc.create.relationship(eight, nine_child._type, {}, nine) YIELD rel


//第十一层节点
WITH nine_child, nine
UNWIND nine_child._children AS ten_child
UNWIND apoc.map.removeKey(ten_child, '_children') AS tenth
CALL apoc.create.node([tenth._type],{type:tenth._type})
YIELD node AS ten
SET ten += apoc.map.removeKey(tenth, '_type')
//添加关系
WITH nine, ten_child, ten
CALL apoc.create.relationship(nine, ten_child._type, {}, ten) YIELD rel


//第十二层节点
WITH ten_child, ten
UNWIND ten_child._children AS eleven_child
UNWIND apoc.map.removeKey(eleven_child, '_children') AS eleventh
CALL apoc.create.node([eleventh._type],{type:eleventh._type})
YIELD node AS eleven
SET eleven += apoc.map.removeKey(eleventh, '_type')
//添加关系
WITH ten, eleven_child, eleven
CALL apoc.create.relationship(ten, eleven_child._type, {}, eleven) YIELD rel


//第十三层节点
WITH eleven_child, eleven
UNWIND eleven_child._children AS twelve_child
UNWIND apoc.map.removeKey(twelve_child, '_children') AS twelfth
CALL apoc.create.node([twelfth._type], {type:twelfth._type})
YIELD node AS twelve
SET twelve += apoc.map.removeKey(twelfth, '_type')
//添加关系
WITH eleven, twelve_child, twelve
CALL apoc.create.relationship(eleven, twelve_child._type, {}, twelve) YIELD rel


//第十四层节点
WITH twelve_child, twelve
UNWIND twelve_child._children AS thirteen_child
UNWIND apoc.map.removeKey(thirteen_child, '_children') AS thirteenth
CALL apoc.create.node([thirteenth._type], {type:thirteenth._type})
YIELD node AS thirteen
SET thirteen += apoc.map.removeKey(thirteenth, '_type')
//添加关系
WITH twelve, thirteen_child, thirteen
CALL apoc.create.relationship(twelve, thirteen_child._type, {}, thirteen) YIELD rel


//第十五层节点
WITH thirteen_child, thirteen
UNWIND thirteen_child._children AS fourteen_child
UNWIND apoc.map.removeKey(fourteen_child, '_children') AS fourteenth
CALL apoc.create.node([fourteenth._type], {type:fourteenth._type})
YIELD node AS fourteen
SET fourteen += apoc.map.removeKey(fourteenth, '_type')
//添加关系
WITH thirteen, fourteen_child, fourteen
CALL apoc.create.relationship(thirteen, fourteen_child._type, {}, fourteen) YIELD rel


//第十六层节点
WITH fourteen_child, fourteen
UNWIND fourteen_child._children AS fifteen_child
UNWIND apoc.map.removeKey(fifteen_child, '_children') AS fifteenth
CALL apoc.create.node([fifteenth._type], {type:fifteenth._type})
YIELD node AS fifteen
SET fifteen += apoc.map.removeKey(fifteenth, '_type')
//添加关系
WITH fourteen, fifteen_child, fifteen
CALL apoc.create.relationship(fourteen, fifteen_child._type, {}, fifteen) YIELD rel


RETURN null
"""

add_rel = """
//如果想要在创建节点后就建立Real_Clas关系，建议为create_query中CityModel添加绝对路径，然后在这个步骤中根据相对路径检索确定CityModel
MATCH p=(m:CityModel)-[*]->(child)
WHERE child.codeSpace IS NOT NULL
WITH child, replace(split(child.codeSpace, 'codelists/')[1],'.xml', '') AS class_name, child._text AS class_num
MATCH q=(n:name)<-[*]-(d:Dictionary)
WHERE n.`_text`=class_name
MATCH r=(d)-[*]->(num:name)
WHERE num.`_text`=class_num
MATCH (num)-[*2]-(des:description)
MERGE (child)-[:Real_Class]-(des)
"""