"""
Day 25：三种高级 RAG 检索技术

  1. Self-querying  — 模型自动拆查询 = 语义 + 元数据过滤
  2. Multi-query    — 把一个问题改写成多个角度，分别检索，合并
  3. Parent Doc     — 检索小块，返回大块（精度+上下文两不误）

每种技术都用一个完整可运行的 demo 展示。
"""
import os, logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("llama_index").setLevel(logging.WARNING)

from dotenv import load_dotenv
load_dotenv("E:/learn/day09/.env")

from openai import OpenAI
llm_client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


# ============================================================
# Part 1: Self-querying — 语义 + 元数据过滤
# ============================================================

print("=== Part 1: Self-querying（自查询）===\n")

print("""
场景：用户问 "2024年关于薪资的规章制度"

传统做法：向量检索 "2024年关于薪资的规章制度" → 全库盲搜
Self-querying：LLM 先分析问题 →
  - 语义查询: "薪资"（Embedding 向量检索）
  - 元数据过滤: year=2024, category="规章制度"（缩小范围）
→ 先在 filtered set 里做向量检索 → 精准命中
""")

# 模拟：用 LLM 拆查询
query = "2024年关于薪资的规章制度"

resp = llm_client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "system", "content": """你是一个查询解析器。分析用户问题，拆分为语义查询和元数据过滤条件。
严格按照JSON格式输出，不要输出其他内容。

元数据字段: source（文档来源）, year（年份）, category（分类）
如果用户没指定某个字段，值为 null。

示例:
用户: "产品手册里关于安装的内容"
输出: {"semantic_query": "安装", "filter": {"source": "产品手册.pdf", "year": null, "category": null}}

用户: "2023年的财务报告"
输出: {"semantic_query": "财务报告", "filter": {"source": null, "year": 2023, "category": "财务"}}"""},
    {"role": "user", "content": query}],
    temperature=0.0,
)

print(f"用户问题: 「{query}」")
print(f"LLM 解析结果: {resp.choices[0].message.content}")
print()

# 第二个例子
query2 = "产品手册里2024年关于安装的内容"
resp2 = llm_client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "system", "content": "同上"}, {"role": "user", "content": query2}],
    temperature=0.0,
)
print(f"用户问题: 「{query2}」")
print(f"LLM 解析结果: {resp2.choices[0].message.content}")

print("\n价值：检索前先用元数据过滤缩小范围，召回更精准。")
print("你的 ODS 经验在这里 = 给文档打高质量元数据标签。\n")


# ============================================================
# Part 2: Multi-query — 一个查询变多个，分别检索
# ============================================================

print("=== Part 2: Multi-query（多查询改写）===\n")

print("""
场景：用户问 "这个设备怎么用？"

原始查询可能跟文档里的表述不完全匹配 →
LLM 把问题改写成多个版本：
  1. "智能温控器使用方法"
  2. "设备操作步骤"
  3. "X-100产品使用说明"

三个角度分别检索 → 合并去重 → 给 LLM
一个版本漏掉的，另一个版本可能捞回来。
""")

original = "这个设备怎么用？"

resp = llm_client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "system", "content": """你是查询改写助手。把用户问题改写为 3 个不同角度的检索查询。
每个查询应该从不同角度描述同一需求，帮助提高检索召回率。
只输出查询列表，每行一个，以 - 开头。

示例:
用户: "怎么提高代码质量"
输出:
- 代码审查最佳实践
- 单元测试编写技巧
- 减少代码坏味道的方法"""},
    {"role": "user", "content": original}],
    temperature=0.3,  # 稍有创造性
)

print(f"原始查询: 「{original}」")
print(f"改写为:\n{resp.choices[0].message.content}\n")

# 演示合并逻辑（伪代码，不实际检索）
print("""合并逻辑（RRF，Day 20 你写过的）:
  for each query_variant:
      results = search(query_variant, top_k=10)
      for rank, doc in enumerate(results):
          rrf_score[doc] += 1/(60 + rank)

  最终按 rrf_score 排序取 Top-K
  同一个文档被多个查询版本命中 → 得分累加 → 排名更高
""")


