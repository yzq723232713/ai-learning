"""
Day 3 练习：类型系统 + 数据处理基础
对比 C++：Python 的类型提示不强制，但有工具链做静态检查
"""

# ========================================
# Part 1: Type Hints（类型提示）
# ========================================

print("=== Part 1: Type Hints ===\n")

# Python 3.6+ 支持类型注解，但运行时不强制校验
# 需要 mypy / pyright 等工具做静态检查

# 基本类型
def greet(name: str, age: int) -> str:
    return f"{name}今年{age}岁"

print(greet("张三", 28))

# 复杂类型（需要 typing 模块）
from typing import List, Dict, Optional, Union, Tuple

def process_scores(students: List[str], scores: Dict[str, float]) -> List[Tuple[str, float]]:
    """处理学生成绩，返回排序后的 (姓名, 分数) 列表"""
    result = [(name, score) for name, score in scores.items()]
    result.sort(key=lambda x: x[1], reverse=True)  # 按分数降序
    return result

students = ["张三", "李四", "王五"]
scores = {"张三": 85.5, "李四": 92.0, "王五": 78.5}
print("排名:", process_scores(students, scores))

# Optional = 可以是指定类型或 None
# TODO:个人理解： 返回值类型外面嵌套一层Optional，是为了包含None的返回值类型
def find_user(name: str) -> Optional[Dict]:
    """返回找到的用户，找不到返回 None"""
    db = {"张三": {"age": 28, "city": "北京"}}
    return db.get(name)  # dict.get() 找不到返回 None

print("找到:", find_user("张三"))
print("找不到:", find_user("赵六"))

# Union = 多种类型之一
# TODO: 返回值可以是多种类型
def to_number(s: str) -> Union[int, float]:
    """字符串转数字，优先整数"""
    if "." in s:
        return float(s)
    return int(s)

print("Union返回int:", to_number("42"))
print("Union返回float:", to_number("3.14"))


# ========================================
# Part 2: dataclass（轻量级数据容器）
# ========================================

print("\n=== Part 2: dataclass ===\n")

from dataclasses import dataclass, field
from datetime import datetime

# dataclass 自动生成 __init__ / __repr__ / __eq__ 等
# 对比 C++ 的 struct，但功能强得多
# TODO：自动添加构造函数和类的通用函数

@dataclass
class Point:
    x: float
    y: float

p1 = Point(3.0, 4.0)
p2 = Point(3.0, 4.0)
print("自动__repr__:", p1)               # Point(x=3.0, y=4.0)
print("自动__eq__:", p1 == p2)           # True

# field() 可以设置默认值、默认工厂等
@dataclass
class Student:
    name: str
    age: int
    scores: List[float] = field(default_factory=list)  # 默认空列表
    created_at: datetime = field(default_factory=datetime.now)

s = Student(name="张三", age=28)
print("Student:", s)
print("类型提示为:", Student.__annotations__)  # 查看所有字段的类型


# ========================================
# Part 3: Pydantic BaseModel（数据校验利器）
# ========================================

print("\n=== Part 3: Pydantic BaseModel ===\n")

from pydantic import BaseModel, Field

# Pydantic = dataclass + 自动校验 + 自动类型转换 + JSON序列化 + 变量值约束
# 是 LangChain / LlamaIndex / FastAPI 的标准数据层
# TODO: AI开发中常用的数据类工具，封装很多常用功能

class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=120)           # ge=大于等于, le=小于等于
    email: str
    tags: List[str] = []                       # 默认空列表（Pydantic 自动安全处理）

# 正常创建
u = User(name="张三", age=28, email="zhangsan@example.com")
print("正常:", u)

# 自动类型转换：传字符串 "28" 自动转成 int 28
u2 = User(name="李四", age="30", email="lisi@example.com")
print("自动转换 age str->int:", u2, type(u2.age))  # <class 'int'>

# 校验失败会报错（试试把下面注释取消）
# User(name="王五", age=200, email="wang@test.com")  # age 超过 120

# model_dump() — 转成字典（Pydantic v2，旧版叫 .dict()）
print("转字典:", u.model_dump())

# model_dump_json() — 直接转 JSON 字符串
print("转JSON:", u.model_dump_json())

# 从 JSON 字符串解析
json_str = '{"name":"赵六","age":25,"email":"zhao@test.com"}'
u3 = User.model_validate_json(json_str)
print("从JSON解析:", u3)

# 从字典解析
u4 = User.model_validate({"name": "钱七", "age": 22, "email": "qian@test.com"})
print("从字典解析:", u4)


# ========================================
# Part 4: 文件读写（你已经会 with open，今天扩展格式）
# ========================================

print("\n=== Part 4: 文件读写 ===\n")

import json
import csv
from pathlib import Path

base = Path("E:/learn/day03")

# 4.1 写/读 TXT（复习）
print("--- TXT ---")
with open(base / "sample.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n第二行\n第三行\n")

with open(base / "sample.txt", "r", encoding="utf-8") as f:
    print(f.read())

# 4.2 写/读 JSON（你项目中高频使用）
print("--- JSON ---")
data = {
    "name": "知识库文档",
    "version": "1.0",
    "chunks": [
        {"id": 1, "text": "第一段内容", "source": "doc1.pdf"},
        {"id": 2, "text": "第二段内容", "source": "doc1.pdf"},
    ]
}

# TODO： 文件、json字符串、python对象相互转换或IO
# json.dump: Python对象 → 写入文件
# json.dumps: Python对象 → JSON字符串（s = string）
with open(base / "sample.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)  # indent缩进，易读

# json.load: 从文件读取 → Python对象
# json.loads: JSON字符串 → Python对象
with open(base / "sample.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
    print(f"读取JSON: 名称={loaded['name']}, 块数={len(loaded['chunks'])}")

# 4.3 写/读 CSV（ODS 经验里你肯定用过）
print("--- CSV ---")
rows = [
    ["姓名", "部门", "薪资"],           # 表头
    ["张三", "研发", "15000"],
    ["李四", "产品", "18000"],
    ["王五", "测试", "12000"],
]

with open(base / "sample.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

with open(base / "sample.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)     # 用 DictReader 每行变成字典
    for row in reader:
        print(f"  {row['姓名']} - {row['部门']} - {row['薪资']}")


# ========================================
# Part 5: Pydantic 嵌套模型（进阶）
# ========================================

print("\n=== Part 5: Pydantic 嵌套模型 ===\n")

# Pydantic 可以嵌套，非常适合描述复杂数据结构
class Chunk(BaseModel):
    """文档块"""
    id: int
    text: str
    source: str
    page: int = 1

class Document(BaseModel):
    """文档"""
    title: str
    file_path: str
    file_size: int
    created_at: datetime
    chunks: List[Chunk] = []       # 嵌套另一个 Pydantic 模型
    tags: List[str] = []

# 创建嵌套对象
doc = Document(
    title="产品手册",
    file_path="/docs/manual.pdf",
    file_size=204800,
    created_at=datetime.now(),
    chunks=[
        Chunk(id=1, text="产品概述...", source="manual.pdf", page=1),
        Chunk(id=2, text="安装步骤...", source="manual.pdf", page=3),
    ],
    tags=["产品", "手册"],
)

print(doc.model_dump_json(indent=2))


print("\n*** Day 3 基础练习全部完成! ***")
print("下一步：看 02_document_metadata.py 完成检验练习")
