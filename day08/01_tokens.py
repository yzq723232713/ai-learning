"""
Day 8：LLM 是什么 + Token 概念

今天的内容偏理解，不是写代码。
先跑这个脚本直观感受 Token，然后去看吴恩达课程。
"""

import tiktoken

# ========================================
# Part 1: LLM 到底在干什么
# ========================================

print("=== Part 1: LLM 的本质 ===\n")

# 语言模型的本质就一句话：
# "给定前面所有的词，预测下一个词最可能是什么"

# 比如你输入 "中国的首都是"
# 模型内部计算出每个可能的下一个词的概率：
# 北京: 92%
# 上海: 3%
# 广州: 1%
# ...其他: 4%
# → 输出 "北京"

# 然后把这个"北京"追加到输入里，继续预测再下一个：
# "中国的首都是北京" → 下一个词？ → "。"
# "中国的首都是北京。" → 下一个词？ → 结束

# 这就是"自回归生成"：吃掉自己的输出，一直往下续写

print("LLM 的本质：给前面所有词 → 猜下一个词 → 把猜出来的词喂回去 → 再猜下一个")

# 这也是为什么 LLM 本质上是"概率模型"，不是"知识库"
# 它说的每一句话都是"统计上最合理的下一个词串"，不是"从数据库查出来的事实"


# ========================================
# Part 2: 什么是 Token
# ========================================

print("\n=== Part 2: 什么是 Token ===\n")

# 模型不认识文字，只认识数字。
# Token = 文本被切分后的最小单位
# Tokenizer = 把文本切成 Token 并映射为数字的工具

# 用 GPT 的 tiktoken 来直观感受
enc = tiktoken.get_encoding("cl100k_base")  # GPT-4 / GPT-3.5 用的编码

texts = [
    "hello world",
    "你好世界",
    "Hello, how are you?",
    "Python is a programming language.",
    "我今天学习了LLM的基础概念。",
    "Transformer",
    "ChatGPT",
]

print(f"{'文本':<40s} | {'Token数':<8s} | Token IDs")
print("-" * 80)
for text in texts:
    tokens = enc.encode(text)
    token_str = str(tokens[:10])  # 只显示前10个
    if len(tokens) > 10:
        token_str += "..."
    print(f"{text:<40s} | {len(tokens):<8d} | {token_str}")


# ========================================
# Part 3: 不同语言，token 效率不同
# ========================================

print("\n=== Part 3: 中英文 Token 效率 ===\n")

# 同一个意思，中英文 token 数量不同
pairs = [
    ("我喜欢学习", "I like learning"),
    ("人工智能正在改变世界", "Artificial intelligence is changing the world"),
    ("你好", "Hello"),
    ("机器学习", "Machine learning"),
]

print(f"{'中文':<30s} | {'Token':<6s} | {'英文':<30s} | Token")
print("-" * 80)
for cn, en in pairs:
    cn_tokens = len(enc.encode(cn))
    en_tokens = len(enc.encode(en))
    print(f"{cn:<30s} | {cn_tokens:<6d} | {en:<30s} | {en_tokens}")


# ========================================
# Part 4: 一个中文汉字 ≈ 几个 token？
# ========================================

print("\n=== Part 4: 中文的 token 规律 ===\n")

# GPT 的 tokenizer 对中文不太友好：
# - 一个英文字母 ≈ 0.3 个 token（3个字母 = 1 token）
# - 一个常见英文单词 ≈ 1 个 token
# - 一个中文字符 ≈ 1.5-2 个 token（个别常用字可能 1 token）

test_chars = "你好世界我是中国人人工智能"
tokens = enc.encode(test_chars)
print(f"文本: {test_chars}")
print(f"字符数: {len(test_chars)}")
print(f"Token数: {len(tokens)}")
print(f"平均每个汉字: {len(tokens)/len(test_chars):.1f} token")
print(f"Token IDs: {tokens}")

# 可以看到每个汉字单独一个 ID，因为 GPT 的词汇表里
# 常用中文字符是单独编码的，但不像英文单词那样能整词编码


# ========================================
# Part 5: 不同模型，tokenizer 不同
# ========================================

print("\n=== Part 5: 不同模型的 tokenizer ===\n")

# GPT 系列用 cl100k_base（上面用的就是这个）
# 通义千问用自己的 tokenizer，中文更友好
# DeepSeek 也用自己的 tokenizer

# 同一个文本在不同 tokenizer 下的 token 数可能差很多
# 这就直接影响了：
#   1. API 费用（按 token 计费）
#   2. 上下文长度（模型最大 token 数固定，token 越少能塞的越多）

sample = "你好世界，这是一段测试文本，用来对比不同tokenizer的效果。"

gpt_tokens = len(enc.encode(sample))
print(f"文本: {sample}")
print(f"GPT-4 token数: {gpt_tokens}")
print(f"通义千问 token数: 通常比 GPT 少（中文优化更好）")
print(f"DeepSeek token数: 比 GPT 少（中文优化）")


# ========================================
# Part 6: Token 的代价
# ========================================

print("\n=== Part 6: Token 计费（API调用的核心成本）===\n")

# 每次调 API 按 token 数收费：
# 输入 token（你发的 prompt） + 输出 token（模型回复）
# 不同模型价格不同

# 举个例子：问 GPT-4 一个问题
question = "请用300字介绍一下机器学习的基本概念。"
input_tokens = len(enc.encode(question))

print(f"问题: {question}")
print(f"输入 token: {input_tokens}")

# 假如模型回复了 400 token
output_tokens = 400

# GPT-4 Turbo 价格（2024年）：
# 输入: $0.01 / 1K tokens
# 输出: $0.03 / 1K tokens
# 一次提问成本 = (input * 0.01 + output * 0.03) / 1000

cost = (input_tokens * 0.01 + output_tokens * 0.03) / 1000
print(f"预估回复: {output_tokens} token")
print(f"本次提问成本: ${cost:.4f}（约 ¥{cost*7.2:.4f}）")

print(f"\n如果是通义千问（价格约为 GPT-4 的 1/10）：")
print(f"本次提问成本: 约 ¥{cost*7.2/10:.4f}")

print("\n这解释了为什么 RAG 要精心设计 Prompt：")
print("  1. 减少不必要的上下文（省 token = 省钱）")
print("  2. 只检索真正相关的文档块（不浪费输入窗口）")
print("  3. 中文模型 token 效率更高（省输入成本）")


print("\n=== Day 8 要点 ===\n")
print("1. LLM = 预测下一个 token 的概率模型")
print("2. Token = 文本被切分的最小数字单位")
print("3. 一个中文字 ≈ 1-2 token（GPT），通义/DeepSeek 更省")
print("4. API 按 token 收费，设计 Prompt 要精打细算")
print("5. 现在去看吴恩达课程前半部分：B站搜 'ChatGPT Prompt Engineering'")
