"""
羲和AI代理系统 - 主程序入口
全自动Android设备控制平台
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

from core.ai_agent import AIAgent
from utils.config_manager import ConfigManager
from utils.logger import setup_logger


async def main():
    """主程序入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="羲和AI代理系统 - 全自动Android设备控制")
    parser.add_argument("--config", "-c", default="config/xihe_config.json", 
                       help="配置文件路径")
    parser.add_argument("--command", help="要执行的命令")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="交互模式")
    parser.add_argument("--daemon", "-d", action="store_true", 
                       help="守护进程模式")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logger("XiheMain", args.log_level)
    logger.info("启动羲和AI代理系统")
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager(args.config)
        
        # 验证配置
        config_errors = config_manager.validate_config()
        if config_errors:
            logger.warning("配置验证发现问题:")
            for error in config_errors:
                logger.warning(f"  - {error}")
        
        # 初始化AI代理
        ai_agent = AIAgent(args.config)
        
        # 启动AI代理
        await ai_agent.start()
        
        if args.command:
            # 执行单个命令
            logger.info(f"执行命令: {args.command}")
            result = await ai_agent.process_command(args.command)
            
            if result["success"]:
                logger.info("命令执行成功")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                logger.error(f"命令执行失败: {result.get('error')}")
                sys.exit(1)
        
        elif args.interactive:
            # 交互模式
            await interactive_mode(ai_agent)
        
        elif args.daemon:
            # 守护进程模式
            await daemon_mode(ai_agent)
        
        else:
            # 默认模式 - 显示帮助
            print_help()
    
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在退出...")
    except Exception as e:
        logger.error(f"程序异常: {e}")
        sys.exit(1)
    finally:
        # 清理资源
        if 'ai_agent' in locals():
            await ai_agent.stop()
        logger.info("羲和AI代理系统已退出")


async def interactive_mode(ai_agent: AIAgent):
    """交互模式"""
    logger = logging.getLogger("XiheMain")
    logger.info("进入交互模式")
    
    print("=" * 60)
    print("羲和AI代理系统 - 交互模式")
    print("输入命令来控制Android设备，输入 'help' 查看帮助，输入 'quit' 退出")
    print("=" * 60)
    
    while True:
        try:
            command = input("\n羲和> ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['quit', 'exit', 'q']:
                break
            
            if command.lower() == 'help':
                print_help()
                continue
            
            if command.lower() == 'status':
                print_status(ai_agent)
                continue
            
            # 执行命令
            print(f"执行命令: {command}")
            result = await ai_agent.process_command(command)
            
            if result["success"]:
                print("✓ 命令执行成功")
                if result.get("result"):
                    print(f"结果: {result['result']}")
            else:
                print(f"✗ 命令执行失败: {result.get('error')}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"交互模式异常: {e}")
            print(f"错误: {e}")


async def daemon_mode(ai_agent: AIAgent):
    """守护进程模式"""
    logger = logging.getLogger("XiheMain")
    logger.info("进入守护进程模式")
    
    try:
        # 保持运行
        while True:
            await asyncio.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("守护进程模式退出")


def print_help():
    """打印帮助信息"""
    help_text = """
羲和AI代理系统 - 命令帮助

基本命令:
  help                    - 显示此帮助信息
  status                  - 显示系统状态
  quit/exit/q            - 退出程序

Android控制命令:
  点击(100,200)          - 点击屏幕坐标
  滑动(100,200,300,400)  - 滑动屏幕
  输入:文本内容          - 输入文本
  返回                   - 按返回键
  主页                   - 按主页键
  最近任务               - 打开最近任务

应用控制命令:
  启动应用:微信          - 启动指定应用
  关闭应用:微信          - 关闭指定应用
  当前应用               - 查看当前前台应用

视频刷取命令:
  刷抖音视频             - 自动刷抖音视频
  刷快手视频             - 自动刷快手视频
  刷B站视频              - 自动刷B站视频

消息发送命令:
  发微信消息:联系人:内容  - 发送微信消息
  发QQ消息:联系人:内容   - 发送QQ消息
  发短信:手机号:内容     - 发送短信

网页抓取命令:
  抓取网页:URL           - 抓取网页内容
  查询信息:关键词        - 搜索信息

任务调度命令:
  添加任务:任务名:配置   - 添加定时任务
  查看任务               - 查看所有任务
  启用任务:任务ID        - 启用任务
  禁用任务:任务ID        - 禁用任务
  触发任务:任务ID        - 立即执行任务

示例:
  点击(500,800)
  启动应用:抖音
  刷抖音视频
  发微信消息:张三:你好
  抓取网页:https://www.example.com
"""
    print(help_text)


def print_status(ai_agent: AIAgent):
    """打印系统状态"""
    print("\n" + "=" * 40)
    print("羲和AI代理系统状态")
    print("=" * 40)
    print(f"Android控制器: {'已连接' if ai_agent.android_controller else '未连接'}")
    print(f"任务调度器: {'运行中' if ai_agent.task_scheduler.is_running else '已停止'}")
    print(f"运行中任务: {len(ai_agent.running_tasks)}")
    print(f"任务历史: {len(ai_agent.task_history)}")
    print("=" * 40)


if __name__ == "__main__":
    # 确保在正确的目录运行
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 运行主程序
    asyncio.run(main())