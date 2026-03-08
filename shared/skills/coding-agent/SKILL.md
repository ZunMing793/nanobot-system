---
name: coding-agent
description: "�?NanoBot 调用 Claude Code CLI 执行编程任务。触发场景：用户�?�?Claude 帮我...'�?�?Claude �?..'�?Claude Code...'�?/claude 命令'�?写代�?�?修改代码'�?调试代码'"
always: true
---

# Coding Agent

�?NanoBot 调用 Claude Code CLI 执行编程任务，通过 tmux 管理长期运行的会话�?
## 触发场景

- 用户说「用 Claude 帮我...」「让 Claude �?..�?- 用户提到「Claude Code」�?claude」命�?- 用户请求「写代码」「修改代码」「调试代码」「重构代码�?- 用户指定要修改某个项目的代码
- 用户说「帮我看看这�?bug」「实现一个功能�?
---

## ⚠️ 执行前�
�?
**决定使用�?skill 后，�
须�
�读�?*�?`coding-agent/GUIDE.md`

**禁止事项**�?- �?不准偷懒不读�?skill 的�
�他详细文�?- �?不准直接�?SKILL.md 中的精简格式给用户输�?- �?不准直接�?exec/shell 命令替代 Claude Code（这是最严重的偷懒！�?- �?这是撒谎行为，会导致输出质量不合�?
**强制执行**�?- ⚠️ 当用户说「用 Claude」「让 Claude」「Claude Code」「方�?」时�?*�
须**通过 tmux 启动 Claude Code
- ⚠️ 即使任务看起来简单，只要用户明确要求�?Claude Code，就�
须�?tmux 方式
- ⚠️ 正确流程：`coding-agent.sh start` �?`coding-agent.sh send "任务"` �?监控状�?
**输出要求**�?- 输出开头�
须列出：「已读取：SKILL.md、GUIDE.md�?
---

## 详细指南

完整能力需要读�?`GUIDE.md`，�
含：
- 命令列表�?claude�?claude status�?claude reset�?- tmux 操作方法
- 任务监控机制
- 任务完成检�?- 日志记录格式
- 示例对话流程
- 注意事项
