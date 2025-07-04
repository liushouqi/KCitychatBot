# KCitychatBot: A knowledge graph based chatbot system for large scale CityGML dataset
A chatbot based on llm and kg to translate citygml into natural language.
---
This repository is the official implementation of [<u>"KCitychatBot: A knowledge graph based chatbot system for large scale CityGML dataset"</u>](https://www.csis.u-tokyo.ac.jp/3d_geoinfo_sdsc_2025/overview.html)  

![整体框架-En](https://github.com/user-attachments/assets/78b53ea9-424e-437e-94b0-a8d537d89d7c)


## 1.Abstract
CityGML has been extensively studied due to its widespread use across various domains. However, its complex hierarchical structure still presents challenges for non-expert users. Recently, large language models (LLMs) have demonstrated significant capabilities in natural language processing (NLP) and chatbot systems. Nevertheless, LLMs heavily rely on pre-trained data, which can lead to hallucination issues and limitations in context length. To address these challenges, we first propose a novel automatic method for transforming CityGML data into knowledge graphs by leveraging a graph database and a transformation plugin. This approach effectively addresses the difficulties of storing and representing the complex structure of CityGML and can serve as an external knowledge base for chatbot systems. Second, we develop a collaborative multi-agent framework that enables natural language queries over CityGML data in a user-friendly manner. By integrating the constructed knowledge graphs with several knowledge augmentation strategies, the chatbot system implements a complete pipeline from natural language input to structured query generation, external knowledge retrieval, and optimized response generation. We conduct experiments on both the city knowledge graphs and the chatbot system to evaluate the accuracy of the knowledge graphs and the interpretability of the system’s outputs. The experimental results demonstrate that the generated knowledge graph is accurate, and the chatbot system performs well in terms of answer accuracy, relevance, and contextual coherence. These findings highlight the potential of the proposed chatbot system to lower the barrier for non-professionals interacting with CityGML data, offering both theoretical insights and practical implications for advancing CityGML applications in the era of LLMs and promoting smart city development.
## 2.Requirements
[<u>DeepSeek API</u>](https://platform.deepseek.com/sign_in) and [<u>OpenAI API</u>](https://platform.openai.com/settings/organization/api-keys) are required, DeepSeek API is used to chat and analysis, while OpenAI API is for embedding models and evaluation. Furthermore, you need to apply for the [<u>Neo4j</u>](https://neo4j.com/download/) database(free), and download a plugin [<u>APOC</u>](https://github.com/neo4j/apoc).  

To install the complete requiring packages, use the following command at the root directory of the repository:  

```
pip install -r requirements.txt
```
## 3.QuickStart



