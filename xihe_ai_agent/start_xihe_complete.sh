#!/bin/bash
#
# 羲和AI代理系统 - 完整启动脚本
# 启动Web界面和所有服务
#

# 设置脚本错误时退出
set -e

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

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_message $RED "错误: Python3未安装"
        exit 1
    fi
    print_message $GREEN "✓ Python3已安装"
}

# 检查依赖
check_dependencies() {
    print_message $BLUE "检查Python依赖..."
    
    # 检查核心依赖
    python3 -c "import flask, flask_socketio, cv2, pytesseract, PIL, numpy" 2>/dev/null || {
        print_message $YELLOW "正在安装Web界面依赖..."
        pip3 install -r web_server/requirements.txt
    }
    
    print_message $GREEN "✓ 所有依赖已安装"
}

# 创建必要目录
create_directories() {
    print_message $BLUE "创建必要目录..."
    
    mkdir -p logs
    mkdir -p screenshots
    mkdir -p scripts
    mkdir -p data
    mkdir -p config
    
    print_message $GREEN "✓ 目录创建完成"
}

# 检查配置文件
check_config() {
    local config_file="config/xihe_config.json"
    
    if [ ! -f "$config_file" ]; then
        print_message $YELLOW "配置文件不存在，创建默认配置..."
        cp web_server/templates/config_template.json "$config_file" 2>/dev/null || {
            print_message $YELLOW "使用内置默认配置"
        }
    fi
    
    print_message $GREEN "✓ 配置文件检查完成"
}

# 启动Web服务器
start_web_server() {
    print_message $BLUE "启动Web服务器..."
    
    cd web_server
    python3 run_web.py &
    WEB_PID=$!
    
    # 等待服务器启动
    sleep 3
    
    if ps -p $WEB_PID > /dev/null; then
        print_message $GREEN "✓ Web服务器启动成功 (PID: $WEB_PID)"
        echo $WEB_PID > ../web_server.pid
    else
        print_message $RED "✗ Web服务器启动失败"
        exit 1
    fi
    
    cd ..
}

# 启动AI代理
start_ai_agent() {
    print_message $BLUE "启动AI代理..."
    
    python3 main.py --daemon &
    AI_PID=$!
    
    # 等待AI代理启动
    sleep 2
    
    if ps -p $AI_PID > /dev/null; then
        print_message $GREEN "✓ AI代理启动成功 (PID: $AI_PID)"
        echo $AI_PID > ai_agent.pid
    else
        print_message $RED "✗ AI代理启动失败"
        exit 1
    fi
}

# 显示访问信息
show_access_info() {
    print_message $GREEN "=" * 60
    print_message $GREEN "    羲和AI代理系统启动完成！"
    print_message $GREEN "=" * 60
    print_message $BLUE "Web界面访问地址:"
    print_message $YELLOW "  http://localhost:5000"
    print_message $YELLOW "  http://127.0.0.1:5000"
    print_message $BLUE ""
    print_message $BLUE "功能模块:"
    print_message $YELLOW "  - AI对话界面: /ai-chat"
    print_message $YELLOW "  - 代码编辑器: /code-editor"
    print_message $YELLOW "  - 屏幕识别: /screen-recognition"
    print_message $YELLOW "  - 系统仪表板: /dashboard"
    print_message $BLUE ""
    print_message $BLUE "停止服务:"
    print_message $YELLOW "  ./stop_xihe.sh"
    print_message $YELLOW "  或按 Ctrl+C"
    print_message $GREEN "=" * 60
}

# 清理函数
cleanup() {
    print_message $YELLOW "\n正在停止服务..."
    
    # 停止Web服务器
    if [ -f "web_server.pid" ]; then
        WEB_PID=$(cat web_server.pid)
        if ps -p $WEB_PID > /dev/null; then
            kill $WEB_PID
            print_message $GREEN "✓ Web服务器已停止"
        fi
        rm -f web_server.pid
    fi
    
    # 停止AI代理
    if [ -f "ai_agent.pid" ]; then
        AI_PID=$(cat ai_agent.pid)
        if ps -p $AI_PID > /dev/null; then
            kill $AI_PID
            print_message $GREEN "✓ AI代理已停止"
        fi
        rm -f ai_agent.pid
    fi
    
    print_message $GREEN "所有服务已停止"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    print_message $BLUE "=" * 60
    print_message $BLUE "    羲和AI代理系统 - 完整启动脚本"
    print_message $BLUE "=" * 60
    
    # 执行检查
    check_python
    check_dependencies
    create_directories
    check_config
    
    # 启动服务
    start_web_server
    start_ai_agent
    
    # 显示访问信息
    show_access_info
    
    # 保持运行
    print_message $BLUE "\n系统正在运行中... (按 Ctrl+C 停止)"
    
    # 等待用户中断
    while true; do
        sleep 1
    done
}

# 运行主函数
main "$@"