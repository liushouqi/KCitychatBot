from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas import EvaluationDataset
from ragas.metrics import Faithfulness,AnswerRelevancy,ContextRelevance
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# 设置嵌入模型
load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo")
embeddings = OpenAIEmbeddings()

# 导入评价数据集
dataset = []
query = ["丰岛区建筑物的平均高度是多少？"]
response = ["丰岛区共有108,943栋建筑物，这些建筑物的平均高度约为10.5米。"]
retrieved_contexts = [['"building_count": 108943, "aver_height": 10.497286654489306']]

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