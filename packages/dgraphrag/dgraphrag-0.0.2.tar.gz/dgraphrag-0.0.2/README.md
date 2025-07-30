# dgraphrag

👉 **Use the GraphRAG Accelerator**  
👉 **Read the docs**  
👉 **GraphRAG Arxiv**  

[![PyPI version](https://img.shields.io/pypi/v/dgraphrag.svg?logo=pypi)](https://pypi.org/project/dgraphrag/)  
[![Downloads](https://static.pepy.tech/badge/dgraphrag)](https://pepy.tech/project/dgraphrag)

---

## Overview

`dgraphrag` 是一个端到端 **GraphRAG** 工具包，帮助开发者从原始文本到知识图，再到 LLM 检索增强生成，串联完整流程并提供可插拔组件。
本项目由 [eust-w](https://github.com/eust-w) 发起，由 **D-Robotics**（<https://d-robotics.cc/>）开源。

要了解 GraphRAG 如何从非结构化数据中构建知识图并增强 LLM，请参考[官方文档](https://d-robotics.cc/docs)。

---

## Quickstart

```bash
pip install dgraphrag[neo4j,openai]         # 典型组合
dgrag ingest docs/                          # 构建图
dgrag ask "What is GraphRAG?"               # 提问
```

详细教程见 [docs/quickstart.md](docs/quickstart.md)。

---

## Repository Guidance

本仓库提供一个最小可行实现（MVP），方便你快速试用 GraphRAG 思路。请注意，默认索引构建与 LLM API 调用可能产生成本，使用前请理解相应流程及费用。

> ⚠️ **Warning:** `dgrag index` 可能在大规模数据时耗费较多资源，请先评估数据量与预算。

---

## Diving Deeper

- 了解核心概念与原理，阅读[设计文档](docs/design.md)  
- 想参与开发？请查看 [CONTRIBUTING.md](CONTRIBUTING.md)  
- 加入社区讨论：GitHub Discussions / Slack (#dgraphrag)

---

## Prompt Tuning

使用你自己的数据与 LLM 时，参考[提示工程指南](docs/prompt_tuning.md) 来微调或构建高质量 prompt。

---

## Versioning

版本遵循 *语义化版本* (SemVer)。重大变更请查看 [CHANGELOG.md](CHANGELOG.md)。  
使用前请始终运行：

```bash
dgrag info   # 检查当前索引版本与配置格式
```

---

## Responsible AI FAQ

详见 [RAI_TRANSPARENCY.md](RAI_TRANSPARENCY.md)，其中解答了：

- GraphRAG 是什么？  
- 它能做些什么？  
- 潜在的局限与风险？  
- ……

---

## Trademarks

本项目可能包含第三方商标或徽标，其所有权归原持有人所有。本仓库仅出于学术与工程示范目的使用，不代表对这些商标或徽标的任何认可。

---

## Privacy

dgraphrag 不会在本地以外收集或存储任何用户数据；所有内容均在你的控制下处理。请在提交敏感数据前自行评估风险。

---
```bash
pip install dgraphrag[arangodb,tigergraph,vector]
# 或者开发模式
pip install -e .[arangodb,tigergraph,vector]
```

## Quick Start
```python
from pathlib import Path

from dgraphrag import (
    LocalTextLoader,
    SimpleParagraphSplitter,
    RegexExtractor,
    InMemoryGraphAdapter,
    SimpleGraphBuilder,
    BasicGraphRetriever,
)

# create a small demo file
Path("demo.txt").write_text("GraphRAG is RetrievalAugmentedGeneration.\n\nRetrievalAugmentedGeneration is Powerful.")

loader = LocalTextLoader()
text = loader.load("demo.txt")

paragraphs = SimpleParagraphSplitter().split(text)
triples = RegexExtractor().extract(paragraphs)

adapter = InMemoryGraphAdapter()
SimpleGraphBuilder(adapter).build(triples)

retriever = BasicGraphRetriever(adapter)
print(retriever.answer("What is GraphRAG?"))
```
