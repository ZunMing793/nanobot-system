---
name: Agent Browser
description: 网页自动化浏览器，可读取微信公众号文章、截图、自动化操作。当用户需要读取网页内容、访问微信公众号、进行网页自动化操作、截图时使用。
always: true
metadata: {"clawdbot":{"emoji":"🌐"}}
allowed-tools: Bash(agent-browser:*,ab:*)
---

# Agent Browser 网页自动化

网页自动化浏览器，支持读取微信公众号文章、截图、自动化操作。

## 触发场景

- 读取微信公众号文章
- 读取网页内容
- 网页自动化操作
- 网页截图
- 用户说"打开这个网页"、"获取这个页面"

---

## ⚠️ 执行前必读

**决定使用此 skill 后，必须先读取**：
`C:/Users/79345/.claude/skills/agent-browser/GUIDE.md`

**禁止事项**：
- ❌ 不准偷懒不读取 skill 的其他详细文件
- ❌ 不准直接用 SKILL.md 中的精简格式给用户输出
- ❌ 这是撒谎行为，会导致操作失败或内容获取不完整

**输出要求**：
- 输出开头必须列出：「已读取：SKILL.md、GUIDE.md」

---

## 详细指南

完整操作能力需要读取 `GUIDE.md`，包含：
- 快速使用方法（ab 命令）
- 读取微信公众号文章
- 常用命令详解
- 注意事项
