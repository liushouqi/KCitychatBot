from neo4j import GraphDatabase
from cypher_noothers import create_query
import tkinter as tk
from tkinter import filedialog
import time


def get_filepath():
    # 创建根窗口，但不显示
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 打开文件选择对话框，用户选择文件
    file_path = filedialog.askopenfilename(title="Select a file")
    return  file_path


def import_single_gml(url, auth, dbname):
    try:
        gml_path = get_filepath()
        with GraphDatabase.driver(url, auth=auth) as driver:
            print("连接成功！")
            with driver.session(database=dbname) as session:
                start_time = time.time()
                records, summary, keys = driver.execute_query(
                    create_query,
                    file_path="/" + gml_path,
                    database_=dbname
                )
                # 下面是使用session以及多条语句的写法
                # with session.begin_transaction() as tx:
                #     tx.run(
                #         create_query,
                #         file_path="/" + gml_path
                #     )
                    # tx.run(
                    #     "MATCH(m:CityModel) SET m.region = $region",
                    #      region = gml_region
                    # )
                end_time = time.time()
                times = end_time - start_time
                print(f"用时{times:.3f}s")


    except Exception as e:
        print(f"连接失败: {e}")


if __name__ == "__main__":
    URL = "bolt://localhost:7687"
    AUTH = ("neo4j", "your password")
    import_single_gml(URL, AUTH, "demo")