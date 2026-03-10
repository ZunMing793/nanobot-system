---
name: skill-creator
description: 创建、重构 skills。触发场景：(1) 创建新skill：用户说"创建一个skill"、"帮我写个skill"、"把这个流程做成skill"；(2) 重构现有skill：用户说"重构这个skill"、"这个skill太长了"、"按照新标准重构"；(3) 查看skill规范：用户问"skill怎么写"、"skill格式是什么"。
always: true
---

# Skill 创建器

创建和重构符合 NanoBot 标准的 skills。

## 触发场景

- 用户说"创建一个skill"、"帮我写个skill"
- 用户说"把这个流程做成skill"
- 用户说"重构这个skill"、"这个skill太长了"
- 用户问"skill怎么写"、"skill格式是什么"

---

## ⚠️ 执行前必读

**决定使用此 skill 后，必须先读取**：
`C:/Users/79345/.claude/skills/skill-creator/GUIDE.md`

**禁止事项**：
- ❌ 不准偷懒不读取 skill 的其他详细文件
- ❌ 不准直接用 SKILL.md 中的精简格式给用户输出
- ❌ 这是撒谎行为，会导致创建的 skill 不合格

**输出要求**：
- 创建/重构 skill 前，必须先展示计划给用户确认
- 输出开头必须列出：「已读取：SKILL.md、GUIDE.md」

---

## 详细指南

完整创建能力需要读取 `GUIDE.md`，包含：

- SKILL.md 标准结构（40-60行）
- GUIDE.md 标准结构
- 执行前必读模块标准写法
- 创建流程（访谈→草稿→确认→创建）
- 重构流程（分析→计划→确认→执行）
- 文件命名规范
- 上下文成本估算
