---
name: tavily
description: AI-optimized web search via Tavily API. 当用户需要搜索网络信息、查找最新资讯、研究某个话题时使用。Returns concise, relevant results for AI agents.
always: true
homepage: https://tavily.com
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["node"]}}}
allowed-tools:
  - Bash(node:*)
  - Read
---

# Tavily Search

AI 优化的网络搜索，返回简洁、相�
�的结果�?
## 触发场景

- 用户需要搜索网络信�?- 用户需要查找最新资�?- 用户需要研究某个话�?- 用户�?搜索一�?.."

---

## ⚠️ 执行前�
�?
**决定使用�?skill 后，�
须�
�读�?*�?`tavily-search/GUIDE.md`

**禁止事项**�?- �?不准偷懒不读�?skill 的�
�他详细文�?- �?不准直接�?SKILL.md 中的精简格式给用户输�?- �?这是撒谎行为，会导致搜索质量不合�?
**输出要求**�?- 输出开头�
须列出：「已读取：SKILL.md、GUIDE.md�?
---

## 详细指南

完整搜索能力需要读�?`GUIDE.md`，�
含：
- 搜索命令详解
- 参数选项说明
- URL �
容提取
- 使用技�?