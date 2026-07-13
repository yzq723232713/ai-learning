"""
Day 23：LangChain RAG 深入 — 切分器 + 检索链 + 多轮对话

对比你手写的实现，看 LangChain 怎么用三行代码替代三十行。
"""
import os
from dotenv import load_dotenv
load_dotenv("E:/learn/day09/.env")


# ============================================================
# Part 1: RecursiveCharacterTextSplitter — 你 Day 16 手写的工业版
# ============================================================

print("=== Part 1: RecursiveCharacterTextSplitter ===\n")

from langchain_text_splitters import RecursiveCharacterTextSplitter

text = """智能温控器 X-100 产品手册\n\n第一章 产品概述\n\n智能温控器是一款智能设备。
支持Wi-Fi连接，可通过手机APP远程控制。\n\n第二章 安装指南\n\n第一步，固定设备。
第二步，连接电源。第三步，下载APP配对。\n\n第三章 故障排除\n\nE01错误代码
表示传感器故障。解决方案：断电重启。"""

# LangChain 一行
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,        # 每块最多 100 字
    chunk_overlap=20,      # 相邻块重叠 20 字
    separators=["\n\n", "\n", "。", "，", " ", ""],  # 递归降级顺序
)
lc_chunks = splitter.split_text(text)

print(f"LangChain 切出 {len(lc_chunks)} 块（chunk_size=100, overlap=20）")
for i, c in enumerate(lc_chunks):
    print(f"  块{i}: {len(c)}字 \"{c[:50]}...\"")
print()

# 你 Day 16 手写的等价代码（chunk_recursive_simple）逻辑一模一样：
#   separators = ["\n\n", "\n", "。", " "]
#   逐级降级切分 → 超长硬切
print("对比：你 Day 16 手写的 chunk_recursive_simple() 和这个逻辑完全一致。")
print("区别：你写了 ~40 行，LangChain 已封装好，传参就行。\n")


# ============================================================
# Part 2: 用 LangChain 建向量库 + Retriever
# ============================================================

print("=== Part 2: 向量库 + Retriever ===\n")

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 加载 Embedding（用你的 bge-small，已缓存）
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={"device": "cpu"},
)

# 模拟文档
docs = [
    Document(page_content="智能温控器安装步骤：固定、连线、APP配对", metadata={"source": "手册.pdf"}),
    Document(page_content="E01错误代码表示传感器故障，解决方案：断电重启", metadata={"source": "手册.pdf"}),
    Document(page_content="产品支持Wi-Fi和蓝牙连接", metadata={"source": "手册.pdf"}),
    Document(page_content="保修期2年，非人为损坏免费维修", metadata={"source": "保修卡.pdf"}),
]

# 建 Chroma 向量库（跟 Day 18 一样，但 LangChain 帮你封装了）
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="rag_demo_day23",
)

print(f"向量库中 {vectorstore._collection.count()} 条数据")

# 创建 Retriever — 统一的检索接口
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 检索
results = retriever.invoke("安装步骤是什么？")
print("\n检索: 「安装步骤是什么?」")
for i, doc in enumerate(results, 1):
    print(f"  {i}. [{doc.metadata['source']}] {doc.page_content[:60]}...")
print()

# 你 Day 18 手写的等价代码：
#   collection.query(query_embeddings=[...], n_results=3)
#   → 手动拼 Document 对象
print("区别：手写时 collection.query() 返回 (docs, metas, dists) 三个列表")
print("      Retriever 一行 invoke()，返回 List[Document]，无脑遍历\n")


# ============================================================
# Part 3: LCEL 链条 — retriever | prompt | llm
# ============================================================

print("=== Part 3: LCEL RAG 链条 ===\n")

from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

llm = ChatDeepSeek(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-chat",
    temperature=0.0,
)

# Prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是知识库助手。根据以下参考资料回答。如果不知道就说不知道。"),
    ("user", "参考资料：\n{context}\n\n问题：{question}"),
])

# 辅助函数：把检索到的 Document 列表拼成字符串
def format_docs(docs):
    return "\n\n".join(f"[{i}] {d.page_content}" for i, d in enumerate(docs, 1))

# LCEL 链：用 | 管道符串联（就是你这个月最值得记住的一行代码）
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 拆解这行代码：
print("""LCEL 链拆解:

  {
    "context": retriever | format_docs,    # ① 检索 → 拼成字符串 → 赋值给 context
    "question": RunnablePassthrough()       # ② 用户输入原样传 → 赋值给 question
  }
  | prompt                                   # ③ 把 {context, question} 填入 prompt 模板
  | llm                                      # ④ 调 DeepSeek 生成
  | StrOutputParser()                        # ⑤ 把 AI 消息对象转成纯文本字符串

  等价于: llm( prompt(context=format_docs(retriever(q)), question=q) )
""")

# 测试
print("提问: 怎么安装设备？")
answer = rag_chain.invoke("怎么安装设备？")
print(f"回答: {answer}\n")

print("提问: E01错误怎么办？")
answer = rag_chain.invoke("E01错误怎么办？")
print(f"回答: {answer}")


# ============================================================
# Part 4: 多轮对话记忆 — ConversationBufferMemory
# ============================================================

print("\n\n=== Part 4: 多轮对话记忆 ===\n")

# Day 9 你手写的多轮对话：手动拼 messages 列表
#   messages = [
#       {"role": "system", "content": "..."},
#       {"role": "user", "content": "第一轮问题"},
#       {"role": "assistant", "content": "第一轮回答"},
#       {"role": "user", "content": "第二轮问题"},
#   ]
# 每次调用都要把历史全传一遍

# LangChain 的 ConversationBufferMemory 自动管理历史
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory(return_messages=True)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=False,
)

print("第1轮:")
resp = conversation.invoke("我叫张三，是一名程序员")
print(f"  助手: {resp['response']}")

print("\n第2轮（不会忘掉我叫张三）:")
resp = conversation.invoke("我叫什么名字？做什么工作？")
print(f"  助手: {resp['response']}")

print(f"\n记忆中存储的历史: {memory.chat_memory.messages}")
print(f"共 {len(memory.chat_memory.messages)} 条消息")

print("""
多轮 RAG 的用法（结合检索 + 记忆）:
  用户在知识库上下文中追问时，历史对话和检索结果一起传给 LLM。
  第1轮: "产品怎么安装？" → RAG 检索 + 回答
  第2轮: "那保修期多久？"   → RAG 检索 + 前一轮历史 + 回答
  第3轮: "坏了怎么修？"     → RAG 检索 + 前两轮历史 + 回答
  
  每个追问不需要重新指定产品名，LLM 从历史里知道"那"指的是产品。
""")


print("*** Day 23 基础练习全部完成! ***")
print("\n关键结论：")
print("  1. RecursiveCharacterTextSplitter = 你 Day 16 的工业封装版")
print("  2. Retriever.invoke() = 统一的检索接口，屏蔽底层")
print("  3. LCEL 链 = retriever | format_docs | prompt | llm | StrOutputParser")
print("  4. ConversationBufferMemory = 自动管理 messages 历史")
