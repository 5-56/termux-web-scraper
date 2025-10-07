#!/usr/bin/env python3
"""
羲和AI代理系统 - Web界面启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_socketio
        import cv2
        import pytesseract
        import PIL
        import numpy
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, cwd=Path(__file__).parent)
        print("✓ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖安装失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("    羲和AI代理系统 - Web界面启动器")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        print("\n正在安装依赖...")
        if not install_dependencies():
            print("依赖安装失败，请手动安装")
            return
        print("依赖安装完成，重新检查...")
        if not check_dependencies():
            print("依赖检查仍然失败，请检查Python环境")
            return
    
    # 启动Web服务器
    print("\n启动Web服务器...")
    try:
        from app import XiheWebServer
        
        server = XiheWebServer()
        print("✓ Web服务器启动成功")
        print("访问地址: http://localhost:5000")
        print("按 Ctrl+C 停止服务器")
        
        server.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()