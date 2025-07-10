# KCitychatBot: A knowledge graph based chatbot system for large scale CityGML dataset
A chatbot based on llm and kg to translate citygml into natural language.
---
This repository is the official implementation of [<u>"KCitychatBot: A knowledge graph based chatbot system for large scale CityGML dataset"</u>](https://www.csis.u-tokyo.ac.jp/3d_geoinfo_sdsc_2025/overview.html)  

![整体框架-En](https://github.com/user-attachments/assets/78b53ea9-424e-437e-94b0-a8d537d89d7c)


## 1.Abstract
CityGML has been extensively studied due to its widespread use across various domains. However, its complex hierarchical structure still presents challenges for non-expert users. Recently, large language models (LLMs) have demonstrated significant capabilities in natural language processing (NLP) and chatbot systems. Nevertheless, LLMs heavily rely on pre-trained data, which can lead to hallucination issues and limitations in context length. To address these challenges, we first propose a novel automatic method for transforming CityGML data into knowledge graphs by leveraging a graph database and a transformation plugin. This approach effectively addresses the difficulties of storing and representing the complex structure of CityGML and can serve as an external knowledge base for chatbot systems. Second, we develop a collaborative multi-agent framework that enables natural language queries over CityGML data in a user-friendly manner. By integrating the constructed knowledge graphs with several knowledge augmentation strategies, the chatbot system implements a complete pipeline from natural language input to structured query generation, external knowledge retrieval, and optimized response generation. We conduct experiments on both the city knowledge graphs and the chatbot system to evaluate the accuracy of the knowledge graphs and the interpretability of the system’s outputs. The experimental results demonstrate that the generated knowledge graph is accurate, and the chatbot system performs well in terms of answer accuracy, relevance, and contextual coherence. These findings highlight the potential of the proposed chatbot system to lower the barrier for non-professionals interacting with CityGML data, offering both theoretical insights and practical implications for advancing CityGML applications in the era of LLMs and promoting smart city development.
## 2.Requirements
[<u>DeepSeek API</u>](https://platform.deepseek.com/sign_in) and [<u>OpenAI API</u>](https://platform.openai.com/settings/organization/api-keys) are required, DeepSeek API is used to chat and analysis, while OpenAI API is for embedding models and evaluation. Furthermore, you need to apply for the [<u>Neo4j</u>](https://neo4j.com/download/) database(free), and download a plugin [<u>APOC</u>](https://github.com/neo4j/apoc). How to use with this [<u>guide</u>](https://blog.csdn.net/m0_63593482/article/details/133096869) 

To install the complete requiring packages, use the following command at the root directory of the repository:  

```
pip install -r requirements.txt
```
## 3.Structure
Some important components explained:  
- `crews/` — Agent and task configuration directory
- `data/`  — Three themes and metadata from [<u>Plateau</u>](https://www.mlit.go.jp/plateau/open-data/)  
- `knowledge` — External knowledge store in this folder  
- `load` — The construction of knowledge graphs  
- `evaluate/` — Based on   evaluation_table.xlsx, evaluation  autonomously 
- `chatflow.py` — The whole workflow of the chatbot system  
- `chatflow_auto.py` — For autonomous evaluation  
- `evaluation_examples.xlsx` — Three evaluation examples  
- `evaluation_table.xlsx` — Input your questions in the 'input' column, run `chatflow_auto.py`, then response and context will be autonomously written  
- `index.html` — The frontend  
- `main.py` — The backend
- `prompts.py` —  The few-shot learning examples and prompts
## 4.Quickstart
git clone this project:
```
git clone git@github.com:liushouqi/KCitychatBot.git
```
To construct knowledge graphs, input URL, user, database name amd password in the load/final.py, then run:
```
python final.py
```
To use this chatbot system, run:
```
uvicorn main:app --reload   
```
To evaluate system's outputs, run:
```
python evaluation.py
```
## 5.Additional Explanation
* We have integrated all frontend and backend achievements in `main.py`, but it takes a significant amount of time. Therefore, using the backend approach is more recommended. To constuct your knowledge graphs, especially for large-scale CityGML datasets, try `load/final.py`. To chat with CityGML data, try `crews/chatbot.py`. Remember to change URL, user...  
* Don't ask questions randomly, you'd better to see some raw data in `data/`, otherwise your questions might be meaningless or refer to something that doesn't exist in the data.  
* We employ DeepSeeK API, it's cheap but slow. Other LLMs API are also workable. You can change LLM in `crews/input2cypher_crew.py` and `crews/generate_crew.py`.  
* ⭐️ If you find this project helpful, please consider giving it a star! ⭐️




