#!/bin/bash
#
# NanoBot Multi-Bot System Manager
# 用于管理多个 bot 进程的启动、停止、重启和状态查看
#

set -e

# 配置
BOT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="/tmp/nanobot"
LOG_DIR="$BOT_ROOT/shared/logs"
VENV_PYTHON="$BOT_ROOT/.venv/bin/python"

# Bot 列表
BOTS=("bot1_core" "bot2_health" "bot3_finance" "bot4_emotion" "bot5_media")

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 创建必要的目录
mkdir -p "$PID_DIR"
mkdir -p "$LOG_DIR"

# 打印帮助
print_help() {
    echo "NanoBot Multi-Bot System Manager"
    echo ""
    echo "Usage: $0 <command> [bot_id]"
    echo ""
    echo "Commands:"
    echo "  start <bot_id>    启动指定 bot"
    echo "  stop <bot_id>     停止指定 bot"
    echo "  restart <bot_id>  重启指定 bot"
    echo "  status [bot_id]   查看状态（不指定则显示所有）"
    echo "  logs <bot_id>     查看指定 bot 日志"
    echo "  start-all         启动所有 bot"
    echo "  stop-all          停止所有 bot"
    echo "  restart-all       重启所有 bot"
    echo ""
    echo "Bot IDs:"
    for bot in "${BOTS[@]}"; do
        echo "  $bot"
    done
}

# 检查 bot 是否在运行
is_running() {
    local bot_id=$1
    local pid_file="$PID_DIR/${bot_id}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# 获取 bot 状态
get_status() {
    local bot_id=$1
    if is_running "$bot_id"; then
        echo -e "${GREEN}运行中${NC}"
    else
        echo -e "${RED}已停止${NC}"
    fi
}

# 启动 bot
start_bot() {
    local bot_id=$1
    local bot_dir="$BOT_ROOT/$bot_id"
    local pid_file="$PID_DIR/${bot_id}.pid"
    local log_file="$bot_dir/logs/bot.log"
    
    if is_running "$bot_id"; then
        echo -e "${YELLOW}$bot_id 已经在运行${NC}"
        return 1
    fi
    
    if [ ! -d "$bot_dir" ]; then
        echo -e "${RED}错误: $bot_id 目录不存在${NC}"
        return 1
    fi
    
    echo -e "${BLUE}启动 $bot_id...${NC}"
    
    cd "$bot_dir"
    mkdir -p logs
    
    # 使用虚拟环境中的 Python
    local python_cmd="$VENV_PYTHON"
    if [ ! -f "$python_cmd" ]; then
        python_cmd="python3"
    fi
    
    # 启动 bot (使用 gateway 命令)
    nohup "$python_cmd" -m nanobot gateway --config config.json > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    
    sleep 1
    
    if is_running "$bot_id"; then
        echo -e "${GREEN}$bot_id 启动成功 (PID: $pid)${NC}"
    else
        echo -e "${RED}$bot_id 启动失败，请检查日志: $log_file${NC}"
        rm -f "$pid_file"
        return 1
    fi
}

# 停止 bot
stop_bot() {
    local bot_id=$1
    local pid_file="$PID_DIR/${bot_id}.pid"
    
    if ! is_running "$bot_id"; then
        echo -e "${YELLOW}$bot_id 未在运行${NC}"
        return 0
    fi
    
    local pid=$(cat "$pid_file")
    echo -e "${BLUE}停止 $bot_id (PID: $pid)...${NC}"
    
    kill "$pid" 2>/dev/null || true
    
    # 等待进程结束
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    # 如果进程还在运行，强制杀死
    if ps -p "$pid" > /dev/null 2>&1; then
        echo -e "${YELLOW}强制停止 $bot_id...${NC}"
        kill -9 "$pid" 2>/dev/null || true
    fi
    
    rm -f "$pid_file"
    echo -e "${GREEN}$bot_id 已停止${NC}"
}

# 重启 bot
restart_bot() {
    local bot_id=$1
    stop_bot "$bot_id"
    sleep 2
    start_bot "$bot_id"
}

# 查看状态
show_status() {
    local bot_id=$1
    
    if [ -n "$bot_id" ]; then
        echo -e "$bot_id: $(get_status "$bot_id")"
    else
        echo "Bot 状态:"
        echo "----------------------------------------"
        for bot in "${BOTS[@]}"; do
            local status=$(get_status "$bot")
            local pid=""
            if is_running "$bot"; then
                pid=$(cat "$PID_DIR/${bot}.pid")
                pid=" (PID: $pid)"
            fi
            echo -e "  $bot: $status$pid"
        done
        echo "----------------------------------------"
    fi
}

# 查看日志
show_logs() {
    local bot_id=$1
    local lines=${2:-100}
    local log_file="$BOT_ROOT/$bot_id/logs/bot.log"
    
    if [ ! -f "$log_file" ]; then
        echo -e "${RED}日志文件不存在: $log_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}=== $bot_id 最近 $lines 行日志 ===${NC}"
    tail -n "$lines" "$log_file"
}

# 启动所有 bot
start_all() {
    echo -e "${BLUE}启动所有 bot...${NC}"
    for bot in "${BOTS[@]}"; do
        start_bot "$bot"
        sleep 1
    done
    echo -e "${GREEN}所有 bot 启动完成${NC}"
    show_status
}

# 停止所有 bot
stop_all() {
    echo -e "${BLUE}停止所有 bot...${NC}"
    for bot in "${BOTS[@]}"; do
        stop_bot "$bot"
    done
    echo -e "${GREEN}所有 bot 已停止${NC}"
}

# 重启所有 bot
restart_all() {
    stop_all
    sleep 2
    start_all
}

# 主入口
case "$1" in
    start)
        if [ -z "$2" ]; then
            echo "错误: 请指定 bot_id"
            print_help
            exit 1
        fi
        start_bot "$2"
        ;;
    stop)
        if [ -z "$2" ]; then
            echo "错误: 请指定 bot_id"
            print_help
            exit 1
        fi
        stop_bot "$2"
        ;;
    restart)
        if [ -z "$2" ]; then
            echo "错误: 请指定 bot_id"
            print_help
            exit 1
        fi
        restart_bot "$2"
        ;;
    status)
        show_status "$2"
        ;;
    logs)
        if [ -z "$2" ]; then
            echo "错误: 请指定 bot_id"
            print_help
            exit 1
        fi
        show_logs "$2" "$3"
        ;;
    start-all)
        start_all
        ;;
    stop-all)
        stop_all
        ;;
    restart-all)
        restart_all
        ;;
    help|--help|-h)
        print_help
        ;;
    *)
        print_help
        exit 1
        ;;
esac
