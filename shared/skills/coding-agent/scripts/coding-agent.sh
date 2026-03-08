#!/bin/bash
# coding-agent.sh - Claude Code tmux 管理脚本
#
# 用法：
#   coding-agent.sh start              # 启动 tmux 会话和 Claude Code
#   coding-agent.sh send "消息"         # 发送消息到 Claude Code
#   coding-agent.sh capture            # 获取当前输出（最后50行）
#   coding-agent.sh status             # 检查状态（running/waiting/done/no_session）
#   coding-agent.sh reset              # 销毁并重建会话
#   coding-agent.sh log "摘要"          # 记录任务日志
#   coding-agent.sh wait-for-input     # 检测是否在等待输入

SESSION_NAME="claude-code"
WORK_DIR="/home/ubuntu"
LOG_FILE="/home/NanoBot/shared/skills/coding-agent/logs/tasks.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$LOG_FILE"
}

# 检查会话是否存在
session_exists() {
    tmux has-session -t "$SESSION_NAME" 2>/dev/null
}

# 启动会话
do_start() {
    if session_exists; then
        echo "status: already_running"
        echo "message: Claude Code 会话已存在"
    else
        # 重要：unset CLAUDECODE 以允许在 Claude Code 环境中嵌套启动
        tmux new-session -d -s "$SESSION_NAME" -c "$WORK_DIR" "unset CLAUDECODE && claude"
        log_message "START" "Claude Code session started"
        echo "status: started"
        echo "message: Claude Code 会话已启动"
    fi
}

# 发送消息
do_send() {
    local message="$1"
    if [ -z "$message" ]; then
        echo "status: error"
        echo "message: 请提供要发送的消息"
        return 1
    fi

    if ! session_exists; then
        # 会话不存在，自动启动
        do_start > /dev/null
        sleep 2  # 等待 Claude Code 启动
    fi

    tmux send-keys -t "$SESSION_NAME" "$message" Enter
    log_message "INPUT" "$message"
    echo "status: sent"
    echo "message: 消息已发送"
}

# 捕获输出
do_capture() {
    if ! session_exists; then
        echo "status: no_session"
        echo "message: 无活跃会话"
        return 1
    fi

    tmux capture-pane -t "$SESSION_NAME" -p -S -50
}

# 检查状态
do_status() {
    if ! session_exists; then
        echo "no_session"
        return 0
    fi

    # 获取最后几行输出
    local output
    output=$(tmux capture-pane -t "$SESSION_NAME" -p -S -10 2>/dev/null)

    # 检查是否在等待输入
    if echo "$output" | grep -qE '(^\s*>|^\s*\?|\[y/n\]|\[Y/n\]|\(Y/n\)|选择|请输入|Enter|❯)'; then
        echo "waiting"
    # 检查是否任务完成
    elif echo "$output" | grep -qE '(Task completed|TASK_DONE|successfully|完成)'; then
        echo "done"
    else
        echo "running"
    fi
}

# 等待输入检测（详细版）
do_wait_for_input() {
    if ! session_exists; then
        echo "status: no_session"
        echo "waiting: false"
        return 0
    fi

    local output
    output=$(tmux capture-pane -t "$SESSION_NAME" -p -S -5 2>/dev/null)

    if echo "$output" | grep -qE '(^\s*>|^\s*\?|\[y/n\]|\[Y/n\]|\(Y/n\)|选择|请输入|Enter|❯)'; then
        echo "status: waiting"
        echo "waiting: true"
        echo "last_lines:"
        echo "$output"
    else
        echo "status: running"
        echo "waiting: false"
    fi
}

# 重置会话
do_reset() {
    if session_exists; then
        tmux kill-session -t "$SESSION_NAME"
    fi

    # 重要：unset CLAUDECODE 以允许在 Claude Code 环境中嵌套启动
    tmux new-session -d -s "$SESSION_NAME" -c "$WORK_DIR" "unset CLAUDECODE && claude"
    log_message "RESET" "Session reset"
    echo "status: reset"
    echo "message: 会话已重置"
}

# 记录日志
do_log() {
    local message="$1"
    if [ -z "$message" ]; then
        echo "status: error"
        echo "message: 请提供日志内容"
        return 1
    fi

    log_message "INFO" "$message"
    echo "status: logged"
    echo "message: 日志已记录"
}

# 帮助信息
do_help() {
    cat << 'EOF'
coding-agent.sh - Claude Code tmux 管理脚本

用法：
  coding-agent.sh start              启动 tmux 会话和 Claude Code
  coding-agent.sh send "消息"         发送消息到 Claude Code
  coding-agent.sh capture            获取当前输出（最后50行）
  coding-agent.sh status             检查状态（running/waiting/done/no_session）
  coding-agent.sh reset              销毁并重建会话
  coding-agent.sh log "摘要"          记录任务日志
  coding-agent.sh wait-for-input     检测是否在等待输入（详细输出）
  coding-agent.sh help               显示帮助信息

状态说明：
  no_session  - 无活跃会话
  running     - 正在执行
  waiting     - 等待用户输入
  done        - 任务完成

示例：
  coding-agent.sh start
  coding-agent.sh send "帮我创建一个 hello.py 文件"
  coding-agent.sh status
  coding-agent.sh capture
  coding-agent.sh log "任务完成：创建 hello.py"
EOF
}

# 主入口
case "$1" in
    start)
        do_start
        ;;
    send)
        do_send "$2"
        ;;
    capture)
        do_capture
        ;;
    status)
        do_status
        ;;
    reset)
        do_reset
        ;;
    log)
        do_log "$2"
        ;;
    wait-for-input)
        do_wait_for_input
        ;;
    help|--help|-h)
        do_help
        ;;
    *)
        echo "错误：未知命令 '$1'"
        echo "运行 'coding-agent.sh help' 查看帮助"
        exit 1
        ;;
esac
