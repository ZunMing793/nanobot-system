---
name: find-skills
description: "Helps users discover and install agent skills when they ask questions like 'how do I do X', 'find a skill for X', 'is there a skill that can...', or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill."
always: true
allowed-tools:
  - Bash
  - Read
---

## ⚠️ 执行前必读

**决定使用此 skill 后，必须先读取**：
`C:/Users/79345/.claude/skills/find-skills/GUIDE.md`

**禁止事项**：
- ❌ 不准偷懒不读取 skill 的其他详细文件
- ❌ 不准直接用 SKILL.md 中的精简格式给用户输出

**输出要求**：
- 输出开头必须列出：「已读取：SKILL.md、GUIDE.md」

## 触发场景

当用户出现以下行为时使用此 skill：
- 询问"如何做 X"、"有没有技能可以做 X"
- 说"find a skill for X"或"is there a skill for X"
- 询问"你能做 X 吗"（X 为专业能力）
- 表达对扩展 agent 能力的兴趣
- 想搜索工具、模板或工作流
- 询问"有哪些可用的技能"或想浏览技能目录
- 提到需要某个领域的帮助（设计、测试、部署等）

## 双平台搜索

本 skill 支持两个互补的平台：
- **skills.sh**：官方注册表，精选质量技能
- **ClawHub**：更广泛的社区技能

## 详细指南索引

完整内容请阅读：GUIDE.md

- 两大平台搜索命令与在线浏览
- 用户明确需求时的搜索流程
- 用户不明确需求时的引导策略
- NanoBot 系统的三种安装方法（ClawHub 推荐）
- 手动下载方法（网络超时场景）
- 常见错误与解决方案
- 安装后检查清单
- 常用技能分类目录
