from neo4j import GraphDatabase, Driver
from typing import Optional

# 创建一个模块级的变量来持有 Driver 实例。
# 初始值为 None，表示尚未连接。
_driver: Optional[Driver] = None

def initialize_driver(url: str, user: str, password: str):
    """
    初始化全局 Driver 对象，供整个应用使用。
    如果已经存在一个 driver，会先关闭它再创建新的。
    """
    global _driver
    if _driver:
        _driver.close()
    
    try:
        # 创建 Driver 实例并验证连接
        _driver = GraphDatabase.driver(url, auth=(user, password))
        _driver.verify_connectivity()
        print("Neo4j Driver initialized successfully.")
    except Exception as e:
        _driver = None # 如果初始化失败，确保 _driver 是 None
        print(f"Failed to initialize Neo4j Driver: {e}")
        raise e # 将异常向上抛出，让调用者知道失败了

def get_neo4j_driver() -> Driver:
    """
    获取已初始化的 Driver 实例。
    这是应用中其他部分（如 gml_processor）应该调用的函数。
    """
    if _driver is None:
        raise Exception("Driver not initialized. Please connect to the database first.")
    return _driver

def close_driver():
    """
    在应用关闭时，关闭 Driver 连接。
    """
    global _driver
    if _driver:
        _driver.close()
        _driver = None
        print("Neo4j Driver closed.")

def test_neo4j_connection(url: str, user: str, password: str):
  
    try:
        with GraphDatabase.driver(url, auth=(user, password)) as driver:
            driver.verify_connectivity()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        raise e