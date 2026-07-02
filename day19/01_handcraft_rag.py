"""
Day 19：手搓 RAG 全链路（不用任何框架）

最重要的一天。今天你会亲手把 Day 15-18 学的全部串起来。

流水线（8 步）：
  1. 加载文档（PDF/Word/TXT/CSV）
  2. 递归切块
  3. Embedding 向量化
  4. 存入 Chroma
  5. 用户 query → 向量化
  6. Chroma 检索 Top-K
  7. 拼接 Prompt
  8. DeepSeek 生成回答 + 引用来源
"""
import os, json
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

# 加载 API Key
load_dotenv("E:/learn/day09/.env")
llm = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

# ============================================================
# 第 1 步：数据结构
# ============================================================

class Chunk(BaseModel):
    text: str
    index: int
    source: str = ""


# ============================================================
# 第 2 步：文档加载（Day 15）
# ============================================================

import fitz
from docx import Document as DocxDocument
import csv

def load_document(file_path: str) -> list[dict]:
    """
    加载单个文档，返回 [{content, source, file_type}]。
    提示：
      .pdf → fitz.open, page.get_text()
      .docx → DocxDocument, p.text
      .txt → read_text(encoding='utf-8')
      .csv → csv.DictReader → 转 Markdown 表格
    """
    # TODO: 根据扩展名加载文档
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
# 第 3 步：递归切块（Day 16）
# ============================================================

def chunk_text(text: str, source: str, chunk_size: int = 300) -> List[Chunk]:
    """
    递归切分：\\n\\n → \\n → 。→ 空格 → 硬切。
    提示：
      - 定义 separators = ['\\n\\n', '\\n', '。', ' ']
      - 先用第一个分隔符切，切出来都 <= chunk_size 就返回
      - 超长的片段用下一个分隔符递归切
      - 最后一级（空格还切不开）硬切
      - 每个 Chunk 带上 source
      - ⚠️ 索引用 len(chunks) 动态计算，不要用 enumerate 的 i（会重复）
    """
    # TODO: 实现递归切分
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
    
    result = []
    for p in pieces:
        if len(p) <= max_size:
            result.append(p)
        else:
            result.extend(_split_recursive(p, separators[1:], max_size))

    return result

# ============================================================
# 第 4 步：Embedding 向量化（Day 17）
# ============================================================

from sentence_transformers import SentenceTransformer

# 加载模型（已缓存，秒加载）
embed_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

def embed_text(texts: List[str]) -> List[List[float]]:
    return embed_model.encode(texts).tolist()

# ============================================================
# 第 5 步：存入 Chroma（Day 18）
# ============================================================

import chromadb

# 初始化 Chroma（指定 Embedding 函数，维度匹配 bge-small 的 512）
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="rag_demo")

def store_chunks(chunks: List[Chunk]):
    """
    把块存入 Chroma。
    提示：
      - ids = [f"chunk_{c.index}" for c in chunks]
      - documents = [c.text for c in chunks]
      - metadatas = [{'source': c.source, 'index': c.index} for c in chunks]
      - collection.add(ids=ids, documents=documents, metadatas=metadatas)
    """
    # TODO: 存入 Chroma
    texts = [chunk.text for chunk in chunks]
    embeddings = embed_text(texts)

    collection.add(
        ids=[f"{c.source}_chunk_{c.index}" for c in chunks],
        embeddings=embeddings,
        metadatas=[{"source": c.source, "index": c.index} for c in chunks],
        documents=texts
    )


# ============================================================
# 第 6 步：检索（Day 18）
# ============================================================

def search(query: str, top_k: int = 5):
    """
    用 Chroma 检索最相关的块。
    提示：
      - collection.query(query_texts=[query], n_results=top_k)
      - 返回 (documents, metadatas, distances)
    """
    # TODO: 检索
    query_emb = embed_text([query])[0]
    result = collection.query(query_embeddings=[query_emb], n_results=top_k)
    return (
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0]
    )


# ============================================================
# 第 7 步：拼接 Prompt（Day 12）
# ============================================================

def build_prompt(query: str, retrieved_chunks: List[str], sources: List[str]) -> str:
    """
    把检索结果拼成 LLM 的 Prompt。
    提示：
      - 用 f-string 把 chunks 拼成编号的参考资料
      - 格式类似：
        你是知识库助手。根据以下参考资料回答用户问题。
        如果参考资料中没有相关信息，请说"根据现有资料无法回答"。
        
        参考资料：
        [1] {chunk1}
        [2] {chunk2}
        
        用户问题：{query}
    """
    # TODO: 构建 Prompt
    references = []
    for i, (chunk, src) in enumerate(zip(retrieved_chunks, sources), 1):
        references.append(f"[{i}] {chunk} 来源:{src}")
    ref_text = "\n".join(references)
    return f"""
        你是知识库助手。根据以下参考资料回答用户问题。
        如果参考资料中没有相关信息，请说"根据现有资料无法回答"。
        
        参考资料：
        {ref_text}
        
        用户问题：{query}
        请回答（末尾列出引用来源）：
    """

# ============================================================
# 第 8 步：LLM 生成回答（Day 9）
# ============================================================

def generate_answer(prompt: str) -> str:
    """
    调用 DeepSeek 生成回答。
    提示：
      - llm.chat.completions.create(model='deepseek-chat', messages=[...])
      - temperature=0.0（知识问答要确定性）
      - 返回 response.choices[0].message.content
    """
    # TODO: 调 LLM
    resp = llm.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=500
    )
    return resp.choices[0].message.content


# ============================================================
# 流水线主函数
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
    import os
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    
    rag_pipeline(
        folder_path="E:/learn/day15/test_docs",
        query="总结一下会议的主题和决议"
    )
