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

## 目录结构

### 第 1 周
- `day01/` — Python 基础语法、列表推导式
- `day02/` — 函数、类、魔术方法、@property
- `day03/` — Type Hints、dataclass、Pydantic、文件读写
- `day04/` — 异步编程 asyncio、aiohttp
- `day05/` — Poetry 包管理、pyproject.toml、dotenv、logging
- `day06/` — 综合练习（文件扫描器 + 异步下载）

### 第 2 周
- `day08/` — Token 概念、tiktoken、中英文 token 效率对比
- `day09/` — DeepSeek API 调用、temperature、stream、System Prompt
- `day10/` — Embedding 向量化、余弦相似度、本地模型 bge-small-zh
- `day11/` — Transformer 架构（定性）、Attention 机制、三种架构对比
- `day12/` — Prompt Engineering 四大技巧：角色/Few-shot/思维链/JSON
- `day13/` — Function Calling 完整循环、多工具自动选择
- `day14/` — 第 2 周复习（24 题自检清单）

## 技术栈

| 类别 | 工具/库 |
|------|--------|
| 语言 | Python 3.12 |
| LLM API | DeepSeek（OpenAI 兼容 SDK） |
| 向量化 | sentence-transformers、bge-small-zh-v1.5 |
| 数据校验 | Pydantic |
| 异步 | asyncio、aiohttp |
| 包管理 | Poetry |
| 环境变量 | python-dotenv |

## 环境

- Python 3.12
- 依赖见各 day 目录及 pyproject.toml
