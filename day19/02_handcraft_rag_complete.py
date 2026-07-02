"""
Day 19：手搓 RAG 全链路 — 完整参考实现

8 步：加载 → 切块 → Embedding → 存库 → 检索 → 拼Prompt → LLM生成
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import csv, json
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import fitz
from docx import Document as DocxDocument
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv("E:/learn/day09/.env")
llm = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

# bge-small 已缓存，秒加载
print("加载 Embedding 模型...")
embed_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

# Chroma 不用内置 Embedding，我们自己算
print("初始化 Chroma...")
chroma_client = chromadb.Client()
try:
    chroma_client.delete_collection("rag_demo")
except Exception:
    pass
collection = chroma_client.create_collection(name="rag_demo")
print("准备就绪\n")


# ============================================================
# 数据结构
# ============================================================

class Chunk(BaseModel):
    text: str
    index: int
    source: str = ""


# ============================================================
# 文档加载
# ============================================================

def load_document(file_path: str) -> list[dict]:
    path = Path(file_path)
    suffix = path.suffix.lower()
    source = path.name

    if suffix == ".pdf":
        doc = fitz.open(path)
        pages = [page.get_text() for page in doc]
        doc.close()
        content = "\n".join(pages).strip()
        return [{"content": content, "source": source, "file_type": "pdf"}]

    elif suffix == ".docx":
        doc = DocxDocument(path)
        content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [{"content": content, "source": source, "file_type": "docx"}]

    elif suffix == ".txt":
        content = path.read_text(encoding="utf-8").strip()
        return [{"content": content, "source": source, "file_type": "txt"}]

    elif suffix == ".csv":
        with open(path, "r", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return [{"content": "", "source": source, "file_type": "csv"}]
        headers = list(rows[0].keys())
        lines = [" | ".join(headers)]
        lines.append(" | ".join(["---"] * len(headers)))
        for row in rows:
            lines.append(" | ".join(str(row[h]) for h in headers))
        return [{"content": "\n".join(lines), "source": source, "file_type": "csv"}]

    raise ValueError(f"不支持: {suffix}")


# ============================================================
# 递归切块
# ============================================================

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
# Embedding
# ============================================================

def embed_texts(texts: List[str]) -> List[List[float]]:
    return embed_model.encode(texts).tolist()


# ============================================================
# 存入 Chroma
# ============================================================

def store_chunks(chunks: List[Chunk]):
    texts = [c.text for c in chunks]
    # print(f"texts的形状：{texts}")
    embeddings = embed_texts(texts)
    # print(f"embeddings的形状：{embeddings}")
    # ID 包含文件名前缀，避免不同文档的 chunk_0 冲突
    collection.add(
        ids=[f"{c.source}_chunk_{c.index}" for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"source": c.source, "index": c.index} for c in chunks],
    )


# ============================================================
# 检索
# ============================================================

def search(query: str, top_k: int = 5):
    query_emb = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)
    return (
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )


# ============================================================
# 拼接 Prompt
# ============================================================

def build_prompt(query: str, retrieved_chunks: List[str], sources: List[str]) -> str:
    references = []
    for i, (chunk, src) in enumerate(zip(retrieved_chunks, sources), 1):
        references.append(f"[{i}] {chunk}\n   来源: {src}")
    ref_text = "\n".join(references)

    return f"""你是知识库助手。根据以下参考资料回答用户问题。
如果参考资料中没有相关信息，请明确说"根据现有资料无法回答"，不要编造。

参考资料：
{ref_text}

用户问题：{query}

请回答（末尾列出引用来源）："""


# ============================================================
# LLM 生成
# ============================================================

def generate_answer(prompt: str) -> str:
    resp = llm.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=500,
    )
    return resp.choices[0].message.content


# ============================================================
# 主流水线
# ============================================================

def rag_pipeline(folder_path: str, query: str):
    print("=" * 60)
    print(f"查询: 「{query}」")

    # Step 2: 加载文档
    print("\n[Step 2] 加载文档...")
    all_chunks = []
    for file in Path(folder_path).iterdir():
        if file.suffix.lower() not in {".pdf", ".docx", ".txt", ".csv"}:
            continue
        docs = load_document(str(file))
        for doc in docs:
            chunks = chunk_text(doc["content"], doc["source"])
            all_chunks.extend(chunks)
    print(f"  共 {len(all_chunks)} 个块")
    for c in all_chunks[:3]:
        print(f"  块{c.index} [{c.source}]: {c.text[:50]}...")

    # Step 4: 存库（Embedding 在 store_chunks 内部完成）
    print("\n[Step 4-5] 向量化 + 存入 Chroma...")
    store_chunks(all_chunks)
    print(f"  已存入 {collection.count()} 条")

    # Step 6: 检索
    print("\n[Step 6] 检索相关块...")
    docs, metas, dists = search(query, top_k=3)
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists), 1):
        print(f"  {i}. [dist={dist:.4f}] {meta['source']}")
        print(f"     {doc[:80]}...")

    # Step 7: 拼接 Prompt
    print("\n[Step 7] 拼接 Prompt...")
    sources = [f"{m['source']} (块{m['index']})" for m in metas]
    prompt = build_prompt(query, docs, sources)
    print(f"  Prompt: {len(prompt)} 字符")

    # Step 8: LLM 生成
    print("\n[Step 8] DeepSeek 生成回答...")
    answer = generate_answer(prompt)

    print(f"\n{'=' * 60}")
    print(f"回答:\n{answer}")
    print(f"{'=' * 60}")
    return answer


# ============================================================
# 测试
# ============================================================
if __name__ == "__main__":
    rag_pipeline(
        folder_path="E:/learn/day15/test_docs",
        query="总结一下会议的主题和决议"
    )
