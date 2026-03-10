# Coding Agent 详细指南

通过 tmux 管理 Claude Code CLI 会话，让 NanoBot 能够执行编程任务。

---

## 0. ⚠️ 强制执行规则（必读）

**以下情况必须通过 tmux 启动 Claude Code，绝对不能用 exec/shell 命令替代**：

| 触发词 | 说明 |
|--------|------|
| 「用 Claude 帮我...」 | 用户明确指定要用 Claude |
| 「让 Claude 来...」 | 用户明确指定要用 Claude |
| 「Claude Code」 | 用户直接提到 Claude Code |
| 「方式2」 | 用户选择方式2（即 coding-agent） |
| 「/claude」 | 用户使用命令触发 |

**错误示例**（绝对禁止）：
```
用户: 用 Claude 帮我扫描项目结构
Bot: [偷懒直接用 exec 执行 ls 命令]  ❌ 错误！
```

**正确示例**：
```
用户: 用 Claude 帮我扫描项目结构
Bot: [执行 coding-agent.sh start]
     [执行 coding-agent.sh send "扫描项目结构"]
     [等待 Claude Code 执行]
     [捕获输出返回给用户]  ✅ 正确！
```

**为什么必须用 tmux**：
1. Claude Code 是一个交互式 CLI，需要长期运行的会话
2. NanoBot 的 exec 工具有 60 秒超时限制
3. 复杂任务需要多轮对话，tmux 可以保持状态
4. 用户明确要求用 Claude Code，必须尊重用户选择

**嵌套会话问题**：
- Claude Code 不允许在另一个 Claude Code 会话中启动
- 脚本已处理：使用 `unset CLAUDECODE && claude` 绕过检测
- 如果仍然失败，检查环境变量 `CLAUDECODE` 是否被正确清除

---

## 1. 核心功能

| 功能 | 说明 |
|------|------|
| 启动任务 | 在 tmux 中启动 Claude Code 执行编程任务 |
| 监控进度 | 定期检查任务执行状态 |
| 实时交互 | 向 Claude Code 发送消息、获取输出 |
| 会话管理 | 重置、销毁会话 |

---

## 2. 命令列表

### 2.1 /claude \<任务\>

启动一个新任务。如果 tmux 会话不存在，会自动创建。

**示例**：
```
/claude 帮我在 /home/ubuntu/my-project 目录下创建一个 Python 脚本
```

### 2.2 /claude status

查看当前 Claude Code 会话状态。

**返回**：
- `running` - 正在执行
- `waiting` - 等待输入
- `done` - 任务完成
- `no_session` - 无会话

### 2.3 /claude reset

销毁当前 tmux 会话并重新创建。用于：
- 任务卡住无法继续
- 需要切换到完全不同的任务
- 会话出现异常

### 2.4 /claude capture

获取 Claude Code 当前输出（最后 50 行）。

---

## 3. tmux 操作方法

### 3.1 会话信息

| 配置项 | 值 |
|--------|-----|
| 会话名称 | `claude-code` |
| 工作目录 | `/home/ubuntu` |
| Shell | `bash` |

### 3.2 核心命令

```bash
# 启动会话并运行 Claude Code
tmux new-session -d -s claude-code -c /home/ubuntu "claude"

# 发送消息（模拟用户输入）
tmux send-keys -t claude-code "用户消息内容" Enter

# 捕获输出（最后 50 行）
tmux capture-pane -t claude-code -p -S -50

# 检查会话是否存在
tmux has-session -t claude-code 2>/dev/null && echo "exists" || echo "not_exists"

# 销毁会话
tmux kill-session -t claude-code
```

### 3.3 辅助脚本

使用封装好的脚本简化操作：

```bash
# 启动
C:/Users/79345/.claude/skills/coding-agent/scripts/coding-agent.sh start

# 发送消息
C:/Users/79345/.claude/skills/coding-agent/scripts/coding-agent.sh send "帮我写个 hello world"

# 捕获输出
C:/Users/79345/.claude/skills/coding-agent/scripts/coding-agent.sh capture

# 检查状态
C:/Users/79345/.claude/skills/coding-agent/scripts/coding-agent.sh status

# 重置
C:/Users/79345/.claude/skills/coding-agent/scripts/coding-agent.sh reset

# 记录日志
C:/Users/79345/.claude/skills/coding-agent/scripts/coding-agent.sh log "任务完成：创建 hello.py"
```

---

## 4. 任务监控机制

### 4.1 监控流程

```
用户发送任务 → 启动 tmux 会话 → 定期检查状态 → 检测完成 → 汇报结果
```

### 4.2 检查频率

| 状态 | 检查间隔 | 超时处理 |
|------|----------|----------|
| 任务执行中 | 每 1 分钟 | 3 分钟无响应提醒用户 |
| 等待输入 | 立即通知用户 | 等待用户回复 |

### 4.3 状态检测逻辑

1. **running**: tmux 会话存在，最后几行没有提示符
2. **waiting**: 检测到 Claude Code 等待输入的特征（如 `>`、`?`、`[y/n]`）
3. **done**: 输出中包含 `[TASK_DONE]` 标记或任务完成特征

---

## 5. 任务完成检测

### 5.1 完成标记

Claude Code 完成任务后会在输出中显示：
- `Task completed successfully`
- 或用户在任务描述中约定 `[TASK_DONE]` 标记

### 5.2 等待输入特征

