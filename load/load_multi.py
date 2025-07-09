from neo4j import GraphDatabase
from cypher_noothers import create_query
import tkinter as tk
from tkinter import filedialog
import os
import time


def get_folder_path():
    """
    打开文件夹选择对话框，选择文件夹并返回路径
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    folder_path = filedialog.askdirectory(title="Select a folder")  # 打开选择文件夹对话框
    return folder_path

def find_gml_path(folder_path):
    """
    遍历文件夹及其子文件夹，查找所有 .gml 格式的文件并返回其绝对路径
    :param folder_path: 要查找的文件夹路径
    :return: gml 文件的绝对路径列表
    """
    gml_path = []

    # 遍历文件夹及其子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".gml", ".xml")): # 判断文件是否是 .gml或.xml格式（忽略大小写）
                absolute_path = os.path.abspath(os.path.join(root, file)).replace("\\", "/")
                gml_path.append(absolute_path)

    return gml_path



def import_from_dir(url, auth, dbname):
    try:
            fold_path = get_folder_path()
            files_path = find_gml_path(fold_path)
            times = 0
            counts = 0
            for index, file_path in enumerate(files_path, start=1):
                with GraphDatabase.driver(url, auth=auth) as driver:
                    driver.verify_connectivity()
                    print(f"连接成功!处理第{index}个文件",end=",")
                    start_time = time.time()
                    records, summary, keys = driver.execute_query(
                        create_query,
                        file_path="/" + file_path,
                        database_=dbname,
                    )
                    end_time = time.time()
                    single_time = end_time - start_time
                    times += single_time
                    counts += 1
                    print(f"文件路径:{file_path},用时:{single_time:.3f}s")
                    driver.close()
            print(f"文件总数:{counts},总用时:{times:.3f}s")


    except Exception as e:
        print(f"连接失败: {e}")


if __name__ == "__main__":
    URL = "bolt://localhost:7687"
    AUTH = ("neo4j", "your password")
    import_from_dir(URL, AUTH, "demo")