# ============================================================
# Part 3: Parent Document Retriever
# ============================================================

print("=== Part 3: Parent Document Retriever ===\n")

print("""
检索的经典矛盾:
  切太碎(50字一块) → 检索精度高，但缺少上下文，LLM 看不懂
  切太大(500字一块) → 上下文完整，但检索精度低，噪声多

Parent Document Retriever 的解法:
  离线: 文档切成二级结构
    - Parent Chunk (大块, 500字): 存完整上下文 → 不给检索用
    - Child Chunk (小块, 100字): 存向量库 → 专用于检索

  在线:
    检索用 child → 找到最相关的 child → 返回它所属的 parent
    → 检索精度 = 小块，返回内容 = 大块
""")

# 示例: 模拟大文档的二级切分
document = """
第一章 产品概述
智能温控器 X-100 是一款面向家庭和办公场景的智能温度控制设备。
该产品支持 Wi-Fi 连接，可通过手机 APP 远程控制室内温度。
产品采用高精度温度传感器，精度可达 ±0.5°C。

第二章 安装指南
在安装设备之前，请确保墙面平整干燥。需要准备的工具有十字螺丝刀、
电钻、水平尺。安装步骤：固定背板、连接电源线、下载 APP 配网。

第三章 故障排除
E01 错误代码表示温度传感器故障，解决方案是断电重启设备。
E02 错误代码表示 Wi-Fi 模块异常，解决方案是检查路由器距离。
如果问题依然存在，请联系售后服务：400-888-XXXX。
"""

# 二级切分
import re
parent_chunks = document.split("\n\n")  # 按段落切，作为 parent
child_chunks = []
parent_map = {}  # child_id → parent_id

for p_idx, parent in enumerate(parent_chunks):
    if not parent.strip():
        continue
    # 每个 parent 切成更小的 child（按句子）
    sentences = re.split(r'[。！]', parent)
    sentences = [s.strip() for s in sentences if s.strip()]
    for s in sentences:
        if len(s) > 10:  # 过滤太短的
            child_id = len(child_chunks)
            child_chunks.append(s)
            parent_map[child_id] = p_idx

print(f"Parent Chunk: {len(parent_chunks)} 个段落")
print(f"Child Chunk:  {len(child_chunks)} 个句子")

# 模拟检索
query = "传感器故障怎么办？"
print(f"\n查询: 「{query}」")
print(f"  1. Embed query → 在 child_chunks 中检索 → 命中最相关的 child")
print(f"     child[?]: E01 错误代码表示温度传感器故障")
print(f"  2. 查 parent_map → 这个 child 属于 parent[{parent_map[4]}]")
print(f"  3. 返回完整的 parent 章节:")
print(f"     {parent_chunks[parent_map[4]].strip()[:80]}...")

print("\n结果: LLM 看到的是一整段故障排除章节（有上下文）,")
print("       但检索用的是精确的 child 小块（无噪声）")


# ============================================================
# 总结对比
# ============================================================

print("\n\n=== 三种技术对比 ===\n")

print("""
┌──────────────────┬─────────────────────┬──────────────────────┐
│      技术         │      解决什么问题     │       核心思路          │
├──────────────────┼─────────────────────┼──────────────────────┤
│ Self-querying    │ 检索范围太大          │ LLM 拆查询 = 语义+过滤 │
│ Multi-query      │ 单一表述可能漏召回     │ 一个查询改写为多个角度   │
│ Parent Doc       │ 小块没上下文，大块不精准│ 小块检索，大块返回       │
└──────────────────┴─────────────────────┴──────────────────────┘

你的 RAG 项目（Day 29）默认用纯向量检索。
面试时如果被问 "怎么优化检索精度" —
  答其中一项：Multi-query 最通用，Parent Doc 最工程化。
""")


print("*** Day 25 基础练习全部完成! ***")
