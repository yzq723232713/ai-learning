"""
Day 13：Function Calling — 让模型调用你写的函数

核心流水线（5步循环）：
  用户提问 → LLM 判断"需要调工具" → 返回函数名+参数
  → 你执行函数拿结果 → 喂回 LLM → LLM 生成最终回复
"""
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("E:/learn/day09/.env")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# ========================================
# Part 1: 定义工具（Tool Schema）
# ========================================

print("=== Part 1: 定义工具 ===\n")

# 工具 = 函数名 + 描述 + 参数 JSON Schema
# LLM 不看你的函数代码，只看这段描述来决定调不调、怎么调

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气。需要提供城市名称。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如'北京'、'上海'",
                    }
                },
                "required": ["city"],
            },
        },
    },
]

print("定义了一个工具: get_weather(city)")
print(f"LLM 看到的描述:\n{json.dumps(tools, indent=2, ensure_ascii=False)}")


# ========================================
# Part 2: 第一次调用 — LLM 决定要不要调工具
# ========================================

print("\n=== Part 2: LLM 判断需要调工具 ===\n")

messages = [
    {"role": "system", "content": "你是AI助手。当用户问天气时，调用 get_weather 工具获取数据。"},
    {"role": "user", "content": "北京今天天气怎么样？"},
]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
    temperature=0.0,
)

msg = response.choices[0].message
print(f"LLM 返回的类型: finish_reason={response.choices[0].finish_reason}")

# 关键判断：有 tool_calls 说明模型想调函数
if msg.tool_calls:
    print("\nLLM 想要调用工具！")
    tool_call = msg.tool_calls[0]
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)
    print(f"  函数名: {func_name}")
    print(f"  参数: {func_args}")
else:
    print("LLM 直接回答了，不需要调工具")
    print(msg.content)


# ========================================
# Part 3: 完整循环 — 调工具 + 喂回结果
# ========================================

print("\n=== Part 3: 完整调用循环 ===\n")

def execute_get_weather(city: str) -> dict:
    """模拟天气查询（实际项目里调真实API）"""
    # 假数据
    weather_db = {
        "北京": {"温度": "25°C", "天气": "晴", "湿度": "45%"},
        "上海": {"温度": "28°C", "天气": "多云", "湿度": "65%"},
        "深圳": {"温度": "30°C", "天气": "阵雨", "湿度": "80%"},
    }
    return weather_db.get(city, {"温度": "未知", "天气": "未知", "湿度": "未知"})


def run_agent(user_question: str):
    """完整的 Function Calling 流程"""
    messages = [
        {"role": "system", "content": "你是AI助手。当用户问天气时，必须调用 get_weather 获取实时数据，不要编造。"},
        {"role": "user", "content": user_question},
    ]

    # 第1步：发给 LLM，让它决定要不要调工具
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        temperature=0.0,
    )

    msg = resp.choices[0].message

    # 第2步：如果 LLM 想调工具，执行并喂回
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)

        print(f"  [调用工具] {func_name}({func_args})")

        # 执行函数
        result = execute_get_weather(**func_args)  # ** 展开字典为关键字参数
        print(f"  [工具返回] {result}")

        # 把工具调用和结果追加到消息历史
        messages.append(msg)  # LLM 的工具调用请求
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False),
        })

        # 第3步：再次调 LLM，让它基于工具结果生成最终回复
        resp2 = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.0,
        )

        return resp2.choices[0].message.content

    # 不需要调工具，直接返回
    return msg.content


# 测试
print("提问: 北京今天天气怎么样？")
print(f"回答: {run_agent('北京今天天气怎么样？')}\n")

print("提问: 上海呢？")
print(f"回答: {run_agent('上海呢？')}\n")

print("提问: Python是什么？")
print(f"回答: {run_agent('Python是什么？')}")


# ========================================
# Part 4: 多个工具 — LLM 自动选择
# ========================================

print("\n\n=== Part 4: 多个工具 — LLM 自动选 ===\n")

multi_tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算。支持加减乘除和括号。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如'(15+3)*2'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                },
                "required": ["city"],
            },
        },
    },
]

from datetime import datetime

def execute_tool(name, args):
    """统一工具执行器"""
    if name == "calculator":
        return {"result": eval(args["expression"])}  # eval 教学用，生产环境用安全方法
    elif name == "get_current_time":
        return {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    elif name == "get_weather":
        return execute_get_weather(args["city"])


def run_multi_tool_agent(question: str):
    """支持多个工具的 Agent"""
    messages = [
        {"role": "system", "content": "你是AI助手。可以调用calculator、get_current_time、get_weather三个工具。"},
        {"role": "user", "content": question},
    ]

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=multi_tools,
        temperature=0.0,
    )
    msg = resp.choices[0].message

    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        print(f"  [调用] {name}({args})")
        result = execute_tool(name, args)
        print(f"  [返回] {result}")

        messages.append(msg)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False),
        })

        resp2 = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.0,
        )
        return resp2.choices[0].message.content

    return msg.content


# 测试 — 同一个 Agent 自动选不同工具
print("提问: 帮我算一下 (15+3)*2")
print(f"回答: {run_multi_tool_agent('帮我算一下 (15+3)*2')}\n")

print("提问: 现在几点了？")
print(f"回答: {run_multi_tool_agent('现在几点了？')}\n")

print("提问: 深圳天气怎么样？")
print(f"回答: {run_multi_tool_agent('深圳天气怎么样？')}")


print("\n\n*** Day 13 基础练习全部完成! ***")
print("\n关键结论:")
print("  1. Function Calling = LLM 返回'我想调这个函数'而不是返回文字")
print("  2. 你执行函数，把结果喂回去，LLM 基于结果生成最终回答")
print("  3. 多个工具时 LLM 自动选最合适的那个")
print("  4. 这就是 AI Agent 的核心机制（Day 44-47 展开）")
print("\n下一步检验：实现 calculator 工具，问 (15+3)*2（Part 4 已经演示了）")
