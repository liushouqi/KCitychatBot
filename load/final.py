from neo4j import GraphDatabase
from cypher_withregion import create_query
import tkinter as tk
from tkinter import filedialog
import os
from lxml import etree
import math
import re
import time


def get_file_path():
    # 创建根窗口，但不显示
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 打开文件选择对话框，用户选择文件
    file_path = filedialog.askopenfilename(title="Select a file")
    return  file_path


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
    folder_path: 要查找的文件夹路径
    gml_path 文件的绝对路径列表
    """
    gml_path = []

    # 遍历文件夹及其子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".gml"):  # 判断文件是否是 .gml 格式（忽略大小写）
                absolute_path = os.path.abspath(os.path.join(root, file)).replace("\\", "/")
                gml_path.append(absolute_path)

    return gml_path


def get_file_size(file_path):
    # 获取文件的大小（以字节为单位）
    file_size = os.path.getsize(file_path)
    # 将字节转换为MB
    file_size_mb = round(file_size / (1024 * 1024), 2)

    return file_size_mb


def extract_namespaces(file_path):
    # 使用 etree 解析文件并获取命名空间
    with open(file_path, 'rb') as f:
        for event, element in etree.iterparse(f, events=('start',)):
            return element.nsmap


def extract_region(path):
    pattern = re.compile(r"/(\d+[\u4e00-\u9fa5]+)/")
    match = pattern.search(path)
    region = match.group(1)
    return  region


def split_gml_file(input_file):
    # 解析 XML 文件
    tree = etree.parse(input_file)
    root = tree.getroot()

    # 动态提取命名空间
    namespaces = extract_namespaces(input_file)

    # 使用 XPath 查询
    boundedBy_elements = root.xpath("//gml:boundedBy", namespaces=namespaces)
    cityObMember_elements = root.xpath("//core:cityObjectMember", namespaces=namespaces)
    print(f"该gml包含的cityObjectMember对象数为:{len(cityObMember_elements)}")

    # 每次分块设置为cityObjectMember元素数的十分之一
    batch_size = math.ceil(len(cityObMember_elements) / 10)
    total_batches = (len(cityObMember_elements) + batch_size - 1) // batch_size

    # 获取输入文件的基础路径
    base_path = input_file.rsplit('.', 1)[0]
    output_files_path = []

    # 遍历每组 cityObjectMember 并保存为单独的文件
    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(cityObMember_elements))
        output_file = f"{base_path}_{batch_idx + 1}.gml"  # 构造输出文件名

        with open(output_file, "wb") as f:
            # 写入 XML 声明
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')

            # 构造 <core:CityModel> 标签
            city_model_start = f'<core:CityModel{" "}'
            for prefix, uri in namespaces.items():
                city_model_start += f'xmlns:{prefix}="{uri}" '
            city_model_start += '>\n'
            f.write(city_model_start.encode('utf-8'))

            # 写入 <gml:boundedBy> 的内容
            for boundedBy in boundedBy_elements:
                boundedBy_content = etree.tostring(boundedBy, pretty_print=True, encoding='utf-8')
                f.write(boundedBy_content)

            # 写入分组的 <core:cityObjectMember> 的内容
            for cityObMember in cityObMember_elements[start_idx:end_idx]:
                cityObMember_content = etree.tostring(cityObMember, pretty_print=True, encoding='utf-8')
                f.write(cityObMember_content)

            # 写入结束标签 </core:CityModel>
            f.write(b'</core:CityModel>\n')
            output_files_path.append(output_file)

        print(f"Batch {batch_idx + 1} written to {output_file}")
    return output_files_path


def import_single_gml(url, auth, dbname):
    """提供数据库地址、名称、用户名、密码
       手动选择一个gml文件
       自动创建节点
    """
    try:
        gml_path = get_file_path()
        times = 0
        counts = 0
        gml_size = get_file_size(gml_path)
        gml_region = extract_region(gml_path)
        if gml_size <= 300:
            with GraphDatabase.driver(url, auth=auth) as driver:
                driver.verify_connectivity()
                print(f"连接成功!处理第{counts + 1}个文件", end=",")
                start_time = time.time()
                records, summary, keys = driver.execute_query(
                        create_query,
                        file_path="/" + gml_path,
                        database_=dbname,
                        region = gml_region
                     )
                end_time = time.time()
                single_time = end_time - start_time
                counts += 1
                print(f"文件路径:{gml_path},用时:{single_time:.3f}s")
                driver.close()
        else:
            print(f'输入文件过大，将进行文件分割！')
            gmls_path = split_gml_file(gml_path)
            for gml_path in gmls_path:
                with GraphDatabase.driver(url, auth=auth) as driver:
                    driver.verify_connectivity()
                    print(f"连接成功!处理第{counts + 1}个文件", end=",")
                    start_time = time.time()
                    records, summary, keys = driver.execute_query(
                        create_query,
                        file_path= "/" + gml_path,
                        database_= dbname,
                        region = gml_region
                    )
                    end_time = time.time()
                    single_time = end_time - start_time
                    times += single_time
                    counts += 1
                    print(f"文件路径:{gml_path},用时:{single_time:.3f}s")
                    driver.close()           

            print(f"文件总数:{counts},总用时:{times:.3f}s")
            
    except Exception as e:
        print(f"连接失败: {e}")


def import_from_dir(url, auth, dbname):
    try:
        fold_path = get_folder_path()
        gmls_path = find_gml_path(fold_path)
        times = 0
        counts = 0
        for gml_path in gmls_path:
            with GraphDatabase.driver(url, auth=auth) as driver:
                driver.verify_connectivity()
                gml_size = get_file_size(gml_path)
                gml_region = extract_region(gml_path)
                if gml_size <= 300:
                    print(f"连接成功!处理第{counts + 1}个文件", end=",")
                    start_time = time.time()
                    records, summary, keys = driver.execute_query(
                        create_query,
                        file_path= "/" + gml_path,
                        database_= dbname,
                        region = gml_region
                    )
                    end_time = time.time()
                    single_time = end_time - start_time
                    times += single_time
                    counts += 1
                    print(f"文件路径:{gml_path},用时:{single_time:.3f}s")
                    driver.close()
                else:
                    print(f'输入文件过大，将进行文件分割！')
                    new_gmls_path = split_gml_file(gml_path)
                    gmls_path.extend(new_gmls_path)

        print(f"文件总数:{counts},总用时:{times:.3f}s")

    except Exception as e:
        print(f"连接失败: {e}")


if __name__ == "__main__":
    URL = "bolt://localhost:7687"
    AUTH = ("neo4j", "your password")

    import_single_gml(URL, AUTH, "demo")
    #import_from_dir(URL, AUTH, "demo")



