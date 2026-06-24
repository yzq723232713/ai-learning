"""
Day 12：Prompt Engineering 基础技巧

四大核心技巧：
  1. 角色设定     — System Prompt 设定身份
  2. 少样本学习   — 给 2-3 个例子让模型照做
  3. 思维链       — "让我们一步步思考"
  4. 结构化输出   — 指定 JSON / 表格格式

直接用 DeepSeek API 跑，每个技巧对比有效 vs 无效的写法。
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("E:/learn/day09/.env")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def ask(system_prompt, user_prompt, temperature=0.0):
    """封装一个简单的调用函数"""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=300,
    )
    return resp.choices[0].message.content


# ========================================
# 技巧1: 角色设定 — System Prompt 的力量
# ========================================

print("=== 技巧1: 角色设定 ===\n")

question = "Python中的装饰器是什么？"

# ❌ 没有角色设定
print("--- 没有角色设定 ---")
print(ask("你是一个AI助手。", question))
print()

# ✅ 设定为 Python 专家
print("--- 设定为 Python 专家 ---")
print(ask(
    "你是一个资深Python工程师，有10年经验。用简洁专业的语言回答，必要时给出代码示例。",
    question
))
print()

# ✅ 设定为面向初学者的老师
print("--- 设定为面向初学者的老师 ---")
print(ask(
    "你是一个面向编程初学者的老师。用生活化的比喻解释概念，避免专业术语。",
    question
))


# ========================================
# 技巧2: 少样本学习（Few-shot）
# ========================================

print("\n\n=== 技巧2: Few-shot（给例子）===\n")

# 任务：把口语化的文本转为正式书面语

# ❌ 不给例子
print("--- 不给例子 ---")
print(ask(
    "你是文本改写助手。把用户输入改写为正式书面语。",
    "这玩意挺好用的，推荐给大家。"
))
print()

# ✅ 给 3 个例子
print("--- 给 3 个例子 ---")
print(ask(
    "你是文本改写助手。把口语化文本改写为正式书面语。参考以下例子：",
    """例子1: "这东西不错" → "该产品质量优良"
例子2: "赶紧的别磨叽" → "请尽快处理，避免延误"
例子3: "很多人用了都说好" → "该产品获得了用户的广泛好评"

现在改写: "这玩意挺好用的，推荐给大家。"
"""
))


# ========================================
# 技巧3: 思维链（Chain of Thought）
# ========================================

print("\n\n=== 技巧3: 思维链（让我们一步步思考）===\n")

# 一个需要推理的问题
question_cot = "一个房间里有3个人：张三、李四、王五。张三比李四高，李四比王五高。谁是最矮的？"

# ❌ 直接要答案
print("--- 直接要答案 ---")
print(ask("回答问题。", question_cot))
print()

# ✅ 要求逐步推理
print("--- 要求逐步推理 ---")
print(ask(
    "你是一个逻辑推理助手。",
    f"{question_cot}\n\n请一步步推导，然后给出最终答案。"
))


# ========================================
# 技巧4: 结构化输出（JSON）
# ========================================

print("\n\n=== 技巧4: 结构化输出 ===\n")

review = "华为Mate60 Pro手机，黑色，价格6999元，拍照效果出色，但电池续航一般。适合商务人士使用。"

# ❌ 自由格式
print("--- 自由格式 ---")
print(ask("提取这段话中的产品信息。", review))
print()

# ✅ 指定 JSON 格式
print("--- 指定 JSON 格式 ---")
print(ask(
    "你是产品信息提取助手。从文本中提取信息，严格按以下JSON格式输出：",
    f"""文本: "{review}"

请输出JSON（不要输出其他内容）:
{{
    "product_name": "",
    "brand": "",
    "color": "",
    "price": 0,
    "pros": [],
    "cons": [],
    "target_users": []
}}
"""
))


# ========================================
# 技巧5: 组合使用 — 全部技巧叠加
# ========================================

print("\n\n=== 技巧5: 组合使用 ===\n")

print(ask(
    "你是一个资深的数据分析师，擅长从杂乱文本中提取结构化信息。",
    """从以下产品描述中提取信息，格式为JSON。

参考示例:
文本: "苹果AirPods Pro，白色，1999元，降噪好但续航短。学生和上班族爱用。"
输出: {"name":"AirPods Pro","brand":"苹果","price":1999,"pros":["降噪好"],"cons":["续航短"],"target":["学生","上班族"]}

现在处理以下文本，一步步提取:
1. 先找出产品名和品牌
2. 找出价格
3. 区分优点和缺点
4. 确定适用人群
5. 汇总为JSON

文本: "小米13 Ultra手机，徕卡光学镜头，5999元，拍照天花板级别，手感略重。摄影爱好者的首选。"
"""
))


print("\n\n*** Day 12 基础练习全部完成! ***")
print("\n下一步检验：自己设计一个 Prompt，把一段杂乱产品描述整理成结构化JSON")
print("检验文件: 02_structured_extraction.py")
