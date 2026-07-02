"""
Day 18：向量数据库 — 从手写检索到专业存储

为什么 Day 17 的 VectorStore 不够？
  文档从 10 份 → 10 万份 → 100 万份：
  每次查询 = 把 query 跟所有块逐个算余弦相似度（暴力搜索）
  10 万块 × 512 维 × 4 字节 = 200MB，100 万块 = 2GB
  算 100 万次余弦相似度 → 几百毫秒 → 不可接受

向量数据库用 ANN（近似最近邻）索引：
  牺牲 1-2% 精度，换 100 倍速度提升
  百万级向量也能毫秒返回结果

今天两个方案：
  1. Chroma    — 开箱即用，适合学习和快速原型
  2. FAISS     — Meta 出品，工业界常用
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import time


# ========================================
# Part 1: 暴力搜索 vs 向量数据库（直观对比）
# ========================================

print("=== Part 1: 暴力搜索 vs 向量数据库 ===\n")

# 加载模型
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

# 生成 1 万个随机向量模拟"大规模文档库"
print("生成 10000 个 512 维随机向量...")
np.random.seed(42)
large_embeddings = np.random.randn(10000, 512).astype(np.float32)
query_vec = np.random.randn(512).astype(np.float32)

# 暴力搜索
start = time.time()
scores = np.dot(large_embeddings, query_vec)  # 矩阵乘法一次算完 10000 个余弦相似度
top_k_indices = np.argsort(scores)[-5:][::-1]
brute_time = time.time() - start

print(f"  暴力搜索 10000 个向量: {brute_time*1000:.1f} ms")
print(f"  Top-5 索引: {top_k_indices}")

# 向量数据库（Chroma）
import chromadb
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="benchmark")

# 生成 ID 和元数据
ids = [f"doc_{i}" for i in range(10000)]
metadatas = [{"source": f"file_{i%100}.txt"} for i in range(10000)]

# 批量插入（演示用 10 条，防止卡顿）
collection.add(
    ids=ids[:10],
    embeddings=[v.tolist() for v in large_embeddings[:10]],
    metadatas=metadatas[:10],
)
insert_time = time.time() - start

# 批量插入完整数据（Chroma 单批不能超过 5461，分批发）
batch_size = 5000
for start_idx in range(10, 10000, batch_size):
    end_idx = min(start_idx + batch_size, 10000)
    collection.add(
        ids=ids[start_idx:end_idx],
        embeddings=[v.tolist() for v in large_embeddings[start_idx:end_idx]],
        metadatas=metadatas[start_idx:end_idx],
    )

# Chroma 检索
start = time.time()
results = collection.query(query_embeddings=[query_vec.tolist()], n_results=5)
chroma_time = time.time() - start

print(f"\n  Chroma 检索 10000 个向量: {chroma_time*1000:.1f} ms")
print(f"  检索到的 ID: {results['ids'][0]}")
print(f"  相似度: {results['distances'][0]}")

print(f"\n  Chroma vs 暴力搜索: {brute_time/chroma_time:.0f}x 快")


# ========================================
# Part 2: Chroma 基础操作
# ========================================

print("\n\n=== Part 2: Chroma 基础操作 ===\n")

# Chroma 核心概念：
#   Client    — 数据库连接（内存模式 / 持久化模式）
#   Collection — 一个"表"，存向量 + 文档 + 元数据
#   每个向量附带 id（唯一标识）、metadata（过滤用）、document（原文本）

# 创建客户端（内存模式，程序退出数据消失）
client = chromadb.Client()

# 创建集合
# 用自定义 Embedding 函数（让 Chroma 知道我们的向量是 512 维）
from chromadb.utils import embedding_functions
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"
)
col = client.create_collection(
    name="knowledge_base",
    embedding_function=ef,   # 告诉 Chroma 用我们的模型（512 维）
    metadata={"description": "知识库文档向量"},
)

# 添加数据（id 是唯一索引，metadata 用来过滤，document 存原文）
# 这里用 Chroma 自动 Embedding，更方便
col.add(
    ids=["doc1_chunk0", "doc1_chunk1", "doc2_chunk0"],
    documents=[
        "智能温控器安装步骤：固定设备、连接电源、APP配对。",
        "设备支持Wi-Fi和蓝牙两种连接方式。",
        "常见故障：E01错误代码表示传感器故障。",
    ],
    metadatas=[
        {"source": "产品手册.pdf", "page": 1},
        {"source": "产品手册.pdf", "page": 2},
        {"source": "故障手册.pdf", "page": 1},
    ],
)

print(f"集合中有 {col.count()} 条数据")

# 查询（有 embedding_function 后直接用文本查，Chroma 自动转向量）
query = "设备怎么连接网络？"
results = col.query(query_texts=[query], n_results=2)
print(f"\n查询: 「{query}」")
for i, (doc_id, doc, meta, dist) in enumerate(zip(
    results["ids"][0], results["documents"][0],
    results["metadatas"][0], results["distances"][0],
), 1):
    print(f"  {i}. id={doc_id} | 距离={dist:.4f} | 来源={meta['source']}")
    print(f"     内容: {doc}")


# ========================================
# Part 3: 元数据过滤（你的 ODS 经验在这里发光）
# ========================================

print("\n\n=== Part 3: 元数据过滤 ===\n")

# 只检索某个特定来源的文档
print("过滤: 只看《故障手册.pdf》")
results = col.query(
    query_texts=[query],
    n_results=2,
    where={"source": "故障手册.pdf"},
)
print(f"  结果: {results['documents'][0]}")

# 只看页码 >= 2 的
print("\n过滤: 页码 >= 2")
results = col.query(
    query_texts=[query],
    n_results=5,
    where={"page": {"$gte": 2}},
)
print(f"  结果数: {len(results['documents'][0])}")

print("\n元数据过滤的价值：")
print("  - 用户问'产品手册里怎么安装' → 过滤 source='产品手册.pdf'")
print("  - 用户问'2024年的制度' → 过滤 year=2024")
print("  - 你 ODS 经验里的数据治理 = 给文档打高质量的元数据标签")


# ========================================
# Part 4: FAISS — 工业级向量索引
# ========================================

print("\n=== Part 4: FAISS 基础 ===\n")

import faiss

# FAISS 的核心：Index（索引结构）
# 不同 Index 算法 = 精度 vs 速度的取舍

dim = 512  # 向量维度

# 方案A：暴力搜索（IndexFlatL2）— 100% 精确，慢
index_flat = faiss.IndexFlatL2(dim)     # L2 距离（欧几里得距离）
index_flat.add(large_embeddings[:1000])  # 只用 1000 条演示

start = time.time()
distances, indices = index_flat.search(query_vec.reshape(1, -1), k=5)
flat_time = time.time() - start
print(f"IndexFlatL2 (精确): {flat_time*1000:.1f} ms")
print(f"  Top-5 索引: {indices[0]}")

# 方案B：近似搜索（IndexIVFFlat）— 牺牲一点精度，快得多
# 新版本 FAISS 使用 index_factory 创建索引
nlist = min(100, 5000 // 39)  # 每个簇至少 39 个向量
index_ivf = faiss.index_factory(dim, f"IVF{nlist},Flat")  # 聚成 nlist 个簇

# FAISS 需要先训练（学习数据分布），再添加向量
index_ivf.train(large_embeddings[:5000])
index_ivf.add(large_embeddings[:5000])

start = time.time()
distances, indices = index_ivf.search(query_vec.reshape(1, -1), k=5)
ivf_time = time.time() - start
print(f"IndexIVFFlat (近似): {ivf_time*1000:.1f} ms")
print(f"  Top-5 索引: {indices[0]}")

if ivf_time > 0:
    print(f"\n  FAISS 精确 vs 近似: {flat_time/ivf_time:.1f}x 快")
else:
    print(f"\n  两种都极快（数据量小），大数据量下近似明显更快")

# 更多 FAISS Index 类型：
print("""
  IndexFlatL2      — 暴力搜索，100%精确，适合 < 10 万向量
  IndexIVFFlat     — 倒排索引，精度约 95%，适合百万级
  IndexHNSWFlat    — 图索引，精度约 97%，适合百万级（推荐）
  IndexPQ          — 压缩索引，省内存，适合亿级别
