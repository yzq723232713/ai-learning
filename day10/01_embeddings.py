"""
Day 10：Embedding 理解 — RAG 最重要的基础

Embedding = 把任意文本变成一个固定长度的浮点数向量
语义相近 → 向量距离近；语义不同 → 距离远
"""
import numpy as np
from sentence_transformers import SentenceTransformer

# 加载中文 Embedding 模型（首次运行会下载，约 100MB）
print("加载模型 BAAI/bge-small-zh-v1.5 ...")
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
print("模型加载完成\n")

# ========================================
# Part 1: 什么是 Embedding — 把文本变成数字
# ========================================

print("=== Part 1: 文本 → 向量 ===\n")

texts = [
    "你好世界",
    "Python是一门编程语言",
    "今天天气真好",
]

embeddings = model.encode(texts)

for text, emb in zip(texts, embeddings):
    print(f"文本: {text}")
    print(f"  维度: {len(emb)}（一个 512 维的向量）")
    print(f"  前5个值: {emb[:5]}")
    print(f"  后5个值: {emb[-5:]}")
    print()

# 512 个浮点数 = 这段文本在"语义空间"中的坐标
# 每个数字没有物理含义，但空间中的"距离"代表语义远近


# ========================================
# Part 2: 余弦相似度 — 怎么衡量"语义接近"
# ========================================

print("=== Part 2: 余弦相似度 ===\n")

def cos_sim(v1, v2):
    """余弦相似度：-1 到 1，越接近 1 越相似"""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# 三组文本
a = "我喜欢吃苹果"
b = "苹果很好吃"
c = "今天下雨了"

va, vb, vc = model.encode([a, b, c])

print(f"「{a}」vs「{b}」→ 余弦相似度: {cos_sim(va, vb):.4f}  ← 语义相近，值高")
print(f"「{a}」vs「{c}」→ 余弦相似度: {cos_sim(va, vc):.4f}  ← 语义不相关，值低")
print(f"「{b}」vs「{c}」→ 余弦相似度: {cos_sim(vb, vc):.4f}  ← 同样不相关")

# 关键结论：相似度高低不由"有没有相同的字"决定，由语义决定
print("\n验证：不是靠关键字匹配")
d = "我不喜欢水果"
vd = model.encode(d)
print(f"「{a}」vs「{d}」→ 余弦相似度: {cos_sim(va, vd):.4f}")
print("虽然两个字面上都有'苹果'，但「不喜欢水果」和「喜欢吃苹果」语义不接近")


# ========================================
# Part 3: 相似文档检索 — RAG 的核心操作
# ========================================

print("\n=== Part 3: 相似文档检索 ===\n")

# 模拟一个文档库
documents = [
    "Python的列表推导式可以简洁地创建列表",
    "今天中午食堂有红烧肉和西红柿炒蛋",
    "深度学习模型需要大量GPU进行训练",
    "食堂二楼的麻辣烫很好吃",
    "asyncio是Python的异步编程库",
    "大语言模型使用Transformer架构",
    "如何用Python发送HTTP请求",
]

query = "Python异步编程怎么做"

print(f"用户查询: 「{query}」\n")

# 把所有文档和查询一起 encode（比逐个快）
all_texts = [query] + documents
all_embs = model.encode(all_texts)

query_emb = all_embs[0]
doc_embs = all_embs[1:]

# 计算每个文档与查询的相似度
scores = []
for i, (doc, emb) in enumerate(zip(documents, doc_embs)):
    score = cos_sim(query_emb, emb)
    scores.append((score, doc))

# 按相似度降序排列
scores.sort(reverse=True, key=lambda x: x[0])

print("检索结果（按相似度从高到低）:")
for rank, (score, doc) in enumerate(scores, 1):
    bar = "█" * int(score * 30)
    print(f"  {rank}. [{score:.4f}] {doc}  {bar}")

print("\n与查询最相关的是「asyncio」和「Python发送HTTP请求」")
print("跟 Python 无关的「食堂」和「深度学习」排在最后")
print("这就是 RAG 检索的核心：用 Embedding 相似度找最相关的文档")


# ========================================
# Part 4: Embedding 的关键特性
# ========================================

print("\n=== Part 4: Embedding 的关键特性 ===\n")

# 特性1：向量可以加减（词向量的经典特性，句子向量弱一些但方向存在）
print("向量运算示例：")
king = model.encode("国王")
man = model.encode("男人")
woman = model.encode("女人")

queen_approx = king - man + woman   # 国王 - 男人 + 女人 ≈ 女王
queen = model.encode("女王")
print(f"  国王 - 男人 + 女人 ≈ 女王？")
print(f"  余弦相似度: {cos_sim(queen_approx, queen):.4f}")
print(f"  （值越高说明这个向量运算方向是对的）")

# 特性2：Embedding 模型对「同一个意思的不同说法」不敏感
print("\n语义等价测试：")
phrases = [
    "我喜欢学习Python",
    "Python是我爱学的编程语言",
    "我讨厌吃苹果",
    "苹果是我厌恶的水果",
]
embs = model.encode(phrases)
print(f"  「喜欢学Python」vs「Python是我爱学的」:  {cos_sim(embs[0], embs[1]):.4f}")
print(f"  「讨厌吃苹果」vs「苹果是我厌恶的」:    {cos_sim(embs[2], embs[3]):.4f}")
print(f"  「喜欢学Python」vs「讨厌吃苹果」:      {cos_sim(embs[0], embs[2]):.4f}")


print("\n\n*** Day 10 基础练习全部完成! ***")
print("\n关键结论：")
print("  1. Embedding = 文本 → 512维（或更多）浮点数向量")
print("  2. 语义相近 → 余弦相似度接近 1；无关 → 接近 0 或负")
print("  3. 检索就是：算 query embedding → 跟文档库所有向量比相似度 → 取最像的")
print("  4. 本地模型免费、无需API、可离线用")
print("\n下一步检验：写一个脚本，用 Embedding 对文档排序（Part 3 已经演示了）")
