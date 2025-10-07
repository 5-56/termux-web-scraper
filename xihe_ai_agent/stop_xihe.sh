#!/bin/bash
#
# 羲和AI代理系统 - 停止脚本
#

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_message $BLUE "正在停止羲和AI代理系统..."

# 停止Web服务器
if [ -f "web_server.pid" ]; then
    WEB_PID=$(cat web_server.pid)
    if ps -p $WEB_PID > /dev/null; then
        kill $WEB_PID
        print_message $GREEN "✓ Web服务器已停止 (PID: $WEB_PID)"
    else
        print_message $YELLOW "Web服务器未运行"
    fi
    rm -f web_server.pid
else
    print_message $YELLOW "未找到Web服务器PID文件"
fi

# 停止AI代理
if [ -f "ai_agent.pid" ]; then
    AI_PID=$(cat ai_agent.pid)
    if ps -p $AI_PID > /dev/null; then
        kill $AI_PID
        print_message $GREEN "✓ AI代理已停止 (PID: $AI_PID)"
    else
        print_message $YELLOW "AI代理未运行"
    fi
    rm -f ai_agent.pid
else
    print_message $YELLOW "未找到AI代理PID文件"
fi

# 清理其他相关进程
print_message $BLUE "清理相关进程..."

# 查找并停止相关Python进程
PYTHON_PIDS=$(ps aux | grep -E "(main\.py|run_web\.py|xihe)" | grep -v grep | awk '{print $2}')
if [ ! -z "$PYTHON_PIDS" ]; then
    echo $PYTHON_PIDS | xargs kill 2>/dev/null || true
    print_message $GREEN "✓ 相关Python进程已清理"
fi

print_message $GREEN "羲和AI代理系统已完全停止"