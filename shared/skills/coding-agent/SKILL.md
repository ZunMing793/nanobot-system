---
name: coding-agent
description: "让 NanoBot 调用 Claude Code CLI 执行编程任务。触发场景：用户说'用 Claude 帮我...'、'让 Claude 来...'、'Claude Code...'、'/claude 命令'、'写代码'、'修改代码'、'调试代码'"
always: true
---

# Coding Agent

让 NanoBot 调用 Claude Code CLI 执行编程任务，通过 tmux 管理长期运行的会话。

## 触发场景

- 用户说「用 Claude 帮我...」「让 Claude 来...」
- 用户提到「Claude Code」「/claude」命令
- 用户请求「写代码」「修改代码」「调试代码」「重构代码」
- 用户指定要修改某个项目的代码
- 用户说「帮我看看这个 bug」「实现一个功能」

---

## ⚠️ 执行前必读

**决定使用此 skill 后，必须先读取**：
`C:/Users/79345/.claude/skills/coding-agent/GUIDE.md`

**禁止事项**：
- ❌ 不准偷懒不读取 skill 的其他详细文件
- ❌ 不准直接用 SKILL.md 中的精简格式给用户输出
- ❌ 不准直接用 exec/shell 命令替代 Claude Code（这是最严重的偷懒！）
- ❌ 这是撒谎行为，会导致输出质量不合格

**强制执行**：
- ⚠️ 当用户说「用 Claude」「让 Claude」「Claude Code」「方式2」时，**必须**通过 tmux 启动 Claude Code
- ⚠️ 即使任务看起来简单，只要用户明确要求用 Claude Code，就必须用 tmux 方式
- ⚠️ 正确流程：`coding-agent.sh start` → `coding-agent.sh send "任务"` → 监控状态

**输出要求**：
- 输出开头必须列出：「已读取：SKILL.md、GUIDE.md」

---

## 详细指南

完整能力需要读取 `GUIDE.md`，包含：
- 命令列表（/claude、/claude status、/claude reset）
- tmux 操作方法
- 任务监控机制
- 任务完成检测
- 日志记录格式
- 示例对话流程
- 注意事项
