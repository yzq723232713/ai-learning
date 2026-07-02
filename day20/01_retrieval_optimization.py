"""
Day 20：检索质量优化 — 三种策略对比

Day 19 手搓的 RAG 只用向量检索，今天加两种优化：
  1. 多路召回（向量 + BM25 关键词）— 互补漏召回
  2. 重排序（Reranker）— 对召回结果精排
对比三种策略在 5 个问题上的效果。
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import csv, json, fitz
from pathlib import Path
from typing import List
from pydantic import BaseModel
from docx import Document as DocxDocument
from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb
from rank_bm25 import BM25Okapi
import jieba  # 中文分词（BM25 需要）

print("加载模型...")
embed_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

# Reranker：需要下载 bge-reranker-v2-m3（约 1GB），HF 被墙时可能失败
# 加载成功就启用 Reranker 策略，否则跳过
reranker = None
try:
    from sentence_transformers import CrossEncoder
    print("加载 Reranker...")
    reranker = CrossEncoder("C:/Users/qiang/.cache/modelscope/BAAI/bge-reranker-v2-m3")
    print("  Reranker 就绪（本地缓存）")
except Exception as e:
    print(f"  Reranker 加载失败，跳过: {type(e).__name__}")

chroma_client = chromadb.Client()
try:
    chroma_client.delete_collection("retrieval_demo")
except Exception:
    pass
collection = chroma_client.create_collection(name="retrieval_demo")
print("就绪\n")


# ============================================================
# 数据结构 + 加载 + 切块（复用 Day 19）
# ============================================================

class Chunk(BaseModel):
    text: str
    index: int
    source: str = ""


def load_document(file_path: str) -> list[dict]:
    path = Path(file_path)
    suffix = path.suffix.lower()
    source = path.name
    if suffix == ".pdf":
        doc = fitz.open(path)
        pages = [page.get_text() for page in doc]
        doc.close()
        return [{"content": "\n".join(pages).strip(), "source": source}]
    elif suffix == ".docx":
        doc = DocxDocument(path)
        content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [{"content": content, "source": source}]
    elif suffix == ".txt":
        return [{"content": path.read_text(encoding="utf-8").strip(), "source": source}]
    elif suffix == ".csv":
        with open(path, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if not rows: return [{"content": "", "source": source}]
        headers = list(rows[0].keys())
        lines = [" | ".join(headers)]
        lines.append(" | ".join(["---"] * len(headers)))
        for row in rows:
            lines.append(" | ".join(str(row[h]) for h in headers))
        return [{"content": "\n".join(lines), "source": source}]
    return [{"content": "", "source": source}]


def chunk_text(text: str, source: str, chunk_size: int = 300) -> List[Chunk]:
    separators = ["\n\n", "\n", "。", " "]
    pieces = _split_recursive(text, separators, chunk_size)
    chunks = []
    for piece in pieces:
        if len(piece) <= chunk_size:
            chunks.append(Chunk(text=piece, index=len(chunks), source=source))
        else:
            for j in range(0, len(piece), chunk_size):
                chunks.append(Chunk(text=piece[j:j+chunk_size], index=len(chunks), source=source))
    return chunks


def _split_recursive(text: str, separators: List[str], max_size: int) -> List[str]:
    if not separators:
        return [text]
    sep = separators[0]
    if sep not in text:
        return _split_recursive(text, separators[1:], max_size)
    pieces = [p.strip() for p in text.split(sep) if p.strip()]
    if not pieces:
        return [text]
    if all(len(p) <= max_size for p in pieces):
        return pieces
    result = []
    for p in pieces:
        if len(p) <= max_size:
            result.append(p)
        else:
            result.extend(_split_recursive(p, separators[1:], max_size))
    return result


# ============================================================
# 建库
# ============================================================

print("加载测试文档并建库...")
all_chunks = []
for f in Path("E:/learn/day15/test_docs").iterdir():
    if f.suffix.lower() not in {".pdf", ".docx", ".txt", ".csv"}:
        continue
    for doc in load_document(str(f)):
        all_chunks.extend(chunk_text(doc["content"], doc["source"]))

print(f"共 {len(all_chunks)} 个块")

# 存入 Chroma（向量库）
embeddings = embed_model.encode([c.text for c in all_chunks]).tolist()
collection.add(
    ids=[f"{c.source}_{c.index}" for c in all_chunks],
    embeddings=embeddings,
    documents=[c.text for c in all_chunks],
    metadatas=[{"source": c.source, "index": c.index} for c in all_chunks],
)

# 构建 BM25 索引（关键词库）
# jieba 分词后交给 BM25
tokenized_corpus = [list(jieba.cut(c.text)) for c in all_chunks]
bm25 = BM25Okapi(tokenized_corpus)
print("BM25 索引就绪\n")


# ============================================================
# 策略 1：纯向量检索（Day 19 的基线）
# ============================================================

def vector_search(query: str, top_k: int = 10) -> list[tuple]:
    """纯向量检索：query embed → Chroma L2距离 → Top-K"""
    q_emb = embed_model.encode(query).tolist()
    results = collection.query(query_embeddings=[q_emb], n_results=top_k)
    items = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        chunk_idx = meta["index"]
        items.append((doc, chunk_idx, -dist))  # 距离取负数（越小越相关 → 越负分数越高）
    return items


# ============================================================
# 策略 2：BM25 关键词检索
# ============================================================

def bm25_search(query: str, top_k: int = 10) -> list[tuple]:
    """纯 BM25 关键词检索"""
    tokenized_query = list(jieba.cut(query))
    scores = bm25.get_scores(tokenized_query)
    # 取 Top-K
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    items = []
    for idx in top_indices:
        items.append((all_chunks[idx].text, idx, float(scores[idx])))
    return items


# ============================================================
# 策略 3：混合检索（向量 + BM25）— RRF 融合
# ============================================================

def hybrid_search(query: str, top_k: int = 10, k: int = 60) -> list[tuple]:
    """
    向量检索和 BM25 检索的结果用 RRF（Reciprocal Rank Fusion）合并。
    向量擅长语义，BM25 擅长精确关键词，互补。
    """
    vec_results = vector_search(query, top_k=20)
    bm_results = bm25_search(query, top_k=20)

    # RRF 评分: score(doc) = Σ 1 / (k + rank)
    rrf_scores = {}
    for rank, (_, idx, _) in enumerate(vec_results, 1):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + rank)

    for rank, (_, idx, _) in enumerate(bm_results, 1):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + rank)

    # 按 RRF 分数降序
    sorted_indices = sorted(rrf_scores, key=rrf_scores.get, reverse=True)
    items = []
    for idx in sorted_indices[:top_k]:
        items.append((all_chunks[idx].text, idx, rrf_scores[idx]))
    return items


# ============================================================
# 策略 4：混合 + Reranker 精排
# ============================================================

def hybrid_with_reranker(query: str, top_k: int = 5) -> list[tuple]:
    """
    先用混合检索粗召回 Top-20，再用 Reranker 精排取 Top-K。
    如果 Reranker 没加载成功，退化为纯混合检索。
    """
    candidates = hybrid_search(query, top_k=20)
    if not candidates or reranker is None:
        return candidates[:top_k]  # Reranker 不可用时退化为混合检索

    # Reranker 打分
    pairs = [(query, c[0]) for c in candidates]
    rerank_scores = reranker.predict(pairs)

    # 按 Reranker 分数降序
    ranked = sorted(zip(candidates, rerank_scores), key=lambda x: x[1], reverse=True)
    items = []
    for (doc, idx, _), score in ranked[:top_k]:
        items.append((doc, idx, float(score)))
    return items


# ============================================================
# 三种策略对比测试
# ============================================================

test_queries = [
    "会议的主题是什么？",
    "有哪些产品功能？",
    "如何安装设备？",
    "故障怎么解决？",
    "张三在哪个部门？",
]

print("=" * 70)
print("三种检索策略对比")
print("=" * 70)

for query in test_queries:
    print(f"\n查询: 「{query}」")

    # 纯向量
    print("  [纯向量 Top-3]")
    for rank, (doc, idx, score) in enumerate(vector_search(query, top_k=3), 1):
        src = all_chunks[idx].source
        print(f"    {rank}. [{score:.4f}] {src}: {doc[:50]}...")

    # 混合检索
    print("  [混合检索 Top-3]")
    for rank, (doc, idx, score) in enumerate(hybrid_search(query, top_k=3), 1):
        src = all_chunks[idx].source
        print(f"    {rank}. [{score:.4f}] {src}: {doc[:50]}...")

    # 混合 + Reranker
    reranker_label = "混合+Reranker Top-3" if reranker else "混合+Reranker（未加载，同混合）"
    print(f"  [{reranker_label}]")
    for rank, (doc, idx, score) in enumerate(hybrid_with_reranker(query, top_k=3), 1):
        src = all_chunks[idx].source
        print(f"    {rank}. [{score:.4f}] {src}: {doc[:50]}...")


# ============================================================
# 三种策略总结
# ============================================================

print("\n\n" + "=" * 70)
print("三种策略对比总结")
print("=" * 70)

print("""
┌──────────────────┬──────────────────┬──────────────────┬──────────────────┐
│      策略         │      优势         │      劣势         │    最佳场景        │
├──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 纯向量检索        │ 语义理解强        │ 精确关键词可能漏   │ 模糊语义查询       │
│ 混合检索(RRF)     │ 语义+关键词互补    │ 多一步计算         │ 绝大多数 RAG      │
│ 混合+Reranker    │ 精度最高          │ 多一个模型，更慢   │ 高精度要求         │
└──────────────────┴──────────────────┴──────────────────┴──────────────────┘

实际工程建议：
  - 项目一（Day 29）: 纯向量检索 → 先跑通，再优化
  - 项目二（Day 57）: 混合检索（向量+BM25）→ RRF 融合
  - 生产环境: 混合+Reranker → 粗召回 20 条，精排取 5 条
""")


print("*** Day 20 基础练习全部完成! ***")
print("\n关键结论：")
print("  1. 向量检索（语义）+ BM25（关键词）= 互补漏召回")
print("  2. RRF 融合比简单并集好——两个检索都排前面的文档得分更高")
print("  3. Reranker 对召回结果重新打分，比余弦相似度更精准")
print("  4. 三步递进：向量 → 混合 → 混合+Reranker，成本和精度递增")
