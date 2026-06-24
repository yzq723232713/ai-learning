"""
Day 14：第2周复习 —— 从 Token 到 Function Calling

本周你完成了 AI 应用开发最基础的一周。
下面的自检清单，全部能用大白话讲通 → 本周过关。
"""

# ============================================================
# 本周知识地图
# ============================================================

print("""
╔══════════════════════════════════════════════════════════════╗
║                   第 2 周 · 知识地图                         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Day 8   Token 是什么                                        ║
║           ↓                                                  ║
║  Day 9   第一次调 API（DeepSeek）                             ║
║           ↓                                                  ║
║  Day 10  Embedding = 文本 → 向量                             ║
║           ↓                                                  ║
║  Day 11  Transformer 架构（注意力机制）                       ║
║           ↓                                                  ║
║  Day 12  Prompt Engineering 四大技巧                         ║
║           ↓                                                  ║
║  Day 13  Function Calling（模型调用你的函数）                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

# ============================================================
# Day 8 自检：Token
# ============================================================

print("=" * 60)
print("Day 8 自检：Token")
print("=" * 60)
print()

questions_day8 = [
    "1. Token 和「字」有什么区别？",
    "2. 为什么中文的 token 效率比英文低？",
    "3. API 按什么计费？输入 token 和输出 token 哪个贵？",
    "4. '你好世界' 在 GPT 的 tokenizer 下大概是几个 token？为什么？",
]

for q in questions_day8:
    print(q)

print("""
答案自查：
1. Token 是 LLM 认识的最小文本单位，一个字可能 1 个 token 也可能被拆成多个
2. GPT 词汇表以英文为主，中文常见字是独立 token，不常见的被拆成字节
3. 按 token 计费；输出 token 更贵（GPT-4: 输入 $0.01/1K, 输出 $0.03/1K）
4. 4个汉字 → 5个 token（世 被拆成了 2 个 token）
""")


# ============================================================
# Day 9 自检：API 调用
# ============================================================

print("\n" + "=" * 60)
print("Day 9 自检：API 调用")
print("=" * 60)
print()

questions_day9 = [
    "1. temperature=0 和 temperature=1 有什么区别？分别用在哪？",
    "2. System Prompt 和 User Prompt 分别干什么？",
    "3. stream=True 的作用是什么？",
    "4. DeepSeek API 的 base_url 为什么要改成 https://api.deepseek.com？",
]

for q in questions_day9:
    print(q)

print("""
答案自查：
1. temp=0 确定性强（分类/提取）; temp=1 创造性（写作/头脑风暴）
2. System Prompt 设定角色和边界；User Prompt 是具体问题
3. 流式逐字返回，不用等完整回复 → 用户体验好
4. OpenAI SDK 默认连 OpenAI 服务器，改 base_url 后指向 DeepSeek
""")


# ============================================================
# Day 10 自检：Embedding
# ============================================================

print("\n" + "=" * 60)
print("Day 10 自检：Embedding")
print("=" * 60)
print()

questions_day10 = [
    "1. Embedding 是什么？512 维是什么概念？",
    "2. 余弦相似度怎么算？它代表什么？",
    "3. 「我喜欢吃苹果」和「苹果很好吃」的相似度应该高还是低？",
    "4. RAG 的检索是 Embedding 怎么用的？",
]

for q in questions_day10:
    print(q)

print("""
答案自查：
1. Embedding = 把文本变成一个固定长度的浮点数数组（512维=512个float）
2. cos_sim = dot(v1,v2) / (norm(v1)*norm(v2)); 值越接近1语义越近
3. 高（语义相同）
4. query → Embedding → 跟文档库所有向量算余弦相似度 → 取 Top-K
""")


# ============================================================
# Day 11 自检：Transformer
# ============================================================

print("\n" + "=" * 60)
print("Day 11 自检：Transformer")
print("=" * 60)
print()

questions_day11 = [
    "1. Transformer 和 RNN 的本质区别是什么？",
    "2. Attention 在干什么？（用大白话说）",
    "3. 为什么 GPT 是 Decoder-only？",
    "4. Positional Encoding 为什么必须要有？",
]

for q in questions_day11:
    print(q)

print("""
答案自查：
1. RNN 串行、忘词；Transformer 并行、每个词直接看到所有词
2. 每个词看其他所有词，决定「谁对我最重要」
3. 生成任务只能根据上文预测下一个词，不能偷看后面
4. 没有位置信息，「我爱你」和「你爱我」对模型完全一样
""")


# ============================================================
# Day 12 自检：Prompt Engineering
# ============================================================

print("\n" + "=" * 60)
print("Day 12 自检：Prompt Engineering")
print("=" * 60)
print()

questions_day12 = [
    "1. 四大 Prompt 技巧分别是什么？各举一个场景。",
    "2. Few-shot 为什么有效？",
    "3. 什么是思维链（Chain of Thought）？什么时候用它？",
    "4. 为什么要指定 JSON 格式输出？不用会怎样？",
]

for q in questions_day12:
    print(q)

print("""
答案自查：
1. 角色设定（设定身份）、Few-shot（给例子）、思维链（逐步推理）、JSON输出（结构化）
2. 模型见到例子后理解「我要什么样的输出格式和风格」
3. 要求模型一步步推导再给结论；复杂推理题必用，能大幅降低错误率
4. 自由格式解析不了；JSON 可以直接 json.loads() 进入程序逻辑
""")


# ============================================================
# Day 13 自检：Function Calling
# ============================================================

print("\n" + "=" * 60)
print("Day 13 自检：Function Calling")
print("=" * 60)
print()

questions_day13 = [
    "1. Function Calling 的完整循环分几步？",
    "2. Tool Schema 里最重要的是哪个字段？为什么？",
    "3. 多个工具时 LLM 怎么选？",
    "4. Function Calling 和普通 API 调用的本质区别是什么？",
]

for q in questions_day13:
    print(q)

print("""
答案自查：
1. 用户提问→LLM返回tool_calls→你执行函数→结果喂回→LLM生成回复
2. description；LLM 不看你的函数代码，只看描述判断「该不该调」
3. LLM 根据用户意图自动匹配最合适的工具
4. 普通API：返回文字；Function Calling：返回「我要调这个函数」的结构化指令
""")


# ============================================================
# 连线题：概念 → 在你的 RAG 项目中怎么用
# ============================================================

print("\n" + "=" * 60)
print("连线：本周概念 → RAG 项目对应")
print("=" * 60)
print()

print("""
  Token / 计费      →  设计 Prompt 要精打细算，不塞无关内容
  Embedding         →  RAG 检索的核心：query向量 vs 文档向量 → 取最像的
  Transformer       →  理解 LLM 为什么能「理解」语义，不是关键字匹配
  System Prompt     →  设定知识库助手的角色和行为边界
  Few-shot          →  告诉模型你要的答案格式和风格
  Chain of Thought  →  复杂问题让 Agent 多步推理
  JSON 输出         →  检索结果、提取的信息结构化返回
  Function Calling  →  Agent 调搜索引擎/数据库/计算器
""")

# ============================================================
# 动手任务
# ============================================================

print("\n" + "=" * 60)
print("今天要做的两件事")
print("=" * 60)
print()

print("""
1. 把 24 个问题过一遍，答不上的回去翻当天代码。

2. 提交 Git：
   cd E:\\learn
   git add day08 day09 day10 day11 day12 day13 day14
   git commit -m "Week 2: Token-Embedding-Transformer-Prompt-FunctionCalling"
   git push

本周是理论最密集的一周。下周开始用这些知识搭第一个 RAG 项目。
""")
