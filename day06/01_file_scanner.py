"""
Day 6 检验1：文件扫描小工具

综合 Day1(Python基础) + Day3(Pydantic/json) + Day5(工程化)

要求：
1. 扫描指定文件夹下所有 .pdf / .docx / .txt 文件
2. 用 Pydantic 模型组织元数据
3. 输出为 JSON 文件

你的任务：实现 scan_folder() 函数，让测试通过
"""
from pathlib import Path
from datetime import datetime
from typing import List
import json
from pydantic import BaseModel


# ========================================
# TODO 1: 定义 FileMeta 模型（3分钟）
# ========================================
class FileMeta(BaseModel):
    """文件元数据 —— 把 Day 3 的 Pydantic 用起来"""
    filename: str        # 文件名（如 "manual.pdf"）
    extension: str       # 扩展名（如 ".pdf"）
    path: str            # 完整路径
    size_bytes: int      # 文件大小（字节）
    modified_at: datetime  # 最后修改时间


# ========================================
# TODO 2: 实现 scan_folder() 函数
# ========================================
def scan_folder(folder_path: str) -> List[FileMeta]:
    """
    扫描文件夹，返回其中所有 .pdf .docx .txt 文件的元数据列表。

    提示：
    - Path(folder_path).rglob("*") 可以递归遍历所有文件
    - file.suffix 获取扩展名（含点号，如 ".pdf"）
    - file.stat().st_size 获取文件大小
    - file.stat().st_mtime 获取修改时间戳（float），用 datetime.fromtimestamp() 转换
    """
    folder = Path(folder_path)
    files = []

    for file in folder.rglob("*"):
        if file.is_file() and file.suffix in [".pdf", ".docx", ".txt"]:
            files.append(FileMeta(
                filename=file.name, 
                extension=file.suffix, 
                path=str(file), 
                size_bytes=file.stat().st_size, 
                modified_at=datetime.fromtimestamp(file.stat().st_mtime)
            ))

    return files


# ========================================
# TODO 3: 实现 save_to_json() 函数
# ========================================
def save_to_json(files: List[FileMeta], output_path: str):
    """
    将文件元数据列表保存为 JSON 文件。
    提示：用 json.dump() 或 FileMeta 的 model_dump()
    """
    data = [f.model_dump(mode="json") for f in files]
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========================================
# 测试
# ========================================
if __name__ == "__main__":
    # 使用 E:\learn\day06\test_docs 作为扫描目标
    test_dir = "E:/learn/day06/test_docs"

    print(f"扫描目录: {test_dir}")
    results = scan_folder(test_dir)
    print(f"找到 {len(results)} 个文件\n")

    for f in results:
        size_kb = f.size_bytes / 1024
        print(f"  {f.filename:20s} | {f.extension:6s} | {size_kb:8.1f} KB | {f.modified_at}")

    # 保存 JSON
    output = "E:/learn/day06/files_metadata.json"
    save_to_json(results, output)
    print(f"\n元数据已保存到: {output}")
