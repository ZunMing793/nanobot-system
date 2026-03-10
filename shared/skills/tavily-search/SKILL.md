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

AI 优化的网络搜索，返回简洁、相关的结果。

## 触发场景

- 用户需要搜索网络信息
- 用户需要查找最新资讯
- 用户需要研究某个话题
- 用户问"搜索一下..."

---

## ⚠️ 执行前必读

**决定使用此 skill 后，必须先读取**：
`C:/Users/79345/.claude/skills/tavily-search/GUIDE.md`

**禁止事项**：
- ❌ 不准偷懒不读取 skill 的其他详细文件
- ❌ 不准直接用 SKILL.md 中的精简格式给用户输出
- ❌ 这是撒谎行为，会导致搜索质量不合格

**输出要求**：
- 输出开头必须列出：「已读取：SKILL.md、GUIDE.md」

---

## 详细指南

完整搜索能力需要读取 `GUIDE.md`，包含：
- 搜索命令详解
- 参数选项说明
- URL 内容提取
- 使用技巧