检测以下模式判断是否在等待输入：
```
>
?
[y/n]
(Y/n)
选择
请输入
```

---

## 6. 日志记录格式

### 6.1 日志文件

`C:/Users/79345/.claude/skills/coding-agent/logs/tasks.log`

### 6.2 日志格式

```
[2024-01-15 14:30:00] [START] 用户：帮我写个 hello world
[2024-01-15 14:32:15] [STATUS] 任务执行中
[2024-01-15 14:35:00] [WAITING] Claude 询问：使用什么语言？
[2024-01-15 14:35:30] [INPUT] 用户回复：Python
[2024-01-15 14:38:00] [DONE] 任务完成：创建 hello.py
```

### 6.3 日志级别

| 级别 | 说明 |
|------|------|
| START | 任务开始 |
| STATUS | 状态更新 |
| WAITING | 等待用户输入 |
| INPUT | 用户输入 |
| DONE | 任务完成 |
| ERROR | 错误发生 |

---

## 7. 示例对话流程

### 场景：用户请求创建脚本

```
用户: 用 Claude 帮我在 /home/ubuntu 目录下创建一个 Python 脚本，输出 hello world

Bot: [读取 GUIDE.md]
已读取：SKILL.md、GUIDE.md

好的，我来启动 Claude Code 执行这个任务。

[执行] coding-agent.sh start
[执行] coding-agent.sh send "在 /home/ubuntu 目录下创建一个 Python 脚本，输出 hello world"
[执行] coding-agent.sh log "[START] 创建 Python hello world 脚本"

Bot: 任务已启动，正在执行中...

[等待 1 分钟后检查]

[执行] coding-agent.sh status → waiting
[执行] coding-agent.sh capture

Bot: Claude Code 询问：您希望脚本命名为 hello.py 可以吗？

用户: 可以

[执行] coding-agent.sh send "可以，命名为 hello.py"
[执行] coding-agent.sh log "[INPUT] 用户确认命名"

[等待 30 秒后检查]

[执行] coding-agent.sh status → done
[执行] coding-agent.sh capture
[执行] coding-agent.sh log "[DONE] 创建 hello.py 成功"

Bot: 任务完成！已在 /home/ubuntu/hello.py 创建脚本。
```

---

## 8. 注意事项

### 8.1 超时处理

- NanoBot exec 工具默认 60 秒超时
- 长时间任务必须在 tmux 中运行，不能直接 exec
- 3 分钟无响应要主动提醒用户

### 8.2 会话冲突

- 确保会话名称 `claude-code` 不会与其他进程冲突
- 同一时间只能有一个活跃任务
- 新任务会覆盖旧任务（先提醒用户）

### 8.3 错误处理

| 错误 | 处理方式 |
|------|----------|
| tmux 会话不存在 | 自动创建新会话 |
| Claude Code 崩溃 | 重启会话，通知用户 |
| 权限不足 | 检查文件/目录权限，通知用户 |

### 8.4 安全注意

- 不要在 Claude Code 中执行危险命令（rm -rf、sudo 等）
- 修改重要文件前提醒用户确认
- 敏感信息不要记录到日志

---

## 9. 脚本实现参考

```bash
#!/bin/bash
# coding-agent.sh - Claude Code tmux 管理脚本

SESSION_NAME="claude-code"
WORK_DIR="/home/ubuntu"
LOG_FILE="C:/Users/79345/.claude/skills/coding-agent/logs/tasks.log"

log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$LOG_FILE"
}

case "$1" in
    start)
        if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
            echo "Session already exists"
        else
            tmux new-session -d -s "$SESSION_NAME" -c "$WORK_DIR" "claude"
            log_message "START" "Claude Code session started"
            echo "Session started"
        fi
        ;;
    send)
        tmux send-keys -t "$SESSION_NAME" "$2" Enter
        log_message "INPUT" "$2"
        ;;
    capture)
        tmux capture-pane -t "$SESSION_NAME" -p -S -50
        ;;
    status)
        if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
            echo "no_session"
        else
            # 检查最后几行是否在等待输入
            local output=$(tmux capture-pane -t "$SESSION_NAME" -p -S -5)
            if echo "$output" | grep -qE '(^\s*>|^\s*\?|\[y/n\]|\(Y/n\)|选择|请输入)'; then
                echo "waiting"
            elif echo "$output" | grep -qE '(Task completed|TASK_DONE)'; then
                echo "done"
            else
                echo "running"
            fi
        fi
        ;;
    reset)
        tmux kill-session -t "$SESSION_NAME" 2>/dev/null
        tmux new-session -d -s "$SESSION_NAME" -c "$WORK_DIR" "claude"
        log_message "RESET" "Session reset"
        echo "Session reset"
        ;;
    log)
        log_message "INFO" "$2"
        ;;
    *)
        echo "Usage: $0 {start|send|capture|status|reset|log}"
        exit 1
        ;;
esac
```

---

## 10. 快速参考

| 操作 | 命令 |
|------|------|
| 启动任务 | `/claude <任务描述>` |
| 查看状态 | `/claude status` |
| 获取输出 | `/claude capture` |
| 重置会话 | `/claude reset` |
| 脚本路径 | `C:/Users/79345/.claude/skills/coding-agent/scripts/coding-agent.sh` |
| 日志路径 | `C:/Users/79345/.claude/skills/coding-agent/logs/tasks.log` |
