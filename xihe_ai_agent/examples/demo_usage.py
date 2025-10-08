#!/usr/bin/env python3
"""
羲和AI代理系统 - 使用示例
展示如何使用羲和系统执行各种自动化任务
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.ai_agent import AIAgent, Task, TaskType
from modules.task_scheduler import ScheduleType
from modules.messaging import Contact, MessagePlatform


async def demo_basic_commands():
    """演示基本命令使用"""
    print("=" * 60)
    print("羲和AI代理系统 - 基本命令演示")
    print("=" * 60)
    
    # 初始化AI代理
    ai_agent = AIAgent("config/xihe_config.json")
    await ai_agent.start()
    
    try:
        # 演示各种命令
        commands = [
            "点击(500,800)",
            "启动应用:微信",
            "输入:你好世界",
            "返回",
            "刷抖音视频",
            "发微信消息:张三:你好，这是自动发送的消息",
            "抓取网页:https://www.example.com",
            "查询信息:Python编程"
        ]
        
        for command in commands:
            print(f"\n执行命令: {command}")
            result = await ai_agent.process_command(command)
            
            if result["success"]:
                print(f"✓ 成功: {result.get('result', '命令执行完成')}")
            else:
                print(f"✗ 失败: {result.get('error', '未知错误')}")
            
            # 等待一下，避免操作过快
            await asyncio.sleep(2)
    
    finally:
        await ai_agent.stop()


async def demo_task_scheduling():
    """演示任务调度功能"""
    print("=" * 60)
    print("羲和AI代理系统 - 任务调度演示")
    print("=" * 60)
    
    ai_agent = AIAgent("config/xihe_config.json")
    await ai_agent.start()
    
    try:
        # 创建定时任务
        print("创建定时任务...")
        
        # 每小时刷抖音视频的任务
        video_task = Task(
            id="video_task_1",
            type=TaskType.VIDEO_WATCHING,
            description="每小时刷抖音视频",
            parameters={"platform": "douyin", "duration": 300}
        )
        
        task_id = await ai_agent.task_scheduler.add_task(
            task=video_task,
            schedule_type=ScheduleType.INTERVAL,
            schedule_config={"interval_seconds": 3600}  # 每小时
        )
        
        print(f"✓ 创建任务成功，ID: {task_id}")
        
        # 创建Cron任务 - 每天上午9点发送消息
        message_task = Task(
            id="message_task_1",
            type=TaskType.MESSAGING,
            description="每天上午9点发送问候消息",
            parameters={
                "platform": "wechat",
                "recipient": "张三",
                "content": "早上好！新的一天开始了！"
            }
        )
        
        cron_task_id = await ai_agent.task_scheduler.add_task(
            task=message_task,
            schedule_type=ScheduleType.CRON,
            schedule_config={"cron": "0 9 * * *"}  # 每天9点
        )
        
        print(f"✓ 创建Cron任务成功，ID: {cron_task_id}")
        
        # 查看所有任务
        print("\n查看所有任务:")
        tasks = ai_agent.task_scheduler.get_all_tasks()
        for task in tasks:
            print(f"  - {task['name']} ({task['status']})")
        
        # 立即触发一个任务
        print("\n立即触发视频任务...")
        success = await ai_agent.task_scheduler.trigger_task(task_id)
        if success:
            print("✓ 任务触发成功")
        else:
            print("✗ 任务触发失败")
    
    finally:
        await ai_agent.stop()


async def demo_messaging_automation():
    """演示消息自动化功能"""
    print("=" * 60)
    print("羲和AI代理系统 - 消息自动化演示")
    print("=" * 60)
    
    ai_agent = AIAgent("config/xihe_config.json")
    await ai_agent.start()
    
    try:
        # 创建联系人列表
        contacts = [
            Contact("张三", MessagePlatform.WECHAT, "zhangsan"),
            Contact("李四", MessagePlatform.WECHAT, "lisi"),
            Contact("王五", MessagePlatform.QQ, "wangwu123")
        ]
        
        # 批量发送消息
        print("批量发送消息...")
        result = await ai_agent.messaging.send_bulk_messages(
            platform="wechat",
            contacts=contacts,
            content="大家好！这是羲和AI代理系统自动发送的消息。",
            delay_range=(5, 10)  # 每条消息间隔5-10秒
        )
        
        if result["success"]:
            print(f"✓ 批量发送完成，成功: {result['success_count']}/{result['total_contacts']}")
        else:
            print(f"✗ 批量发送失败: {result['error']}")
        
        # 发送模板消息
        print("\n发送模板消息...")
        template_result = await ai_agent.messaging.send_template_message(
            template_name="问候",
            platform="wechat",
            contacts=contacts[:1],  # 只给第一个联系人发送
            variables={"name": "张三"}
        )
        
        if template_result["success"]:
            print("✓ 模板消息发送成功")
        else:
            print(f"✗ 模板消息发送失败: {template_result['error']}")
    
    finally:
        await ai_agent.stop()


async def demo_web_scraping():
    """演示网页抓取功能"""
    print("=" * 60)
    print("羲和AI代理系统 - 网页抓取演示")
    print("=" * 60)
    
    ai_agent = AIAgent("config/xihe_config.json")
    await ai_agent.start()
    
    try:
        # 抓取单个网页
        print("抓取单个网页...")
        result = await ai_agent.web_automation.scrape_website(
            url="https://www.example.com",
            data_type="text",
            selectors={
                "title": "h1",
                "content": "p"
            },
            take_screenshot=True
        )
        
        if result["success"]:
            print("✓ 网页抓取成功")
            print(f"数据: {json.dumps(result['result'], indent=2, ensure_ascii=False)}")
        else:
            print(f"✗ 网页抓取失败: {result['error']}")
        
        # 批量抓取
        print("\n批量抓取多个网页...")
        urls = [
            "https://www.example.com",
            "https://httpbin.org/html",
            "https://httpbin.org/json"
        ]
        
        batch_result = await ai_agent.web_automation.batch_scraping(
            urls=urls,
            data_type="text",
            selectors={"title": "h1"},
            concurrent_limit=2
        )
        
        if batch_result["success"]:
            print(f"✓ 批量抓取完成，成功: {batch_result['successful']}/{batch_result['total_urls']}")
        else:
            print(f"✗ 批量抓取失败: {batch_result['error']}")
        
        # 查询信息
        print("\n查询信息...")
        query_result = await ai_agent.web_automation.query_data(
            query="Python编程教程",
            source="web"
        )
        
        if query_result["success"]:
            print("✓ 信息查询成功")
        else:
            print(f"✗ 信息查询失败: {query_result['error']}")
    
    finally:
        await ai_agent.stop()


async def demo_ui_automation():
    """演示UI自动化功能"""
    print("=" * 60)
    print("羲和AI代理系统 - UI自动化演示")
    print("=" * 60)
    
    ai_agent = AIAgent("config/xihe_config.json")
    await ai_agent.start()
    
    try:
        # 自动刷视频
        print("自动刷抖音视频...")
        video_result = await ai_agent.ui_automation.watch_videos(
            platform="douyin",
            duration=60  # 刷1分钟
        )
        
        if video_result["success"]:
            print(f"✓ 刷视频完成，观看了 {video_result['videos_watched']} 个视频")
        else:
            print(f"✗ 刷视频失败: {video_result['error']}")
        
        # 自动点赞
        print("\n自动点赞...")
        like_result = await ai_agent.ui_automation.auto_like_posts(
            app_name="抖音",
            count=5
        )
        
        if like_result["success"]:
            print(f"✓ 自动点赞完成，点赞了 {like_result['liked_count']} 个帖子")
        else:
            print(f"✗ 自动点赞失败: {like_result['error']}")
        
        # 自动关注
        print("\n自动关注用户...")
        follow_result = await ai_agent.ui_automation.auto_follow_users(
            app_name="抖音",
            count=3
        )
        
        if follow_result["success"]:
            print(f"✓ 自动关注完成，关注了 {follow_result['followed_count']} 个用户")
        else:
            print(f"✗ 自动关注失败: {follow_result['error']}")
    
    finally:
        await ai_agent.stop()


async def main():
    """主演示函数"""
    print("羲和AI代理系统 - 完整功能演示")
    print("注意: 此演示需要Android设备连接和正确的配置")
    print()
    
    # 检查配置
    config_file = Path("config/xihe_config.json")
    if not config_file.exists():
        print("错误: 配置文件不存在，请先运行安装脚本")
        return
    
    # 运行各种演示
    demos = [
        ("基本命令", demo_basic_commands),
        ("任务调度", demo_task_scheduling),
        ("消息自动化", demo_messaging_automation),
        ("网页抓取", demo_web_scraping),
        ("UI自动化", demo_ui_automation)
    ]
    
    for name, demo_func in demos:
        try:
            print(f"\n开始演示: {name}")
            await demo_func()
            print(f"✓ {name} 演示完成")
        except Exception as e:
            print(f"✗ {name} 演示失败: {e}")
        
        # 演示间暂停
        await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("所有演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())