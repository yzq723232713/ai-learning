# AI 应用开发学习记录

从零自学 AI 应用开发（RAG、Agent、大模型应用），4 个月学习路线。

## 进度

### 第 1 周：Python 基础

| 天数 | 内容 | 状态 |
|------|------|------|
| Day 1 | Python 基础语法 | ✅ |
| Day 2 | 函数与面向对象 | ✅ |
| Day 3 | 类型系统 + Pydantic | ✅ |
| Day 4 | 异步编程 asyncio | ✅ |
| Day 5 | 包管理 + 工程化 | ✅ |
| Day 6 | 综合练习（文件扫描 + 异步下载） | ✅ |
| Day 7 | 休息 | — |

### 第 2 周：LLM 基础

| 天数 | 内容 | 状态 |
|------|------|------|
| Day 8 | LLM 概念 + Token | ✅ |
| Day 9 | DeepSeek API 调用 | ✅ |
| Day 10 | Embedding 向量化 | ✅ |
| Day 11 | Transformer 架构 | ✅ |
| Day 12 | Prompt Engineering | ✅ |
| Day 13 | Function Calling | ✅ |
| Day 14 | 第 2 周复习 | ✅ |

### 第 3 周：RAG 全链路

| 天数 | 内容 | 状态 |
|------|------|------|
| Day 15 | RAG 全景 + 文档加载器 | ✅ |
| Day 16 | Chunking 三种切分策略 | ✅ |
| Day 17 | Embedding 管道 + 检索 | ✅ |
| Day 18 | 向量数据库 Chroma + FAISS | ✅ |
| Day 19 | 手搓 RAG 全链路（无框架） | ✅ |
| Day 20 | 检索优化（多路召回 + Reranker） | ✅ |
| Day 21 | 休息 | — |

### 第 4 周：LangChain + LlamaIndex + 高级检索

| 天数 | 内容 | 状态 |
|------|------|------|
| Day 22 | LangChain 核心抽象 | ✅ |
| Day 23 | LangChain RAG 深入 | ✅ |
| Day 24 | LlamaIndex 入门 | ✅ |
| Day 25 | 高级 RAG（Self-query / Multi-query / Parent Doc） | ✅ |
| Day 26 | RAGAS 评估 4 指标 | ✅ |
| Day 27 | 个人知识库实战 | ✅ |
| Day 28 | 休息 | — |

### 第 5 周：项目一 — 企业知识库 RAG 系统

| 天数 | 内容 | 状态 |
|------|------|------|
| Day 29 | 项目规划 + 骨架搭建 | ✅ |
| Day 30 | 文档加载器 + 测试 | ✅ |
| Day 31 | 文本切分 + 统计验证 | ✅ |
| Day 32 | Embedding 模块 | ✅ |
| Day 33 | 向量存储 + 元数据过滤 | ✅ |
| Day 34 | 检索模块（混合检索 + Reranker） | ✅ |
| Day 35 | 生成模块（Prompt + DeepSeek） | ✅ |
| Day 36 | FastAPI（5 端点 + CORS + 流式） | ✅ |
| Day 37 | 端到端集成测试 | ✅ |
| Day 38 | Streamlit 极简 UI | ✅ |
| Day 39 | RAGAS 评估 + 优化日记 | ✅ |

## 项目

### [ai-knowledge-base](https://github.com/yzq723232713/ai-knowledge-base) — 企业知识库 RAG 问答系统

