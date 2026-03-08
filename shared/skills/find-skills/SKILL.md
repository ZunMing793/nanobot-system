---
name: find-skills
description: "Helps users discover and install agent skills when they ask questions like 'how do I do X', 'find a skill for X', 'is there a skill that can...', or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill."
always: true
allowed-tools:
  - Bash
  - Read
---

## ⚠️ 执行前�
�?
**决定使用�?skill 后，�
须�
�读�?*�?`find-skills/GUIDE.md`

**禁止事项**�?- �?不准偷懒不读�?skill 的�
�他详细文�?- �?不准直接�?SKILL.md 中的精简格式给用户输�?
**输出要求**�?- 输出开头�
须列出：「已读取：SKILL.md、GUIDE.md�?
## 触发场景

当用户出现以下行为时使用�?skill�?- 询问"如何�?X"�?有没有技能可以做 X"
- �?find a skill for X"�?is there a skill for X"
- 询问"你能�?X �?（X 为专业能力）
- 表达对扩�?agent 能力的�
��?- 想搜索工�
�、模板或工作�?- 询问"有哪些可用的技�?或想浏览技能目�?- 提到需要某个领域的帮助（设计、测试、部署等�?
## 双平台搜�?
�?skill 支持两个互补的平台：
- **skills.sh**：官方注册表，精选质量技�?- **ClawHub**：更广泛的社区技�?
## 详细指南索引

完整�
容请�
读：GUIDE.md

- 两大平台搜索命令与在线浏�?- 用户明确需求时的搜索流�?- 用户不明确需求时的引导策�?- NanoBot 系统的三种安�
方法（ClawHub 推荐�?- 手动下载方法（网络�
时场景）
- 常见错误与解决方�?- 安�
后检查�
�?- 常用技能分类目�?