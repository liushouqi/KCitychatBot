# gml_processor.py
import os
from lxml import etree
import math
import re
import time
from typing import List, Tuple, Dict
from load.db_connector import get_neo4j_driver
from load.cypher_withregion import create_query
import asyncio
import aiofiles
import uuid

# 假设 main.py 中的 ConnectionManager 类在这里可以被访问
# 更好的做法是定义一个基类或直接传递 websocket 对象，但为了简单，我们直接传递 manager 和 client_id
# from main import manager # 避免循环导入，直接通过参数传递

# --- 将同步函数包装成异步 ---
async def run_in_thread(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)

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
        # iterparse 可以在不加载整个文件到内存的情况下工作
        for event, element in etree.iterparse(f, events=('start',)):
            return element.nsmap
    return {}

def extract_region(path: str) -> str:
    """从文件路径中提取区域信息。"""
    # 这个正则表达式可能需要根据你的文件名格式进行调整
    # 例如，如果文件名为 "510100成都市_Building.gml"，这个正则可以工作
    pattern = re.compile(r"(\d+[\u4e00-\u9fa5]+)") 
    match = pattern.search(path)
    if match:
        return match.group(1)
    return "UnknownRegion"

def _split_gml_file_sync(input_file_path: str, namespaces: Dict, original_filename: str) -> List[str]:
    """同步分割文件的核心逻辑"""
    tree = etree.parse(input_file_path)
    root = tree.getroot()
    cityObMember_elements = root.xpath("//core:cityObjectMember", namespaces=namespaces)
    
    if not cityObMember_elements:
        return [input_file_path] # 如果没有 cityObjectMember，则不分割

    batch_size = math.ceil(len(cityObMember_elements) / 10)
    total_batches = (len(cityObMember_elements) + batch_size - 1) // batch_size
    
    # 使用原始文件名的前缀，避免临时文件名影响输出
    base_name = os.path.splitext(original_filename)[0]
    output_dir = os.path.dirname(input_file_path)
    output_files_path = []

    boundedBy_elements = root.xpath("//gml:boundedBy", namespaces=namespaces)

    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(cityObMember_elements))
        output_file = os.path.join(output_dir, f"{base_name}_part{batch_idx + 1}.gml")

        with open(output_file, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            city_model_start = f'<core:CityModel{" "}'
            for prefix, uri in namespaces.items():
                city_model_start += f'xmlns:{prefix}="{uri}" '
            city_model_start += '>\n'
            f.write(city_model_start.encode('utf-8'))

            for boundedBy in boundedBy_elements:
                f.write(etree.tostring(boundedBy, pretty_print=True, encoding='utf-8'))
            
            for cityObMember in cityObMember_elements[start_idx:end_idx]:
                f.write(etree.tostring(cityObMember, pretty_print=True, encoding='utf-8'))

            f.write(b'</core:CityModel>\n')
            output_files_path.append(output_file)
    return output_files_path


async def import_gml_file_to_neo4j(file_path: str, dbname: str, original_filename: str, manager, client_id: str) -> bool:
    """
    将 GML 文件导入 Neo4j 的核心逻辑，并通过 WebSocket 发送进度。
    """
    gml_region = extract_region(original_filename) # 从原始文件名提取区域信息
    file_display_name = os.path.basename(original_filename)

    driver = get_neo4j_driver()
    if not driver:
        await manager.send_personal_message("Error: Database driver has not been initialized. Please connect first.", client_id)
        return False

    # 使用 run_in_thread 执行同步 IO 操作
    gml_size = await run_in_thread(get_file_size, file_path)
    namespaces = await run_in_thread(extract_namespaces, file_path)

    success = False
    
    # 辅助函数，用于执行数据库查询
    async def execute_db_query(path, display_name):
        start_time = time.time()
        try:
            absolute_path = os.path.abspath(path)       
            uri_compatible_path = absolute_path.replace('\\', '/')
            
            # 数据库查询是阻塞的，也放入线程池
            await run_in_thread(
                driver.execute_query,
                create_query,
                # 使用修正后的URI
                file_path="/" + uri_compatible_path,
                database_=dbname,
                region=gml_region
            )
            single_time = time.time() - start_time
            await manager.send_personal_message(f"Import successfully:{display_name}, time taken: {single_time:.3f}s", client_id)
            return True
        except Exception as query_e:
            await manager.send_personal_message(f"Import failed: {display_name}: {query_e}", client_id)
            return False

    if gml_size <= 300:
        await manager.send_personal_message(f"File is being imported: {file_display_name} (Size: {gml_size:.2f}MB)", client_id)
        success = await execute_db_query(file_path, file_display_name)
    else:
        await manager.send_personal_message(f'File: {file_display_name} is ({gml_size:.2f}MB), and it will be divided and imported in batches.', client_id)
        
        # 分割文件是CPU和IO密集型操作，放入线程池
        split_paths = await run_in_thread(_split_gml_file_sync, file_path, namespaces, original_filename)
        await manager.send_personal_message(f"File: '{file_display_name}' has been divided into {len(split_paths)} batcdhes.", client_id)
        
        batch_success = True
        for idx, part_gml_path in enumerate(split_paths):
            part_display_name = os.path.basename(part_gml_path)
            await manager.send_personal_message(f"Batch {idx + 1}/{len(split_paths)}: {part_display_name} is being processed.", client_id)
            if not await execute_db_query(part_gml_path, part_display_name):
                batch_success = False

        if batch_success:
            await manager.send_personal_message(f"All the batches have been imported successfully.", client_id)
            success = True
        else:
            await manager.send_personal_message("Partial or complete batches import failed.", client_id)
            success = False
    
    return success

async def process_uploaded_gml_file(original_filename: str, file_content: bytes, dbname: str, manager, client_id: str):
    temp_dir = "temp_uploaded_gml"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 创建一个唯一的临时文件名来避免冲突
    temp_file_name = f"uploaded_{uuid.uuid4()}_{original_filename}"
    temp_file_path = os.path.join(temp_dir, temp_file_name)
    
    all_temp_files = [temp_file_path] # 记录所有生成的临时文件以便清理

    try:
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            await out_file.write(file_content)
        
        await manager.send_personal_message(f"File: '{original_filename}' has been saved to the server, start processing.", client_id)
        
        # 调用核心导入逻辑
        await import_gml_file_to_neo4j(temp_file_path, dbname, original_filename, manager, client_id)
        
        # 收集分割后产生的文件
        base_name = os.path.splitext(original_filename)[0]
        for item in os.listdir(temp_dir):
            if item.startswith(f"{base_name}_part") and item.endswith(".gml"):
                 all_temp_files.append(os.path.join(temp_dir, item))

    except Exception as e:
        await manager.send_personal_message(f"Processing file: '{original_filename}' occurs with serious error: {e}", client_id)
    finally:
        # 清理所有临时文件
        for f_path in all_temp_files:
            if os.path.exists(f_path):
                os.remove(f_path)
        await manager.send_personal_message(f"File: '{original_filename}' has been processed, and the temporary files have been cleared.", client_id)
        # 尝试清理空目录
        try:
            if not os.listdir(temp_dir):
                os.rmdir(temp_dir)
        except OSError:
            pass # 目录非空则忽略