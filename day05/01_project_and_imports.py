"""
Day 5 练习：包管理 + 工程化
对比 C++：poetry ≈ CMake + vcpkg，pyproject.toml ≈ CMakeLists.txt
"""

# ========================================
# Part 1: pyproject.toml 结构讲解
# ========================================

print("=== Part 1: pyproject.toml ===\n")

# pyproject.toml 是 Python 项目的"身份证"，放在项目根目录
# 
# [tool.poetry]        — 项目元信息（名称、版本、描述）
# [tool.poetry.dependencies] — 生产依赖（运行时需要的库）
# [tool.poetry.group.dev.dependencies] — 开发依赖（测试、格式化等）
# [build-system]       — 构建系统配置
#
# 对比 pyproject.toml vs requirements.txt：
#   requirements.txt 只管依赖名，不管版本锁定、不管开发/生产区分
#   pyproject.toml + poetry.lock = 精确可复现的环境

# 咱们的 ai-learning 项目最终会是这样的 pyproject.toml：
example_toml = """
[tool.poetry]
name = "ai-knowledge-base"
version = "0.1.0"
description = "企业级RAG知识库问答系统"
authors = ["Your Name <email@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115"
langchain = "^0.3"
pydantic = "^2.0"
python-dotenv = "^1.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
print("一个典型的 pyproject.toml 长这样:")
print(example_toml)


# ========================================
# Part 2: import 机制 — 绝对导入 vs 相对导入
# ========================================

print("=== Part 2: import 机制 ===\n")

# 假设你的项目结构：
# ai-knowledge-base/
#   src/
#     __init__.py
#     loader/
#       __init__.py
#       pdf_loader.py      # 里面有 PDFLoader 类
#       docx_loader.py     # 里面有 DocxLoader 类
#     api/
#       __init__.py
#       main.py            # FastAPI 入口
#   tests/
#     test_loader.py

# ===== 绝对导入（推荐，最清晰）=====
# 从项目根路径写起，不管当前文件在哪个目录

# 在 tests/test_loader.py 里：
# from src.loader.pdf_loader import PDFLoader       # 从项目根写

# 在 src/api/main.py 里：
# from src.loader.pdf_loader import PDFLoader       # 同上


# ===== 相对导入（只能在包内部用）=====
# 用 . 表示当前目录，.. 表示上级目录

# 在 src/loader/docx_loader.py 里引用同目录的 pdf_loader：
# from .pdf_loader import PDFLoader                 # . = 当前目录

# 在 src/api/main.py 里引用上一级的 loader：
# from ..loader.pdf_loader import PDFLoader         # .. = 上一级


# ===== __init__.py 的作用 =====
# 1. 标记这个目录是一个 Python 包（没有它就不能 import）
# 2. 可以在里面写 import 简化外部调用

# src/loader/__init__.py 内容可以是：
# from .pdf_loader import PDFLoader
# from .docx_loader import DocxLoader
# 这样外部就能 from src.loader import PDFLoader，不用写全路径

print("import 规则只有两条：")
print("  1. 每个需要被 import 的文件夹都要有 __init__.py")
print("  2. 项目里尽量用绝对导入 from src.xxx import yyy")
print("  3. 同一个 package 内部可以用相对导入 from .xxx import yyy")


# ========================================
# Part 3: python-dotenv — 管理敏感信息
# ========================================

print("\n=== Part 3: python-dotenv ===\n")

# 问题：API Key 不能硬编码在代码里（会泄露到 Git）
# 方案：放 .env 文件，用 python-dotenv 加载到环境变量

from dotenv import load_dotenv
import os

# 先创建 .env 文件
env_content = """# API 密钥（不要提交到 Git！）
DASHSCOPE_API_KEY=sk-your-key-here
OPENAI_API_KEY=sk-your-openai-key
DB_HOST=localhost
DB_PORT=5432
"""
with open("E:/learn/day05/.env", "w", encoding="utf-8") as f:
    f.write(env_content)

# 加载 .env 文件
load_dotenv("E:/learn/day05/.env")

# 用 os.getenv 读取（第二个参数是默认值，key 不存在时用这个）
api_key = os.getenv("DASHSCOPE_API_KEY")
db_host = os.getenv("DB_HOST", "127.0.0.1")   # 有就取，没有用默认
db_port = os.getenv("DB_PORT", "3306")

print(f"DASHSCOPE_API_KEY = {api_key}")
print(f"DB_HOST = {db_host}")
print(f"DB_PORT = {db_port}")

# 实际项目中的用法：
# load_dotenv()          # 默认加载当前目录的 .env
# api_key = os.getenv("DASHSCOPE_API_KEY")
# client = DashScope(api_key=api_key)

# 别忘了把 .env 加入 .gitignore！
# echo ".env" >> .gitignore


# ========================================
# Part 4: logging — 日志模块
# ========================================

print("\n=== Part 4: logging ===\n")

import logging

# 4.1 最简单的用法（直接输出到控制台）
print("--- 基本用法 ---")
logging.basicConfig(
    level=logging.INFO,                          # 只显示 INFO 及以上级别
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

logging.debug("这是调试信息（不会显示，级别低于 INFO）")
logging.info("文档加载完成，共 150 个块")
logging.warning("文档 sample.pdf 解析失败，已跳过")
logging.error("向量库连接失败")
# logging.critical("系统不可用，立即处理")

# 日志级别（从低到高）：
# DEBUG < INFO < WARNING < ERROR < CRITICAL
# 设置了 level=INFO，DEBUG 就被过滤掉了

# 4.2 写入文件
print("\n--- 写入文件 ---")
file_handler = logging.FileHandler("E:/learn/day05/app.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logger = logging.getLogger("my_app")   # 创建一个命名 logger
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

logger.info("应用启动")
logger.warning("配置文件未找到，使用默认配置")

print("日志已写入 E:/learn/day05/app.log")


# ========================================
# Part 5: 虚拟环境的概念
# ========================================

print("\n=== Part 5: 虚拟环境 ===\n")

# 为什么需要虚拟环境？
# 项目A 需要 langchain==0.3.0
# 项目B 需要 langchain==0.2.0
# 全局只能装一个版本 → 冲突！
# 解决：每个项目一个虚拟环境，互相隔离

# poetry 自动管理虚拟环境，你不需要手动操作：
# poetry install      → 创建虚拟环境 + 安装所有依赖
# poetry shell         → 进入虚拟环境的 shell
# poetry add fastapi   → 安装一个包到虚拟环境
# poetry run python xxx.py → 在虚拟环境里运行脚本

# 如果你不用 poetry，Python 自带的 venv 也能做：
# python -m venv .venv          → 创建虚拟环境
# .venv\Scripts\activate        → 激活（Windows）
# pip install xxx               → 在虚拟环境里装包

print("poetry 三个常用命令：")
print("  poetry init     → 初始化项目（交互式）")
print("  poetry add xxx  → 添加依赖")
print("  poetry install  → 安装 pyproject.toml 里列出的所有依赖")


print("\n*** Day 5 基础练习全部完成! ***")
print("下一步：看 02_poetry_project.md 完成检验练习")
