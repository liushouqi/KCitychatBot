import os
from lxml import etree
import math
import re
import time
from typing import List, Tuple, Dict, BinaryIO
from load.db_connector import get_neo4j_driver
from load.cypher_withregion import create_query 
import asyncio
import aiofiles
import uuid


def get_file_size(file_path: str) -> float:
    """获取文件的大小（MB）。"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    file_size = os.path.getsize(file_path)
    file_size_mb = round(file_size / (1024 * 1024), 2)
    return file_size_mb

def extract_namespaces(file_path: str) -> Dict[str, str]:
    """解析 XML 文件以提取命名空间。"""
    with open(file_path, 'rb') as f:
        for event, element in etree.iterparse(f, events=('start',)):
            return element.nsmap
    return {}

def extract_region(path: str) -> str:
    """从文件路径中提取区域信息。"""
    pattern = re.compile(r"/(\d+[\u4e00-\u9fa5]+)/") # 匹配数字和中文字符
    match = pattern.search(path)
    if match:
        return match.group(1)
    return "UnknownRegion" # 如果未找到，返回默认值

def split_gml_file(input_file_path: str) -> List[str]:
    """
    将大GML文件分割成小块并保存，返回分割后的文件路径列表。
    """
    tree = etree.parse(input_file_path)
    root = tree.getroot()
    namespaces = extract_namespaces(input_file_path)

    boundedBy_elements = root.xpath("//gml:boundedBy", namespaces=namespaces)
    cityObMember_elements = root.xpath("//core:cityObjectMember", namespaces=namespaces)
    
    batch_size = math.ceil(len(cityObMember_elements) / 10) if len(cityObMember_elements) > 0 else 1
    total_batches = (len(cityObMember_elements) + batch_size - 1) // batch_size if len(cityObMember_elements) > 0 else 0

    base_path = input_file_path.rsplit('.', 1)[0]
    output_files_path = []

    if total_batches == 0:
        output_files_path.append(input_file_path)
        return output_files_path

    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(cityObMember_elements))
        output_file = f"{base_path}_part{batch_idx + 1}.gml"

        with open(output_file, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')

            city_model_start = f'<core:CityModel{" "}'
            for prefix, uri in namespaces.items():
                city_model_start += f'xmlns:{prefix}="{uri}" '
            city_model_start += '>\n'
            f.write(city_model_start.encode('utf-8'))

            for boundedBy in boundedBy_elements:
                boundedBy_content = etree.tostring(boundedBy, pretty_print=True, encoding='utf-8')
                f.write(boundedBy_content)

            for cityObMember in cityObMember_elements[start_idx:end_idx]:
                cityObMember_content = etree.tostring(cityObMember, pretty_print=True, encoding='utf-8')
                f.write(cityObMember_content)

            f.write(b'</core:CityModel>\n')
            output_files_path.append(output_file)
    return output_files_path


async def import_gml_file_to_neo4j(file_path: str, dbname: str, messages: List[str]) -> bool:
    """
    实际将 GML 文件（或其分割部分）导入 Neo4j 的核心逻辑。
    messages: 用于收集日志消息。
    """
    gml_size = get_file_size(file_path)
    # 重新引入 region 提取，因为 create_query 期望这个参数
    gml_region = extract_region(file_path) 

    driver = get_neo4j_driver()
    if not driver:
        messages.append("错误：数据库未连接。请先连接。")
        return False

    success = False
    file_display_name = os.path.basename(file_path)

    if gml_size <= 300: # 分割阈值，例如 300 MB
        messages.append(f"正在导入文件: {file_display_name} (大小: {gml_size:.2f}MB)")
        start_time = time.time()
        try:
            # 直接使用导入的 create_query
            records, summary, keys = driver.execute_query(
                create_query,
                file_path="file:///" + file_path, # Neo4j LOAD CSV 的路径格式
                database_=dbname,
                region=gml_region # 重新传入 region 参数
            )
            end_time = time.time()
            single_time = end_time - start_time
            messages.append(f"文件导入成功: {file_display_name}, 用时: {single_time:.3f}s")
            success = True
        except Exception as query_e:
            messages.append(f"文件导入失败 {file_display_name}: {query_e}")
            success = False
    else:
        messages.append(f'文件 {file_display_name} 过大 ({gml_size:.2f}MB)，将进行分割并分批导入。')
        split_paths = split_gml_file(file_path)
        messages.append(f"文件 '{file_display_name}' 已被分割成 {len(split_paths)} 个部分。")
        
        total_batch_time = 0.0
        batch_success = True
        for idx, part_gml_path in enumerate(split_paths):
            messages.append(f"正在导入分割文件 {idx + 1}/{len(split_paths)}: {os.path.basename(part_gml_path)}")
            start_time = time.time()
            try:
                # 直接使用导入的 create_query
                records, summary, keys = driver.execute_query(
                    create_query,
                    file_path="file:///" + part_gml_path,
                    database_=dbname,
                    region=gml_region # 重新传入 region 参数
                )
                end_time = time.time()
                single_time = end_time - start_time
                messages.append(f"分割文件导入成功: {os.path.basename(part_gml_path)}, 用时: {single_time:.3f}s")
                total_batch_time += single_time
            except Exception as query_e:
                messages.append(f"分割文件导入失败 {os.path.basename(part_gml_path)}: {query_e}")
                batch_success = False
        
        if batch_success:
            messages.append(f"所有分割文件导入完毕。总用时: {total_batch_time:.3f}s")
            success = True
        else:
            messages.append("部分或全部分割文件导入失败。")
            success = False
    return success

async def process_uploaded_gml_file(original_filename: str, file_content: bytes, dbname: str) -> Tuple[List[str], bool]:  
    messages = []
    overall_success = True
    temp_dir = "temp_uploaded_gml"

    os.makedirs(temp_dir, exist_ok=True)

    temp_file_name = f"uploaded_{uuid.uuid4()}_{original_filename}"
    temp_file_path = os.path.join(temp_dir, temp_file_name)
    
    messages.append(f"已接收文件: {original_filename}")

    try:
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            await out_file.write(file_content)
        
        messages.append(f"文件 '{original_filename}' 已保存到临时路径: {temp_file_path}")
        
        success_this_file = await import_gml_file_to_neo4j(temp_file_path, dbname, messages)
        if not success_this_file:
            overall_success = False
    except Exception as e:
        messages.append(f"处理文件 '{original_filename}' 过程中发生错误: {e}")
        overall_success = False
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            messages.append(f"临时文件 {os.path.basename(temp_file_path)} (原文件: '{original_filename}') 已清理。")

    try:
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
            messages.append(f"临时目录 '{temp_dir}' 已移除。")
    except OSError as e:
        messages.append(f"警告：无法移除临时目录 '{temp_dir}': {e}")

    return messages, overall_success