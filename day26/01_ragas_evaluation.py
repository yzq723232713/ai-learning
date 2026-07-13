"""
Day 26：RAGAS 评估 — 别瞎优化，先看分数

RAG 的优化是黑暗中的摸索？不——先评估，找到短板，再针对性改进。
RAGAS 是专门评估 RAG 系统的框架，4 个指标覆盖了整条流水线。
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

from dotenv import load_dotenv
load_dotenv("E:/learn/day09/.env")
import jieba

# ============================================================
# Part 1: 为什么要评估
# ============================================================

print("=== Part 1: 为什么需要评估 ===\n")

print("""
RAG 系统有 3 个环节可能出问题：

  1. 检索阶段：搜到的文档对不对？
     → context_precision / context_recall
  2. 生成阶段：LLM 有没有根据文档回答（还是瞎编）？
     → faithfulness
  3. 端到端：最终回答跟用户问题切题吗？
     → answer_relevancy

没有评估的优化 = 盲人摸象。
加了新的检索策略 → 回答变好了吗？不知道。
换了 Prompt → 幻觉减少了吗？不知道。
""")


# ============================================================
# Part 2: 4 个评估指标
# ============================================================

print("\n=== Part 2: RAGAS 4 个指标 ===\n")

print("""
┌─────────────────────┬──────────────────────────────────────┬──────────────────────┐
│      指标            │             测什么                    │     理想值            │
├─────────────────────┼──────────────────────────────────────┼──────────────────────┤
│ context_precision   │ 召回的 N 篇文档里，有多少是真正相关？     │ 高（> 0.7）           │
│ context_recall      │ 该召回的文档，系统都召回来了没？         │ 高（> 0.7）           │
│ faithfulness        │ LLM 的回答是否基于召回的文档（不瞎编）？ │ 高（> 0.8）           │
│ answer_relevancy    │ 最终回答是否切中用户问题？              │ 高                     │
└─────────────────────┴──────────────────────────────────────┴──────────────────────┘

类比（帮你记）：
  context_precision = 「搜出来的一堆里，有多少是干货」
  context_recall    = 「该搜到的，都搜到了吗」
  faithfulness      = 「LLM 有没有胡说八道」
  answer_relevancy  = 「最后答的是不是用户想问的」
