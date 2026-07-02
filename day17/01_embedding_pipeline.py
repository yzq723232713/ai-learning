"""
Day 17：Embedding 模型选型 + 向量化
把 Day 16 切好的块变成向量，然后用查询检索最相关的块。

今天用已缓存的 bge-small-zh-v1.5（Day 10 下载过，秒加载）
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
import time

# 复用 Day 16 的 Chunk 定义和示例文档
from pydantic import BaseModel

class Chunk(BaseModel):
    text: str
    index: int
    char_start: int = 0
    char_end: int = 0

# 复用 Day 16 的递归切分
def chunk_recursive_simple(text: str, chunk_size: int = 300, separators: List[str] = None) -> List[Chunk]:
    if separators is None:
        separators = ["\n\n", "\n", "。", " "]
    chunks = _split_by_seps(text, separators, chunk_size)
    result = []
    for idx, chunk_text in enumerate(chunks):
        if len(chunk_text) <= chunk_size:
            result.append(Chunk(text=chunk_text, index=idx))
        else:
            for i in range(0, len(chunk_text), chunk_size):
                result.append(Chunk(text=chunk_text[i:i + chunk_size], index=len(result)))
    return result

def _split_by_seps(text, separators, max_size):
    if not separators:
        return [text]
    sep = separators[0]
    if sep not in text:
        return _split_by_seps(text, separators[1:], max_size)
    pieces = [p for p in text.split(sep) if p.strip()]
    if all(len(p) <= max_size for p in pieces):
        return pieces
    result = []
    for p in pieces:
        if len(p) <= max_size:
            result.append(p)
        else:
            result.extend(_split_by_seps(p, separators[1:], max_size))
    return result


# ========================================
# Part 1: 主流 Embedding 模型一览
# ========================================

print("=== Part 1: 主流 Embedding 模型选型 ===\n")

print("""
┌──────────────────────────┬────────┬────────┬──────────────────┐
│ 模型                      │ 维度    │ 大小    │ 特点              │
├──────────────────────────┼────────┼────────┼──────────────────┤
│ text-embedding-3-small   │ 1536   │ API    │ OpenAI，便宜，英文  │
│ bge-large-zh-v1.5        │ 1024   │ ~600MB │ 中文最强，本地部署  │
│ bge-small-zh-v1.5        │ 512    │ ~100MB │ 中文，轻量，已缓存  │
│ m3e-base                 │ 768    │ ~400MB │ 开源中文，可商用    │
│ stella-base-zh           │ 768    │ ~200MB │ 轻量中文           │
└──────────────────────────┴────────┴────────┴──────────────────┘

选择建议：
  - 学习/开发: bge-small-zh（已缓存，本地跑，免费无限次）
  - 生产中文: bge-large-zh-v1.5 或 m3e-large（精准）
  - 生产英文: text-embedding-3-small（API 调用，免运维）
""")

print("今天用已缓存的 bge-small-zh-v1.5 (512维)")
print("加载模型...")
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
print("模型就绪\n")


# ========================================
# Part 2: 加载文档 → 切块 → 向量化
# ========================================

print("=== Part 2: 文档 → 切块 → 向量化 ===\n")

# 复用 Day 16 的测试文档
SAMPLE_TEXT = """
智能温控器 X-100 产品手册

第一章 产品概述
智能温控器 X-100 是一款面向家庭和办公场景的智能温度控制设备。
该产品支持Wi-Fi连接，可通过手机APP远程控制室内温度。

第二章 安装指南
第一步，使用水平尺在墙面标记安装位置。第二步，用电钻打孔。
第三步，将膨胀螺栓插入孔中。第四步，将设备背板对准螺栓固定。
第五步，连接电源线：火线接L端子，零线接N端子。
注意：接线前务必断开总电源！

第三章 APP连接
安装完成后，打开手机蓝牙和Wi-Fi。下载"智能家"APP。
点击"添加设备"，按照屏幕提示完成设备配对。

第四章 故障排除
问题一：设备显示"E01"错误代码。原因：温度传感器故障。
解决方案：断电重启设备，若问题依然存在，请联系售后服务。

问题二：Wi-Fi连接不稳定。原因：路由器距离过远。
解决方案：将路由器移至距离设备5米以内。

问题三：APP显示设备离线。解决方案：长按模式键10秒恢复出厂设置。
"""

# 切块
chunks = chunk_recursive_simple(SAMPLE_TEXT, chunk_size=300)
print(f"切出 {len(chunks)} 个块\n")

# 批量向量化（比一个个调快 10 倍）
start = time.time()
chunk_texts = [c.text for c in chunks]
chunk_embeddings = model.encode(chunk_texts, show_progress_bar=False)
elapsed = time.time() - start

print(f"向量化完成！耗时: {elapsed:.2f}秒")
print(f"向量维度: {chunk_embeddings.shape[1]} 维")
print(f"向量矩阵形状: {chunk_embeddings.shape}  ← ({len(chunks)}块 × 512维)")

for i, (chunk, emb) in enumerate(zip(chunks, chunk_embeddings)):
    text_preview = chunk.text[:50].replace("\n", " ")
    print(f"  块{i}: [{text_preview}...] → {len(emb)}维向量")


# ========================================
# Part 3: 检索 — 输入查询，找最相关块
# ========================================

print("\n\n=== Part 3: 检索 — 查询 vs 所有块 ===\n")

def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def search(query: str, model, chunks: List[Chunk], chunk_embs, top_k: int = 5):
    """输入查询，返回 Top-K 相关块"""
    query_emb = model.encode(query)

    scores = []
    for i, (chunk, emb) in enumerate(zip(chunks, chunk_embs)):
        score = cos_sim(query_emb, emb)
        scores.append((score, i, chunk))

    scores.sort(reverse=True, key=lambda x: x[0])
    return scores[:top_k]


# 测试不同的查询
queries = [
    "怎么安装设备？",
    "APP怎么连接？",
    "E01错误代码是什么意思？",
    "产品有什么功能？",
]

for query in queries:
    print(f"查询: 「{query}」")
    results = search(query, model, chunks, chunk_embeddings, top_k=3)
    for rank, (score, idx, chunk) in enumerate(results, 1):
        bar = "█" * int(score * 20)
        preview = chunk.text[:60].replace("\n", " ")
        print(f"  {rank}. [{score:.4f}] 块{idx}: {preview}  {bar}")
    print()


# ========================================
# Part 4: 维度 vs 精度 — 不同模型的取舍
# ========================================

print("=== Part 4: 维度 vs 精度 ===\n")

print("""
维度越高的模型：
  优点: 能捕捉更多语义细节，检索更精准
  缺点: 向量存储空间大、计算慢、API 更贵

维度越低的模型：
  优点: 快、省空间、便宜
  缺点: 语义粗糙，可能把不相关的内容排在前面

实际取舍:
  少量文档(< 1000份) → bge-small (512维) 足够
  海量文档 + 高精度 → bge-large (1024维) 或 m3e-large
  英文为主 → text-embedding-3-small (1536维 API)
  完全离线 → m3e-base (768维)

你现在 512 维做练习完全够用，项目二再换 1024 维的也不迟。
""")


print("*** Day 17 基础练习全部完成! ***")
print("\n关键结论：")
print("  1. 文档切块后，用 model.encode() 批量转向量（一次调比逐个快 10 倍）")
print("  2. 检索 = query向量 vs 所有块向量 → 余弦相似度排序 → 取 Top-K")
print("  3. 选模型 = 维度、精度、速度、价格四者权衡")
print("  4. bge-small (512维) 学习够用，生产换 bge-large (1024维)")