""")


# ========================================
# Part 5: Chroma / FAISS / Milvus 对比
# ========================================

print("=== Part 5: 方案对比 ===\n")

print("""
┌──────────┬──────────────┬──────────────┬──────────────┐
│          │    Chroma     │    FAISS     │   Milvus     │
├──────────┼──────────────┼──────────────┼──────────────┤
│ 类型      │ 向量数据库     │ 向量索引库    │ 向量数据库     │
│ 元数据过滤 │ ✅ 原生支持   │ ❌ 需自己实现  │ ✅ 原生支持   │
│ 持久化    │ ✅ 一键开启    │ ❌ 内存中     │ ✅ 分布式存储  │
│ 部署      │ pip install  │ pip install  │ Docker/K8s  │
│ 适合规模   │ < 100万      │ 无上限        │ > 100万      │
│ 学习难度  │ ⭐            │ ⭐⭐          │ ⭐⭐⭐       │
│ 适合阶段  │ 学习/原型     │ 钻研算法      │ 生产环境      │
└──────────┴──────────────┴──────────────┴──────────────┘

你的选择：
  学习阶段（现在）→ Chroma（pip install 完就能用）
  项目一（Day 29）  → Chroma（持久化，够用）
  项目二（Day 57）  → Chroma 足够，想挑战可换 Milvus Lite
  找工作面试       → 讲清楚 Chroma/FAISS/Milvus 三者区别
""")


print("*** Day 18 基础练习全部完成! ***")
print("\n关键结论：")
print("  1. 向量数据库 = ANN 索引，牺牲 1-2% 精度换 100 倍速度")
print("  2. Chroma 开箱即用，带元数据过滤（你的 ODS 经验直接复用）")
print("  3. FAISS 算法库，需自己搭配存储和过滤，工业常用")
print("  4. 学习用 Chroma，生产换 Milvus")
print("\n检验：把 Day 17 的文档块存入 Chroma 并检索（Part 2 已演示，项目一来真的）")
