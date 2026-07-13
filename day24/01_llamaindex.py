"""
Day 24：LlamaIndex 入门 — 跟 LangChain 正面 PK

LangChain = 瑞士军刀，什么都能拼
LlamaIndex = 数据管道专家，专注"文档 → 索引 → 检索 → 回答"

今天用 LlamaIndex 加载 Day 15 的测试文档，跑 RAG 问答，对比两者。
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("llama_index").setLevel(logging.WARNING)

from dotenv import load_dotenv
load_dotenv("E:/learn/day09/.env")


# ============================================================
# Part 1: 定位差异 — LangChain vs LlamaIndex
# ============================================================

print("=== Part 1: LangChain vs LlamaIndex 定位 ===\n")

print("""
┌──────────────────┬─────────────────────┬─────────────────────┐
│      维度         │      LangChain       │     LlamaIndex       │
├──────────────────┼─────────────────────┼─────────────────────┤
│ 核心关注          │ 拼装 LLM 应用        │ 数据索引 + 检索       │
│ 数据处理          │ 需手动拼加载+切块     │ 内置 Ingestion Pipeline│
│ 检索策略          │ 需手动写混合检索      │ 内置多种检索器        │
│ 向量库            │ 需手动集成 Chroma     │ 内置向量存储           │
│ RAG 开箱体验      │ 写一条 LCEL 链       │ SimpleDirectoryReader  │
│                  │                     │ → index.as_query_engine│
│ 适合场景          │ 通用 LLM 应用        │ 文档问答、知识库       │
│ 跟你 ODS 经验的关联│ 弱                  │ 强：数据摄入管道        │
└──────────────────┴─────────────────────┴─────────────────────┘

一句话区分：
  LangChain 让你拼积木（retriever | prompt | llm）
  LlamaIndex 给你一个装修好的房子（把文档扔进去，直接问）
""")


# ============================================================
# Part 2: LlamaIndex 最小 RAG — 5 行代码
# ============================================================

print("=== Part 2: LlamaIndex 最小 RAG ===\n")

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

# 1. 加载文档（一个函数搞定，不用手写 PyMuPDF/docx/txt/csv 四种加载器）
documents = SimpleDirectoryReader(
    input_dir="E:/learn/day15/test_docs",
    required_exts=[".pdf", ".docx", ".txt", ".csv"],  # 自动按扩展名选加载器
).load_data()

print(f"加载了 {len(documents)} 个文档:")
for doc in documents:
    filename = doc.metadata['file_name']
    preview = doc.text[:60].replace("\r", "").replace("\n", " ")
    print(f"  [{filename}] | {len(doc.text)}字 | {preview}...")

# 2. 建索引（自动切块 + Embedding + 入库，一步完成）
# 对比 Day 16-19 你手写的 4 个步骤
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model,
    chunk_size=300,       # 内置递归切分，不用手写
    chunk_overlap=50,
)

# 3. 创建查询引擎（= retriever + prompt + llm 的封装）
llm = OpenAILike(
    model="deepseek-chat",
    api_base="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.0,
    is_chat_model=True,
)
query_engine = index.as_query_engine(llm=llm, similarity_top_k=3)

# 4. 提问
print("\n提问: 「会议的主题是什么？」")
response = query_engine.query("会议的主题是什么？")
print(f"回答: {response}\n")

print("提问: 「怎么安装设备？」")
response = query_engine.query("怎么安装设备？")
print(f"回答: {response}\n")

print("提问: 「张三在哪个部门？」")
response = query_engine.query("张三在哪个部门？")
print(f"回答: {response}")


# ============================================================
# Part 3: 对比 — 你的手写 Day 19 vs LangChain vs LlamaIndex
# ============================================================

print("\n\n=== Part 3: 三种实现方式对比 ===\n")

print("""
┌────────────────┬──────────────────┬─────────────────┬─────────────────┐
│      步骤       │   手写 (Day 19)    │   LangChain       │   LlamaIndex     │
├────────────────┼──────────────────┼─────────────────┼─────────────────┤
│ 文档加载        │ load_document()   │ 需手动集成      │ SimpleDirectory- │
│                │ 4种格式各写一个    │ PyMuPDF等       │ Reader 一行搞定  │
├────────────────┼──────────────────┼─────────────────┼─────────────────┤
│ 切块           │ chunk_text()     │ RecursiveChar-  │ VectorStoreIndex │
│                │ 递归降级 40行     │ acterTextSplitter│ .from_documents  │
│                │                  │ 传参即可         │ 内置切分         │
├────────────────┼──────────────────┼─────────────────┼─────────────────┤
│ Embedding + 存库│ embed + chroma  │ embeddings +    │ 同上，一步完成    │
│                │ .add() 手动调    │ Chroma.from_docs│                  │
├────────────────┼──────────────────┼─────────────────┼─────────────────┤
│ 检索           │ search() 手写    │ retriever       │ query_engine     │
│                │ collection.query │ .invoke()       │ .query()         │
├────────────────┼──────────────────┼─────────────────┼─────────────────┤
│ Prompt + LLM   │ build_prompt()+  │ LCEL 管道符     │ 内置 Prompt      │
│                │ generate_answer()│ retriever|prompt│ 可自定义覆盖      │
│                │                  │ |llm            │                  │
├────────────────┼──────────────────┼─────────────────┼─────────────────┤
│ 代码量          │ ~250 行          │ ~30 行           │ ~10 行           │
│ 可控性          │ 最高             │ 高               │ 中               │
│ 学习价值        │ 最高（理解原理）  │ 高（面试常用）   │ 快速原型         │
└────────────────┴──────────────────┴─────────────────┴─────────────────┘
""")


# ============================================================
# Part 4: LlamaIndex 独有 — Ingestion Pipeline
# ============================================================

print("=== Part 4: Ingestion Pipeline（和你的 ODS 经验最相关）===\n")

print("""
LlamaIndex 的 IngestionPipeline = 你的 ODS 数据管道 + AI 化

ODS 层（你的老本行）:
  原始数据 → 抽取 → 清洗 → 转换 → 加载到 DWD

LlamaIndex Ingestion Pipeline:
  文档 → DocParser → TextCleaner → ChunkSplitter → Embedding → VectorStore

完全对应的思维模型！只是输出从"结构化数据表"变成了"向量 + 文档块"。

代码示例（概念，不跑）:
  from llama_index.core.ingestion import IngestionPipeline
  pipeline = IngestionPipeline(
      transformations=[
          TextCleaner(),          # 你的数据清洗
          SentenceSplitter(),     # 你的数据转换（切块）
          embed_model,            # 向量化
      ]
  )
  nodes = pipeline.run(documents=documents)

面试时讲这个故事：
  "我之前做ODS数仓，对数据质量治理有经验。在RAG项目中，
   我把数据清洗思维用到了文档预处理管道上——去重、清洗、
   标准化格式后才能进向量库。LlamaIndex的IngestionPipeline
   把这个流程工程化了。"
""")


print("*** Day 24 基础练习全部完成! ***")
print("\n关键结论：")
print("  1. LlamaIndex 比 LangChain 更专注 RAG，开箱即用度更高")
print("  2. SimpleDirectoryReader → VectorStoreIndex → query_engine.query = 完整 RAG")
print("  3. IngestionPipeline 跟你的 ODS 数据管道思维直接对应")
print("  4. 选型: 学习用 LlamaIndex（快），面试用 LangChain（灵活），你的项目用 LangChain")
