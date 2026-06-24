"""
Day 12 检验：设计一个 Prompt，把杂乱的产品描述整理成结构化 JSON

你的任务：
  写一个 system_prompt 和 user_prompt，
  让模型把下面的杂乱描述提取为指定的 JSON 结构。
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("E:/learn/day09/.env")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 一段杂乱的"产品描述"（模拟从网页抓下来的原始文本）
raw_text = """
【爆款推荐】Apple iPhone 15 Pro Max 256GB 原色钛金属！！
价格只要9999元！比官网便宜！！支持5G全网通，A17 Pro芯片性能炸裂，
拍照方面有4800万像素主摄，还有钛金属边框手感超好。
就是有点重，而且价格偏贵。适合追求极致体验的数码发烧友和摄影爱好者。
哦对了电池续航比上一代强了不少，一天一充就够了哈。
"""

# ========================================
# TODO: 设计你的 Prompt
# ========================================

# 你要提取的目标 JSON 结构：
# {
#     "product_name": "iPhone 15 Pro Max",
#     "brand": "Apple",
#     "specs": {
#         "storage": "256GB",
#         "color": "原色钛金属"
#     },
#     "price": 9999,
#     "pros": ["A17 Pro芯片", "4800万像素主摄", "钛金属边框", "续航好"],
#     "cons": ["有点重", "价格偏贵"],
#     "target_users": ["数码发烧友", "摄影爱好者"]
# }

system_prompt = "你是一个资深的数据分析师，擅长从杂乱文本中提取结构化信息。"

user_prompt = """从以下产品描述中提取信息，格式为JSON,
参考示例：
输出JSON格式：
{
     "product_name": "",
     "brand": "",
     "specs": {
         "storage": "",
         "color": ""
     },
     "price": ,
     "pros": [],
     "cons": [],
     "target_users": []
 },
现在处理以下文本，一步步提取:
1. 先找出产品名和品牌
2. 找出价格
3. 区分优点和缺点
4. 确定适用人群
5. 汇总为JSON

文本: """ + raw_text

# ========================================
# 调用 API
# ========================================
if __name__ == "__main__":
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )
    print("模型输出:")
    print(resp.choices[0].message.content)
