from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas import EvaluationDataset
from ragas.metrics import Faithfulness,AnswerRelevancy,ContextRelevance
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import pandas as pd

# 设置嵌入模型
load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo")
embeddings = OpenAIEmbeddings()

# 导入评价数据集
dataset = []

# 评价表示例，query、response列表中存储字符串，retrieved_contexts存储上下文构成的子列表
"""
query = ["丰岛区最高的建筑物在什么位置？","丰岛区建筑物的平均高度是多少？"]
response = ["丰岛区最高的建筑物位于东京都丰岛区东池袋三丁目，该建筑物高度为234.1米。","丰岛区共有108,943栋建筑物，这些建筑物的平均高度约为10.5米。"]
retrieved_contexts = [["\"b\":\"identity\":371035736,\"labels\":\"Building\",\"properties\":\"gml:id\":\"bldg_ac8d4b0e-6f5b-4caf-b9c8-9af3a82685ac\",\"type\":\"Building\",\"region\":\"1丰岛区\",\"elementId\":\"4:be6dcfeb-90a4-4ae6-b3aa-1ccc9172af42:371035736\",\"h\":\"identity\":371138349,\"labels\":\"measuredHeight\",\"properties\":\"uom\":\"m\",\"type\":\"measuredHeight\",\"_text\":\"234.1\",\"elementId\":\"4:be6dcfeb-90a4-4ae6-b3aa-1ccc9172af42:371138349\",\"ln\":\"identity\":372593781,\"labels\":\"LocalityName\",\"properties\":\"Type\":\"Town\",\"type\":\"LocalityName\",\"_text\":\"東京都豊島区東池袋三丁目\",\"elementId\":\"4:be6dcfeb-90a4-4ae6-b3aa-1ccc9172af42:372593781\""],
                        ["\"building_count\":108943,\"aver_height\":10.497286654489306"]
                     ]
"""
# 读取 Excel 文件
df = pd.read_excel('evaluation_examples.xlsx')

# 分别读取input、response、context
query = df['input'].tolist()
response = df['response'].tolist()
retrieved_contexts = []

for i in range(df.shape[0]):
    context = df.loc[i, 'context']
    context_list = [context]
    retrieved_contexts.append(context_list)

for q, r, c in zip(query, response, retrieved_contexts):
    dataset.append(
        {
            "user_input": q,
            "response": r,
            "retrieved_contexts": c
        }
    )
evaluation_dataset = EvaluationDataset.from_list(dataset)

# 评价参数
evaluator_llm = LangchainLLMWrapper(llm)
result = evaluate(dataset=evaluation_dataset, metrics=[Faithfulness(), AnswerRelevancy(), ContextRelevance()], llm=evaluator_llm)

print(result)