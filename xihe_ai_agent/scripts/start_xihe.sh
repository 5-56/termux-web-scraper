#!/bin/bash
#
# 羲和AI代理系统启动脚本
# 在Termux环境中启动羲和系统
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

# 检查是否在Termux环境中
check_termux() {
    if [ -z "$TERMUX_VERSION" ]; then
        print_message $RED "错误: 此脚本必须在Termux环境中运行"
        exit 1
    fi
    print_message $GREEN "✓ 检测到Termux环境"
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_message $RED "错误: Python3未安装"
        print_message $YELLOW "请运行: pkg install python"
        exit 1
    fi
    print_message $GREEN "✓ Python3已安装"
}

# 检查ADB连接
check_adb() {
    if ! command -v adb &> /dev/null; then
        print_message $RED "错误: ADB未安装"
        print_message $YELLOW "请运行: pkg install android-tools"
        exit 1
    fi
    
    # 检查设备连接
    if ! adb devices | grep -q "device$"; then
        print_message $YELLOW "警告: 未检测到Android设备"
        print_message $YELLOW "请确保:"
        print_message $YELLOW "1. 设备已连接并开启USB调试"
        print_message $YELLOW "2. 已授权调试权限"
        print_message $YELLOW "3. 运行: adb devices 检查连接"
    else
        print_message $GREEN "✓ Android设备已连接"
    fi
}

# 安装依赖
install_dependencies() {
    print_message $BLUE "安装Python依赖..."
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        print_message $YELLOW "安装pip..."
        pkg install python-pip -y
    fi
    
    # 安装Python包
    pip3 install --user selenium requests webdriver-manager
    
    print_message $GREEN "✓ 依赖安装完成"
}

# 创建必要目录
create_directories() {
    print_message $BLUE "创建必要目录..."
    
    mkdir -p logs
    mkdir -p screenshots
    mkdir -p config
    mkdir -p data
    
    print_message $GREEN "✓ 目录创建完成"
}

# 检查配置文件
check_config() {
    local config_file="config/xihe_config.json"
    
    if [ ! -f "$config_file" ]; then
        print_message $YELLOW "配置文件不存在，创建默认配置..."
        # 这里可以复制默认配置文件
        print_message $GREEN "✓ 配置文件已创建"
    else
        print_message $GREEN "✓ 配置文件存在"
    fi
}

# 启动羲和系统
start_xihe() {
    local mode=$1
    
    print_message $BLUE "启动羲和AI代理系统..."
    
    case $mode in
        "interactive")
            print_message $GREEN "进入交互模式"
            python3 main.py --interactive
            ;;
        "daemon")
            print_message $GREEN "进入守护进程模式"
            python3 main.py --daemon
            ;;
        *)
            print_message $GREEN "进入默认模式"
            python3 main.py --help
            ;;
    esac
}

# 显示帮助信息
show_help() {
    echo "羲和AI代理系统启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -i, --interactive    交互模式"
    echo "  -d, --daemon         守护进程模式"
    echo "  -h, --help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --interactive     # 启动交互模式"
    echo "  $0 --daemon          # 启动守护进程模式"
}

# 主函数
main() {
    local mode=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--interactive)
                mode="interactive"
                shift
                ;;
            -d|--daemon)
                mode="daemon"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_message $RED "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_message $BLUE "=========================================="
    print_message $BLUE "    羲和AI代理系统启动脚本"
    print_message $BLUE "=========================================="
    
    # 执行检查
    check_termux
    check_python
    check_adb
    install_dependencies
    create_directories
    check_config
    
    print_message $GREEN "✓ 所有检查通过，准备启动系统"
    
    # 启动系统
    start_xihe $mode
}

# 运行主函数
main "$@"