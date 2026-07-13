"""
Day 27：个人知识库 — 把前三周的学习笔记变成可问答的知识库

目标：扫描 E:\\learn 下所有 .py 和 .md 文件，建 RAG，验证效果。

今天把 Day 15-26 学到的全部连起来，做一件真正有用的事：
  - 问"异步编程怎么写" → 从你的 day04 笔记里找到 asyncio 示例
  - 问"RAG检索怎么评估" → 从你的 day26 笔记里找到 RAGAS 指标
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

from dotenv import load_dotenv
load_dotenv("E:/learn/day09/.env")

from pathlib import Path
from typing import List
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI
import time


# ============================================================
# Step 1: 加载你的学习笔记
# ============================================================

print("=== Step 1: 加载学习笔记 ===\n")

def load_learn_files(base_dir: str = "E:/learn") -> List[dict]:
    """扫描 E:\\learn 下所有 .py 和 .md 文件"""
    files = []
    for f in Path(base_dir).rglob("*"):
        if f.suffix in {".py", ".md"} and f.is_file():
            content = f.read_text(encoding="utf-8", errors="ignore")
            # 跳过空文件
            if not content.strip():
                continue
            files.append({
                "source": str(f.relative_to(base_dir)).replace("\\", "/"),
                "content": content,
            })
    return files

files = load_learn_files()
print(f"找到 {len(files)} 个文件")
for f in files[:5]:
    print(f"  {f['source']}: {len(f['content'])} 字")
if len(files) > 5:
    print(f"  ... 还有 {len(files) - 5} 个文件\n")


# ============================================================
# Step 2: 切块 + Embedding + 入库（Day 15-18 的完整管线）
# ============================================================

print("=== Step 2: 建索引 ===\n")

def chunk_text(text: str, source: str, chunk_size: int = 500) -> List[dict]:
    """按段落切分，太长的按句子切（不用太复杂，py/md 文件有天然分段）"""
    separators = ["\n\n", "\n"]
    pieces = _split_recursive(text, separators, chunk_size)
    chunks = []
    for piece in pieces:
        if not piece.strip():
            continue
        chunks.append({
            "text": piece.strip(),
            "source": source,
            "index": len(chunks),
        })
    return chunks

def _split_recursive(text, separators, max_size):
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

# 切所有文件
all_chunks = []
for f in files:
    chunks = chunk_text(f["content"], f["source"])
    all_chunks.extend(chunks)

print(f"共 {len(all_chunks)} 个文本块")

# Embedding + 存入 Chroma
print("加载 Embedding 模型...")
embed_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

print("向量化 + 入库...")
embeddings = embed_model.encode([c["text"] for c in all_chunks]).tolist()

chroma_client = chromadb.Client()
try:
    chroma_client.delete_collection("day27_kb")
except Exception:
    pass
collection = chroma_client.create_collection(name="day27_kb")

# 分批插入（Chroma 限制）
batch_size = 500
for start in range(0, len(all_chunks), batch_size):
    end = min(start + batch_size, len(all_chunks))
    collection.add(
        ids=[f"{c['source']}_{c['index']}" for c in all_chunks[start:end]],
        embeddings=embeddings[start:end],
        documents=[c["text"] for c in all_chunks[start:end]],
        metadatas=[{"source": c["source"], "index": c["index"]} for c in all_chunks[start:end]],
    )

print(f"索引就绪: {collection.count()} 条\n")


# ============================================================
# Step 3: LLM 设置
# ============================================================

llm = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)



# ============================================================
# Step 4: RAG 问答
# ============================================================

def ask(question: str) -> str:
    """完整 RAG 问答：检索 → 拼 Prompt → LLM 生成"""
    # 检索
    q_emb = embed_model.encode(question).tolist()
    results = collection.query(query_embeddings=[q_emb], n_results=5)

    # 拼 Prompt
    refs = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        refs.append(f"【来源: {meta['source']}】\n{doc}")

    context = "\n\n".join(refs)

    system_prompt = """你是 AI 学习助手。根据提供的笔记内容回答用户问题。
- 如果笔记中有答案，引用笔记内容回答，并在末尾标注来源。
- 如果笔记中没有相关信息，就说"笔记中暂无相关内容"，不要编造。
- 回答简洁，不超过 200 字。"""

    resp = llm.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"参考资料：\n{context}\n\n问题：{question}"},
        ],
        temperature=0.0,
    )
    return resp.choices[0].message.content


# ============================================================
# Step 5: 测试
# ============================================================

print("=== Step 3: 测试你的知识库 ===\n")

questions = [
    "Python异步编程怎么写？",
    "余弦相似度怎么算的？",
    "BM25和向量检索有什么区别？",
    "什么是Function Calling？",
    "RAG检索怎么评估？",
    "向量数据库是什么？",
    "向量化的方式有哪些？",
]

for q in questions:
    print(f"问: {q}")
    start = time.time()
    answer = ask(q)
    elapsed = time.time() - start
    print(f"答: {answer}")
    print(f"  (耗时 {elapsed:.1f}s)\n")


# ============================================================
# Step 6: 你的设计思考题
# ============================================================

print("=== Step 4: 设计思考 ===\n")

print("""
如果把这份个人知识库持续改进，你可以考虑：

  1. 检索优化：现在只有向量检索。加 BM25 关键词检索能精准找到
     "Function Calling" 这样的术语（向量可能把它跟"工具调用"混淆）

  2. 文件类型感知：.py 是代码、.md 是笔记文���。代码块的检索
     可能需要不同的 chunk 策略（按函数/类切，而不是按段落）

  3. 时效性：你的笔记每天都在更新。做成定时重建索引的脚本，
     或者监听文件变更自动更新

  4. 多轮对话：如果第一轮答案宽泛，用户追问"能给我代码示例吗"，
     需要多轮记忆 + 二次检索

这个知识库可以变成你面试时的演示项目：
  "我自己做了一个学习笔记RAG系统，存了30天的AI学习笔记，
   能提问题上百个，找知识比手动翻文件夹快10倍。"
""")


print("*** Day 27 基础练习全部完成! ***")
print(f"\n你的个人知识库包含:")
print(f"  - {len(files)} 个源文件（笔记+代码）")
print(f"  - {len(all_chunks)} 个可检索的文本块")
print(f"  - 整个 RAG 管线加载+切块+索引+问答，共约 100 行代码")
print("\n今天你用自己写过的全部代码当数据源，建了一个真正有用的东西。")
