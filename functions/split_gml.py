from lxml import etree
import tkinter as tk
from tkinter import filedialog
import math


def get_filepath():
    # 创建根窗口，但不显示
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 打开文件选择对话框，用户选择文件
    return filedialog.askopenfilename(title="Select a file")


def extract_namespaces(file_path):
    # 使用 etree 解析文件并获取命名空间
    with open(file_path, 'rb') as f:
        for event, element in etree.iterparse(f, events=('start',)):
            return element.nsmap


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

if __name__ == "__main__":
    input_file = get_filepath()
    if input_file:
        split_gml_file(input_file)
