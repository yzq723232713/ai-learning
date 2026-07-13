"""
Day 22：LangChain 五⼤核心抽象

LangChain 不是魔法——就是你 Day 19 手搓的那些胶水代码的工业化封装。
今天把五个核心抽象逐个对照你的手写版本。
"""
import os
from dotenv import load_dotenv
load_dotenv("E:/learn/day09/.env")


# ============================================================
# 抽象 1：PromptTemplate — 拼字符串的模板引擎
# ============================================================

print("=== 抽象 1: PromptTemplate ===\n")

# Day 19 你手写的版本（f-string 拼凑）：
def handcraft_prompt(query, chunks):
    refs = "\n".join(f"[{i}] {c}" for i, c in enumerate(chunks, 1))
    return f"""你是知识库助手。根据参考资料回答。
参考资料：{refs}
问题：{query}"""

print("手写版: 用 f-string 把变量嵌进字符串")
print(handcraft_prompt("怎么安装？", ["步骤1: 固定", "步骤2: 连线"]))
print()

# LangChain 版本：声明变量名（用 {} 包起来），自动填充
# from langchain_core.prompts import PromptTemplate
# prompt = PromptTemplate.from_template("问题：{question}\n参考：{references}")
# prompt.format(question="怎么安装？", references="文档内容")

print("LangChain 版: 声明 {变量名}，自动填充，不用写 f-string 嵌套")
print("好处：变量多时不容易拼错，框架自动做类型校验\n")


# ============================================================
# 抽象 2：ChatModel — 统一 LLM 接口
# ============================================================

print("=== 抽象 2: ChatModel ===\n")

# Day 9 手写版（直接调 OpenAI SDK）:
from openai import OpenAI
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用一句话解释什么是大模型"}],
    temperature=0.0,
)
print(f"手写版 OpenAI SDK: {resp.choices[0].message.content[:80]}...")

# LangChain 统一封装:
# from langchain_deepseek import ChatDeepSeek
# llm = ChatDeepSeek(api_key="...", model="deepseek-chat", temperature=0.0)
# resp = llm.invoke("用一句话解释什么是大模型")  # 一行调用
# resp.content  # 拿文本

print("\nLangChain 版: llm.invoke() 一个方法调所有模型")
print("换模型只改 ChatDeepSeek → ChatOpenAI，业务代码不动\n")


# ============================================================
# 抽象 3：Document — 统一文档对象
# ============================================================

print("=== 抽象 3: Document ===\n")

# Day 15 你手写的 LoadedDocument (Pydantic):
# class LoadedDocument:
#     content: str    # 文本内容
#     source: str     # 来源文件
#     file_type: str  # 文件类型

# LangChain 内置:
# from langchain_core.documents import Document
# doc = Document(
#     page_content="智能温控器安装步骤...",
#     metadata={"source": "产品手册.pdf", "page": 3}
# )

print("你的 LoadedDocument → content, source, file_type")
print("LangChain Document  → page_content, metadata={任意键值对}")
print("metadata 是个自由字典，source/file_type/page 全塞进去\n")


# ============================================================
# 抽象 4：Retriever — 统一检索接口
# ============================================================

print("=== 抽象 4: Retriever ===\n")

# Day 19 手写版:
# results = collection.query(query_embeddings=[q_emb], n_results=5)
# 返回: (documents, metadatas, distances) 三个分开的列表

# LangChain Retriever:
# retriever.invoke("怎么安装？")
# 返回: [Document(...), Document(...), ...]
# 不管底层是 Chroma / FAISS / Elasticsearch，外面都一样

print("手写版:    collection.query() → (docs, metas, dists)")
print("Retriever: retriever.invoke() → List[Document]")
print("换向量数据库时只改 retriever 构造，invoke 调用不变\n")


# ============================================================
# 抽象 5：LCEL — | 管道符串流水线
# ============================================================

print("=== 抽象 5: LCEL（管道符）===\n")

# Day 19 手写版（8步函数调用）:
#   chunks = load_and_chunk(folder)
#   store_chunks(chunks)
#   docs = search(query)
#   prompt = build_prompt(query, docs)
#   answer = generate_answer(prompt)
# → 所有步骤我自己的函数，我也自己调度

# LangChain LCEL 用 | 管道符串:
# chain = prompt | llm
# chain.invoke({"question": "怎么安装？"})
# 等价于: llm.invoke(prompt.format({"question": "怎么安装？"}))

# 多步链:
# chain = retriever | prompt | llm | StrOutputParser()
# 数据从左流到右:
#   "查询" → retriever → [Document...] → prompt → "拼好的字符串" → llm → AI消息 → StrOutputParser → "纯文本"

# 测试：prompt + llm 管道（你用 OpenAI SDK 跑，不依赖 LangChain 安装）
prompt_text = "给一个{age}岁{job}推荐3本必读书。只输出书名。"
# prompt | llm 本质上就是:
formatted = prompt_text.format(age="28", job="程序员")
print(f"管道符模拟: prompt | llm")
print(f"  Step1 prompt.format() → '{formatted}'")
print(f"  Step2 llm.invoke('{formatted}') → 调 DeepSeek")

resp2 = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": formatted}],
    temperature=0.0,
)
print(f"  结果: {resp2.choices[0].message.content}")


# ============================================================
# 总结：250 行手写 vs 15 行 LCEL
# ============================================================

print("\n\n=== Day 19 手写 vs LangChain LCEL ===\n")

print("""
Day 19 手写版（8 个函数，~250 行）:
  load_document → chunk_text → embed_chunks → store_chunks
  → search → build_prompt → generate_answer → rag_pipeline

LangChain 等价写法:
  chain = retriever | prompt | llm | StrOutputParser()
  chain.invoke({"question": "怎么安装?"})

LangChain 没发明新东西——就是把你的 8 个步骤标准化了:
  每个组件都有 invoke() 方法 → 用 | 串成流水线
  换底层实现不改业务代码 → 所有东西都叫 Document
""")


print("*** Day 22 基础练习全部完成! ***")
print("\n五个核心抽象总结：")
print("  1. PromptTemplate  — 声明式 {变量} 模板，替代 f-string")
print("  2. ChatModel       — 统一 invoke()，换模型只改一行")
print("  3. Document        — page_content + metadata，就是你的 LoadedDocument")
print("  4. Retriever       — invoke(query) → List[Document]，屏蔽底层")
print("  5. LCEL (|)        — 管道符串流水线，retriever | prompt | llm")
