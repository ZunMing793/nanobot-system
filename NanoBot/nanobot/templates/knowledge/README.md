# 知识库
> 本目录用于存放 bot 可复用的外部资料,与记忆/经验文件分层管理。

## 目录说明

- `raw/`:原始资料,如 `pdf`、`docx`、`epub`、`md`、`txt`
- `extracted/`:从原始资料提取出的可读文本缓存
- `index/`:索引、摘要、标签、清单

## 使用原则

- 先把原始文件放进 `raw/`
- 先阅读 `index/CATALOG.md` 和 `index/manifest.json`
- 需要时再调用对应 skill 或解析器读取原文件
- 提取结果尽量缓存到 `extracted/`,避免重复解析
- 可运行 `python scripts/ingest_knowledge.py` 更新索引与提取缓存
