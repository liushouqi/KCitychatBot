import pandas as pd

# 读取 Excel 文件
df = pd.read_excel('evaluation_examples.xlsx')

# 分别读取第二列、第三列、第四列（索引为1, 2, 3）的数据，从第1行开始
"""
query = df.iloc[:, 1].tolist()
response = df.iloc[:, 2].tolist()
row_num = df.shape[0]
retrieved_contexts = []
for i in range(0, row_num, 1):
        context = df.iloc[i, 3]
        context_list = [context]
        retrieved_contexts.append(context_list)
"""
# 分别读取input、response、context
query = df['input'].tolist()
response = df['response'].tolist()
retrieved_contexts = []

for i in range(df.shape[0]):
    context = df.loc[i, 'context']
    context_list = [context]
    retrieved_contexts.append(context_list)

print(retrieved_contexts)