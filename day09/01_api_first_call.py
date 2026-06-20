"""
Day 9：API 上手 — 用 DeepSeek 跑第一个 LLM 调用
DeepSeek API 兼容 OpenAI SDK，把 base_url 改成 DeepSeek 就行
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("E:/learn/day09/.env")

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# ========================================
# Part 1: 第一个 API 调用
# ========================================

print("=== Part 1: 第一个 API 调用 ===\n")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个乐于助人的AI助手。"},
        {"role": "user", "content": "用一句话介绍什么是RAG。"},
    ],
)

print("回复:", response.choices[0].message.content)
print(f"\n本次消耗 token: {response.usage.total_tokens}")
print(f"  输入: {response.usage.prompt_tokens}")
print(f"  输出: {response.usage.completion_tokens}")


# ========================================
# Part 2: 核心参数实验 — Temperature
# ========================================

print("\n\n=== Part 2: Temperature 参数 ===\n")

question = "用一句话描述春天"

for temp in [0.0, 0.5, 1.0, 1.5]:
    print(f"--- Temperature = {temp} ---")
    for i in range(3):
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": question}],
            temperature=temp,
            max_tokens=50,
        )
        print(f"  第{i+1}次: {resp.choices[0].message.content}")
    print()

print("观察结论：")
print("  temp=0: 每次几乎一样（确定性最高）")
print("  temp=1.0: 每次明显不同（创造性）")
print("  temp=1.5: 可能跑偏（>1 不推荐生产用）")


# ========================================
# Part 3: top_p（核采样）
# ========================================

print("=== Part 3: top_p 参数 ===\n")

# top_p = 从概率最高的词开始累加，直到累积概率 >= p，只从这些词里选
# p=1.0 等价于从所有词里选；p=0.1 等价于只从最可能的10%词里选

print("问题: 写一个四个字的标题，描述夏天的感觉\n")

for p in [0.1, 0.5, 1.0]:
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "写一个四个字的标题，描述夏天的感觉"}],
        top_p=p,
        temperature=1.0,
        max_tokens=20,
    )
    print(f"top_p={p}: {resp.choices[0].message.content}")

print("\n通常 temperature 和 top_p 只调一个，推荐先调 temperature。")


# ========================================
# Part 4: System Prompt vs User Prompt
# ========================================

print("\n=== Part 4: System Prompt vs User Prompt ===\n")

# System Prompt = 设定角色和行为（发一次，放在最前面）
# User Prompt = 具体的问题

question = "写一段关于编程的文字，50字以内"

# 版本A：只有 User Prompt
print("--- 版本A：只有 User Prompt ---")
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": question}],
    max_tokens=100,
)
print(f"回复: {resp.choices[0].message.content}\n")

# 版本B：System Prompt 设定角色
print("--- 版本B：System Prompt 设定为小学老师 ---")
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个小学计算机老师，用简单易懂的语言解释概念，多打比方。"},
        {"role": "user", "content": question},
    ],
    max_tokens=100,
)
print(f"回复: {resp.choices[0].message.content}\n")

# 版本C：System Prompt 设定为技术专家
print("--- 版本C：System Prompt 设定为技术专家 ---")
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个资深软件架构师，回答技术、专业、精确。"},
        {"role": "user", "content": question},
    ],
    max_tokens=100,
)
print(f"回复: {resp.choices[0].message.content}\n")

print("同一个问题，System Prompt 不同，回答风格天差地别。")


# ========================================
# Part 5: 流式输出（SSE）
# ========================================

print("=== Part 5: 流式输出（逐字显示）===\n")

print("提问: 用三句话介绍深度学习")
print("回答: ", end="", flush=True)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用三句话介绍深度学习"}],
    stream=True,        # ← 开启流式
    max_tokens=200,
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print("\n")

# stream=True 时，response 返回的是迭代器
# 每收到一小段就 yield 出来，不用等完整回复


# ========================================
# Part 6: max_tokens 限制长度
# ========================================

print("=== Part 6: max_tokens 限制输出长度 ===\n")

for limit in [10, 30, 100]:
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "介绍一下Python的特点"}],
        max_tokens=limit,
    )
    print(f"max_tokens={limit:3d}: {resp.choices[0].message.content}")


print("\n\n*** Day 9 基础练习全部完成! ***")
print("\n下一步检验：用不同 temperature 对同一个问题各调3次，观察输出差异（已经在上面的 Part 2 里跑过了）")