""")


# ============================================================
# Part 3: 手写一个简易评估（理解原理，不依赖 ragas 安装）
# ============================================================

print("=== Part 3: 手写评估（理解 RAGAS 底层原理）===\n")

# 准备评估数据：我们手动标注几个 question + ground_truth + contexts + answer
eval_data = [
    {
        "question": "会议的主题是什么？",
        "ground_truth": "会议主题是2024年Q2产品规划",
        "contexts": [
            "会议主题: 2024年Q2产品规划 时间: 2024年3月15日",  # ✅ 相关
            "参会人: 张三(研发)、李四(产品)、王五(测试)",           # ⚠️ 部分相关
            "产品名称: 智能温控器 X-100",                          # ❌ 无关
        ],
        "answer": "会议主题为2024年Q2产品规划，参会人包括张三、李四和王五。"
    },
    {
        "question": "E01错误代码怎么解决？",
        "ground_truth": "E01表示温度传感器故障，需断电重启，若仍存在则联系售后",
        "contexts": [
            "问题一：设备显示E01错误代码。原因：温度传感器故障。解决方案：断电重启",  # ✅
            "问题二：Wi-Fi连接不稳定。原因：路由器距离过远",                         # ❌
            "产品采用高精度温度传感器，精度可达±0.5°C",                               # ⚠️
        ],
        "answer": "E01错误表示传感器故障，重启设备即可解决。"
    },
    {
        "question": "张三在哪个部门？",
        "ground_truth": "张三在研发部门",
        "contexts": [
            "张三, 研发, 2022-01-15, 15000",   # ✅
            "李四, 产品, 2021-06-20, 18000",   # ❌
            "王五, 测试, 2023-03-10, 12000",   # ❌
        ],
        "answer": "张三在研发部门，于2022年1月15日入职。"
    },
]


# ---------- 指标 1: Context Precision（精确率，手写版）----------
# 定义: 检索到的文档中，相关文档的比例
# 简化为: relevant_count / total_retrieved_count

def context_precision(contexts: list[str], ground_truth: str) -> float:
    """判断每个检索到的文档是否包含 ground_truth 中的关键词"""
    keywords = set(jieba.cut(ground_truth.lower()))
    relevant = 0
    for ctx in contexts:
        ctx_words = set(jieba.cut(ctx.lower()))
        if len(keywords & ctx_words) >= 2:
            relevant += 1
    return relevant / len(contexts) if contexts else 0


# ---------- 指标 2: Context Recall（召回率，手写版）----------
# 定义: ground_truth 里的信息，多少出现在了检索到的文档中
# 简化为: ground_truth 关键词被 contexts 覆盖的比例

def context_recall(contexts: list[str], ground_truth: str) -> float:
    keywords = set(jieba.cut(ground_truth.lower()))
    if not keywords:
        return 0
    all_ctx_text = jieba.lcut(" ".join(contexts).lower())
    matched = sum(1 for kw in keywords if kw in all_ctx_text)
    return matched / len(keywords)


# ---------- 指标 3: Faithfulness（忠实度，手写版）----------
# 定义: answer 中的陈述句有多少能在 contexts 中找到依据
# 简化为: answer 关键词被 contexts 覆盖的比例

def faithfulness(contexts: list[str], answer: str) -> float:
    all_ctx = " ".join(contexts).lower()
    ans_words = jieba.lcut(answer.lower())
    if not ans_words:
        return 0
    stopwords = {"的", "了", "在", "和", "是", "等", "中", "为", "于", "、"}
    meaningful = [w for w in ans_words if w not in stopwords and len(w) > 1]
    if not meaningful:
        return 0
    matched = sum(1 for w in meaningful if w in all_ctx)
    return matched / len(meaningful)


# ---------- 指标 4: Answer Relevancy（切题度，手写版）----------
# 定义: 回答跟问题的关联度
# 简化为: question 和 answer 的关键词重叠度

def answer_relevancy(question: str, answer: str) -> float:
    q_words = set(jieba.cut(question.lower()))
    a_words = set(jieba.cut(answer.lower()))
    if not q_words or not a_words:
        return 0
    overlap = q_words & a_words
    return len(overlap) / len(q_words)


# ---------- 跑评估 ----------
print("评估结果（注：手写简化版，仅展示原理。生产用 RAGAS 的 LLM 评估更准）\n")

print(f"{'问题':<30s} {'Prec':>5s} {'Rec':>5s} {'Faith':>5s} {'Relev':>5s}")
print("-" * 55)

for item in eval_data:
    prec = context_precision(item["contexts"], item["ground_truth"])
    rec = context_recall(item["contexts"], item["ground_truth"])
    faith = faithfulness(item["contexts"], item["answer"])
    relev = answer_relevancy(item["question"], item["answer"])
    
    q_short = item["question"][:28]
    print(f"{q_short:<30s} {prec:>5.2f} {rec:>5.2f} {faith:>5.2f} {relev:>5.2f}")

# 平均分
avg_prec = sum(context_precision(d["contexts"], d["ground_truth"]) for d in eval_data) / len(eval_data)
avg_rec = sum(context_recall(d["contexts"], d["ground_truth"]) for d in eval_data) / len(eval_data)
avg_faith = sum(faithfulness(d["contexts"], d["answer"]) for d in eval_data) / len(eval_data)
avg_relev = sum(answer_relevancy(d["question"], d["answer"]) for d in eval_data) / len(eval_data)

print("-" * 55)
print(f"{'平均':<30s} {avg_prec:>5.2f} {avg_rec:>5.2f} {avg_faith:>5.2f} {avg_relev:>5.2f}")


# ============================================================
# Part 4: 分析评估结果 → 指导优化方向
# ============================================================

print("\n\n=== Part 4: 从分数到行动 ===\n")

print("""
评估结果的解读和行动：

  context_precision 低 → 检索不精准，召回了很多无关文档
    → 优化方向: 加 Reranker、调大 chunk_overlap、改进 Embedding

  context_recall 低 → 该搜出来的没搜出来
    → 优化方向: 多路召回(BM25+向量)、Multi-query、调小 chunk_size

  faithfulness 低 → LLM 在编造信息
    → 优化方向: 改进 Prompt（加"不知道就说不知道"）、加大检索 top_k

  answer_relevancy 低 → 回答跑题
    → 优化方向: 改进 System Prompt、检查 Prompt 中 context 和 question 的比例

你的 RAG 系统的典型劣势（基于 Day 19/20 的观察）：
  - faithfulness 可能偏低：测试文档少，LLM 会用自己知识补充
  - context_recall 可能偏低：单一向量检索，BM25 还没充分发挥
""")


# ============================================================
# Part 5: RAGAS 生产环境用法（概念，不跑）
# ============================================================

print("=== Part 5: RAGAS 生产环境正确用法 ===\n")

print("""
生产中用 RAGAS 时要这样写（今天不跑，手写版已理解原理）：

  from ragas import evaluate
  from ragas.metrics import context_precision, context_recall, faithfulness, answer_relevancy
  from datasets import Dataset

  # 准备 50+ 条标注数据
  dataset = Dataset.from_dict({
      "question": [...],
      "ground_truth": [...],
      "contexts": [...],   # 每条问题对应的检索结果列表
      "answer": [...],
  })

  result = evaluate(dataset, metrics=[context_precision, context_recall, faithfulness, answer_relevancy])
  print(result)

关键：RAGAS 内部用 LLM 来判断"这段文档是否相关"，而不是你手写的关键词匹配。
这也是为什么 RAGAS 的评估比手写版精准——它真的"读"了文档和答案，不是靠关键词。
""")


print("*** Day 26 基础练习全部完成! ***")
print("\n关键结论：")
print("  1. RAG 优化前先评估：precision/recall/faithfulness/relevancy 找短板")
print("  2. 手写关键词评估给直觉，生产用 RAGAS 的 LLM 评估给精度")
print("  3. 今天手写的 4 个函数就是 RAGAS 的底层数学逻辑")
print("  4. 项目一优化前先跑这几个指标，别瞎改")