项目目录：`D:\ai-knowledge-base\`

```
src/
├── loader/       # 文档加载 (Day 30)
├── chunker/      # 文本切分 (Day 31)
├── embedder/     # 向量化
├── retriever/    # 检索
├── generator/    # LLM 生成
└── api/          # FastAPI 接口
```

## 目录结构

### 第 1 周：Python 基础
- `day01/` — Python 基础语法、列表推导式
- `day02/` — 函数、类、魔术方法、@property
- `day03/` — Type Hints、dataclass、Pydantic、文件读写
- `day04/` — 异步编程 asyncio、aiohttp
- `day05/` — Poetry 包管理、pyproject.toml、dotenv、logging
- `day06/` — 综合练习（文件扫描器 + 异步下载）

### 第 2 周：LLM 基础
- `day08/` — Token 概念、tiktoken、中英文 token 效率对比
- `day09/` — DeepSeek API 调用、temperature、stream、System Prompt
- `day10/` — Embedding 向量化、余弦相似度、本地模型 bge-small-zh
- `day11/` — Transformer 架构（定性）、Attention 机制、三种架构对比
- `day12/` — Prompt Engineering 四大技巧：角色/Few-shot/思维链/JSON
- `day13/` — Function Calling 完整循环、多工具自动选择
- `day14/` — 第 2 周复习（24 题自检清单）

### 第 3 周：RAG 全链路
- `day15/` — RAG 两阶段架构、PyMuPDF/python-docx 加载、DocumentLoader
- `day16/` — 固定长度/按分隔符/递归切分、overlap、RecursiveCharacterTextSplitter
- `day17/` — Embedding 模型选型、批量向量化、综合流水线（加载→切块→检索）
- `day18/` — Chroma 基础操作+元数据过滤、FAISS IndexFlatL2/IndexIVFFlat
- `day19/` — 手搓 RAG 全链路（加载→切块→Embedding→Chroma→拼Prompt→DeepSeek）
- `day20/` — 多路召回(BM25+RRF)、Reranker(bge-reranker-v2-m3)精排

### 第 4 周：LangChain + LlamaIndex + 高级检索
- `day22/` — LangChain 五⼤抽象：PromptTemplate/ChatModel/Chain/Retriever/Document
- `day23/` — LCEL 管道符链、ConversationBufferMemory 多轮对话
- `day24/` — LlamaIndex SimpleDirectoryReader、VectorStoreIndex、IngestionPipeline
- `day25/` — Self-querying、Multi-query、Parent Document Retriever 三种高级检索
- `day26/` — RAGAS 评估：context_precision/recall/faithfulness/answer_relevancy
- `day27/` — 个人知识库系统：扫描 D:\learn 全部笔记 → RAG 问答

### 第 5 周：项目一 — 企业知识库 RAG — [项目仓库](https://github.com/yzq723232713/ai-knowledge-base)
- `day29` — 项目规划 + 骨架搭建
- `day30` — 文档加载器（4 种格式 + 错误处理）
- `day31` — 文本切分（递归降级 + overlap + 统计）
- `day32` — Embedding 模块（本地 + API 双方案）
- `day33` — Chroma 向量库封装 + 元数据过滤
- `day34` — 混合检索（向量+BM25+RRF）+ Reranker 精排
- `day35` — Generator 生成模块（Prompt 拼接 + 流式 + 引用）
- `day36` — FastAPI 5 端点（upload/search/chat/stream）+ CORS
- `day37` — 端到端集成测试
- `day38` — Streamlit UI（文件上传 + 流式问答）
- `day39` — RAGAS 评估 + 优化日记（三策略对比：Baseline/Hybrid/Hybrid+Rerank）

## 技术栈

| 类别 | 工具/库 |
|------|--------|
| 语言 | Python 3.12 |
| LLM API | DeepSeek（OpenAI 兼容 SDK） |
| 本地 Embedding | sentence-transformers、bge-small-zh-v1.5 |
| Reranker | bge-reranker-v2-m3（ModelScope 下载） |
| 向量数据库 | Chroma、FAISS |
| 关键词检索 | rank-bm25、jieba 分词 |
| 文档解析 | PyMuPDF、python-docx |
| 框架 | LangChain、LlamaIndex |
| 评估 | RAGAS（手写版 + 框架版） |
| Web 服务 | FastAPI、uvicorn |
| 数据校验 | Pydantic |
| 异步 | asyncio、aiohttp |
| 测试 | pytest |
| 包管理 | Poetry |
| 环境变量 | python-dotenv |

## 环境

- Python 3.12
- 模型缓存：`~/.cache/huggingface/`（bge-small）、`~/.cache/modelscope/`（bge-reranker）
